# Feature Implementation Order — payroll-backend

## Implementation Sequence

Follow this order for every new feature:

### 1. Database / Schema

- Edit `prisma/schema.prisma`
- Run `nx run payroll-backend:prisma-generate`
- Create migration: `nx run payroll-backend:prisma-migrate --create-only --name=<Name>`
  - **Propose** a PascalCase name to the user and **ASK to confirm** (e.g. `AddProcessingPeriodToCompany`)
  - Prisma auto-converts to snake_case folder names
- Review the generated SQL before applying

### 2. Models / Interfaces

- Define TypeScript types in `models/` and `interfaces/`

### 3. Repository

- Add data access methods following naming conventions (see `service-and-repository.md`)
- Handle JSON fields with `Prisma.DbNull`

### 4. Service

- Implement business logic and orchestration
- Wire up external service calls if needed
- Add event emission

### 5. DTOs

- Create request/response/query DTOs (see `dto-and-expose-rules.md`)
- **Every response DTO property MUST have `@Expose()`**

### 6. Controller

- Add API endpoints (see `controller-patterns.md`)
- Select correct base class
- Add Swagger decorators
- Wire up authorization

### 7. Module

- Register all new providers, controllers, exports in module file
- Register module in `app.module.ts` if new

### 8. Tests

- Unit tests for controller + service
- Integration tests for controller endpoints
- (see `testing-conventions.md`)

### 9. OpenAPI

- **Mandatory**: Run `nx run payroll-backend:open-api`
- If it fails, **fix the underlying error** — do NOT skip or manually edit the spec

## Pre-Implementation Checklist

Before starting, confirm:

1. Scope understood — ask clarifying questions
2. Affected modules identified
3. External integrations checked (CheckHQ, HRIS, etc.)
4. Database changes needed?
5. API changes needed?

## Post-Implementation Checklist

- [ ] All tests pass (`nx run payroll-backend:test:unit` + `test:integration`)
- [ ] OpenAPI spec regenerated
- [ ] No linting errors (`nx run payroll-backend:lint`)
- [ ] LLM-generated comments removed
- [ ] No `any` types
- [ ] `@Expose()` on all response DTO properties

## External Services Reference

| Service   | Location                     | Purpose            |
| --------- | ---------------------------- | ------------------ |
| CheckHQ   | `src/app/checkhq/`           | Payroll processing |
| HRIS      | `src/app/hris/`              | Core HR data       |
| Time-Off  | `src/app/time-off-earnings/` | Leave management   |
| OneSchema | `src/app/webhooks/`          | Data import        |
| Hedylogos | `src/app/ai-agent/`          | AI services        |

## Feature Flags

For significant features, consider GrowthBook integration for gradual rollout. Features can be enabled per-company.
