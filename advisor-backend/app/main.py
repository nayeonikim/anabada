"""FastAPI 앱 — 3개 라우트 + DI 조립 + 예외 핸들러 (§1.6/§3.2).

- DI: config → infra(repository/registry/llm/feedbackStore) → components → S1 orchestrator.
- demoMode ON=FixtureLLMClient / OFF=BedrockClaudeClient (폴백 없음, §1.2).
- 예외 핸들러: AdvisorError → HTTP↔code 매핑, 내부 예외 문자열 미노출.
"""
from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import errors as api_errors
from app.api.schemas import (
    AdviceResponse,
    AdviseRequest,
    ClarificationRequestDTO,
    EvidenceChainDTO,
    EvidenceItemDTO,
    FeedbackRequest,
    FeedbackResponse,
    IntentRequest,
    IntentResponse,
    RankedCandidateDTO,
    StructuredIntentDTO,
)
from app.components.asset_search import AssetSearchComponent
from app.components.candidate_selection import CandidateSelectionComponent
from app.components.evidence_builder import EvidenceBuilderComponent
from app.components.feedback import FeedbackComponent
from app.components.permission_filter import PermissionFilterComponent
from app.components.reverification import ReVerificationComponent
from app.components.structure import IntentStructuringComponent
from app.config import Config
from app.domain.errors import AdvisorError
from app.domain.models import (
    AdviceResult,
    ClarificationRequest,
    ClassificationConfig,
    FeedbackVerdict,
    PermissionContext,
    StructuredIntent,
)
from app.infra.asset_repository import AssetRepository
from app.infra.feedback_store import FeedbackStore
from app.infra.llm_client import BedrockClaudeClient, FixtureLLMClient, LLMClient
from app.logging_setup import audit, configure_logging, get_audit_logger
from app.adapters.registry import SourceAdapterRegistry
from app.services.orchestrator import AdvisorOrchestratorService


# ── DI 조립 ───────────────────────────────────────────────────────
def build_orchestrator(config: Config) -> AdvisorOrchestratorService:
    repository = AssetRepository.load(config.assets_path, config.evidence_path)
    registry = SourceAdapterRegistry.build_mock(repository)
    feedback_store = FeedbackStore(config.feedback_path)
    llm = _build_llm(config)
    classification = ClassificationConfig(
        reuse_threshold=config.reuse_threshold,
        extend_threshold=config.extend_threshold,
        top_n=config.top_n,
    )
    return AdvisorOrchestratorService(
        structuring=IntentStructuringComponent(llm),
        search=AssetSearchComponent(registry, repository),
        permission_filter=PermissionFilterComponent(repository),
        selection=CandidateSelectionComponent(),
        reverification=ReVerificationComponent(llm),
        evidence_builder=EvidenceBuilderComponent(),
        feedback=FeedbackComponent(feedback_store),
        config=classification,
    )


def _build_llm(config: Config) -> LLMClient:
    # demoMode ON=Fixture / OFF=Bedrock (폴백 없음, §1.2)
    if config.demo_mode:
        return FixtureLLMClient.load(config.demo_fixtures_path)
    return BedrockClaudeClient(
        model_id=config.llm_model_id,
        region=config.llm_region,
        timeout_seconds=config.llm_timeout_seconds,
    )


def create_app(config: Config | None = None) -> FastAPI:
    config = config or Config.load()
    configure_logging(config.log_level)
    orchestrator = build_orchestrator(config)

    app = FastAPI(title="Reuse Advisor Backend (U1)", version="1.0.0")
    app.state.orchestrator = orchestrator

    @app.middleware("http")
    async def _request_id(request: Request, call_next):
        request.state.request_id = uuid.uuid4().hex
        return await call_next(request)

    # ── 예외 핸들러: 내부 문자열 미노출(§1.6) ────────────────────
    @app.exception_handler(AdvisorError)
    async def _advisor_error(request: Request, exc: AdvisorError):
        request_id = getattr(request.state, "request_id", "")
        get_audit_logger().warning(
            "advisor_error code=%s requestId=%s detail=%s",
            exc.code.value,
            request_id,
            exc.internal_detail,  # 서버 로그 전용
        )
        return JSONResponse(
            status_code=api_errors.http_status_for(exc),
            content=api_errors.to_error_response(exc, request_id).model_dump(),
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "")
        get_audit_logger().error(
            "unexpected_error requestId=%s type=%s",
            request_id,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content=api_errors.generic_error_response(request_id).model_dump(),
        )

    _register_routes(app)
    return app


def _register_routes(app: FastAPI) -> None:
    @app.post("/intent", response_model=IntentResponse)
    async def submit_intent(body: IntentRequest, request: Request) -> IntentResponse:
        request_id = getattr(request.state, "request_id", "")
        result = _orchestrator(request).submit_intent(body.rawText, request_id)
        if isinstance(result, ClarificationRequest):
            return IntentResponse(
                status="clarification",
                clarification=ClarificationRequestDTO(
                    missingFields=result.missing_fields,
                    questions=result.questions,
                ),
            )
        return IntentResponse(status="structured", intent=_intent_dto(result))

    @app.post("/advise", response_model=AdviceResponse)
    async def advise(body: AdviseRequest, request: Request) -> AdviceResponse:
        request_id = getattr(request.state, "request_id", "")
        intent = StructuredIntent(
            role=body.intent.role,
            goal=body.intent.goal,
            function=body.intent.function,
            data=body.intent.data,
            output=body.intent.output,
        )
        ctx = PermissionContext(user_id=body.context.userId, role=body.context.role)
        result = _orchestrator(request).advise(intent, ctx, request_id)
        return _advice_dto(result)

    @app.post("/feedback", response_model=FeedbackResponse)
    async def submit_feedback(
        body: FeedbackRequest, request: Request
    ) -> FeedbackResponse:
        confirmation = _orchestrator(request).submit_feedback(
            body.resultId, body.candidateId, FeedbackVerdict(body.verdict)
        )
        return FeedbackResponse(confirmationId=confirmation)


# ── 라우트 헬퍼 ────────────────────────────────────────────────────
def _orchestrator(request: Request) -> AdvisorOrchestratorService:
    return request.app.state.orchestrator


def _intent_dto(intent: StructuredIntent) -> StructuredIntentDTO:
    return StructuredIntentDTO(
        role=intent.role,
        goal=intent.goal,
        function=intent.function,
        data=intent.data,
        output=intent.output,
    )


def _advice_dto(result: AdviceResult) -> AdviceResponse:
    return AdviceResponse(
        resultId=result.result_id,
        ranking=[
            RankedCandidateDTO(
                candidateId=r.candidate_id,
                sources=[s.value for s in r.sources],
                assetName=r.asset_name,
                lifecycleStatus=r.lifecycle_status.value,
                evaluationStatus=r.evaluation_status.value,
                reusabilityScore=r.reusability_score,
                candidateState=r.candidate_state.value,
                capabilityMatch=r.capability_match,
                rank=r.rank,
            )
            for r in result.ranking
        ],
        overallDecision=result.overall_decision.value,
        overallRationale=result.overall_rationale,
        isRecommendation=result.is_recommendation,
        evidenceChains=[
            EvidenceChainDTO(
                candidateId=c.candidate_id,
                evidenceItems=[
                    EvidenceItemDTO(
                        source=i.source.value,
                        evidenceType=i.evidence_type,
                        title=i.title,
                        sourceRef=i.source_ref,
                    )
                    for i in c.evidence_items
                ],
                stateRationale=c.state_rationale,
            )
            for c in result.evidence_chains
        ],
    )


# 모듈 로드 시 앱 인스턴스(uvicorn app.main:app)
app = create_app()
