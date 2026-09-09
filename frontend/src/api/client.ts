// U1 백엔드 3개 API 클라이언트. Vite dev proxy가 /intent·/advise·/feedback를 :8000으로 전달.
import type {
  AdviceResponse,
  AdviseRequest,
  ApiErrorBody,
  FeedbackRequest,
  FeedbackResponse,
  IntentResponse,
} from './types'

/** 백엔드 공개 오류 모델을 담는 예외. 내부 문자열은 서버가 노출하지 않는다. */
export class ApiError extends Error {
  code: string
  status: number
  requestId?: string
  constructor(status: number, code: string, message: string, requestId?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.requestId = requestId
  }
}

async function post<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  let res: Response
  try {
    res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', '백엔드에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.')
  }

  if (!res.ok) {
    let code = 'HTTP_ERROR'
    let message = `요청이 실패했습니다 (HTTP ${res.status}).`
    let requestId: string | undefined
    try {
      const data = (await res.json()) as ApiErrorBody
      if (data?.error) {
        code = data.error.code ?? code
        message = data.error.message ?? message
        requestId = data.error.requestId
      }
    } catch {
      // 오류 본문 파싱 실패 → 기본 메시지 유지
    }
    throw new ApiError(res.status, code, message, requestId)
  }

  return (await res.json()) as TRes
}

export const api = {
  submitIntent(rawText: string): Promise<IntentResponse> {
    return post('/intent', { rawText })
  },
  advise(req: AdviseRequest): Promise<AdviceResponse> {
    return post('/advise', req)
  },
  submitFeedback(req: FeedbackRequest): Promise<FeedbackResponse> {
    return post('/feedback', req)
  },
}
