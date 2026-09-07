# Rebuild or Reuse Advisor

Hackathon project for helping users decide whether to reuse, extend, or newly develop software before starting implementation.

## Core decision

- REUSE
- EXTEND EXISTING
- DEVELOP
- NEEDS REVIEW

## Repository layout

```text
.
├── README.md
├── app/                  # MVP application code
├── docs/
│   ├── use-cases/        # Role/use-case inputs and happy paths
│   ├── aidlc/            # AI-DLC discovery inputs and outputs
│   └── presentation/     # Demo/presentation material
├── scripts/              # Utility scripts
└── tests/                # Tests
```

## Hackathon flow

Task / role / context input
→ discover related existing assets
→ compare reuse vs extension vs new development
→ return a decision with evidence
→ continue into AI-DLC implementation flow
