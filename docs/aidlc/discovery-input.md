# AI-DLC Discovery Input

## Project

Rebuild or Reuse Advisor

## Problem

Generative AI has lowered the cost of creating software, which also increases the risk of rebuilding something that already exists.

Before implementation begins, users need help answering:

> Should this task reuse an existing asset, extend something that already exists, or be developed from scratch?

The service should gather task context, discover similar assets, compare fit and gaps, and return a decision with evidence.

## Target users

The service should support multiple roles, including developers and non-developers who create software or internal tools with AI-assisted development.

## Primary decision output

- REUSE
- EXTEND EXISTING
- DEVELOP
- NEEDS REVIEW

## Primary Use Case — Developer

A developer working on an existing project needs to add or improve functionality.

### Happy Path

1. Requirement or improvement need occurs.
2. User explains the task, problem, and desired outcome.
3. System collects relevant task context.
4. System searches for similar existing assets.
5. System compares task requirements with discovered assets.
6. System identifies reusable coverage and gaps.
7. System produces one of four decisions: REUSE, EXTEND EXISTING, DEVELOP, NEEDS REVIEW.
8. System explains the evidence behind the decision.
9. The result becomes input to the subsequent AI-DLC implementation flow.

## Information to collect

- User role
- Task title
- Problem statement
- Desired outcome
- Existing project / system context
- Current workflow
- Related systems or assets already known by the user
- Functional requirements
- Constraints
- Security / compliance considerations
- Expected users
- Expected usage frequency or scale
- Time / implementation constraints

## Asset evidence

For each potentially reusable asset, capture:

- Asset name
- Asset type
- Description
- Source
- Similarity to task
- Requirements covered
- Missing requirements
- Integration effort
- Constraints / risks
- Evidence links or references

## Decision guidance

### REUSE

Use when an existing asset already satisfies most core requirements and can be adopted with little or no meaningful modification.

### EXTEND EXISTING

Use when an existing asset is a strong fit but meaningful gaps should be implemented on top of it.

### DEVELOP

Use when discovered assets do not sufficiently cover the core need, or adapting them would cost more than a focused new implementation.

### NEEDS REVIEW

Use when evidence is insufficient, conflicting, or the trade-off cannot be decided confidently without human judgment.

## MVP scope

The hackathon MVP should prove the decision workflow rather than attempt full enterprise search integration.

Minimum flow:

Task input
→ context structuring
→ candidate asset retrieval
→ comparison
→ decision
→ evidence-backed explanation

Enterprise data sources can initially be represented with prepared sample data or adapters, while keeping interfaces suitable for later integration.

## AI-DLC goal

Use this discovery input to derive:

1. Functional requirements
2. Non-functional requirements
3. MVP scope
4. Architecture
5. Data model
6. API / UI interaction flow
7. Test scenarios
8. Evidence and review gates

Prioritize a small, demonstrable Happy Path that can be completed during the hackathon.
