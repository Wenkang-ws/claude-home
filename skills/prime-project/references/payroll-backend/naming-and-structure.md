# Naming & Structure Conventions — payroll-backend

## Module Directory Layout

```
src/app/<module>/
├── <module>.module.ts
├── controllers/
│   ├── <entity>.controller.ts          # Public V1
│   ├── <entity>-v2.controller.ts       # Public V2
│   ├── internal-<entity>.controller.ts # Internal V1
│   └── internal-<entity>-v2.controller.ts
├── services/
│   ├── <entity>.service.ts
│   ├── <entity>-v2.service.ts
│   └── <entity>-<purpose>.service.ts   # e.g. payroll-notification.service.ts
├── repositories/
│   └── <entity>.repository.ts
├── listeners/
│   └── <entity>.listener.ts
├── jobs/
│   └── <purpose>.job.ts
├── dto/
│   ├── <action>-<entity>-request.dto.ts
│   ├── <entity>-response.dto.ts
│   ├── <action>-<entity>-query.dto.ts
│   ├── internal-<entity>-<type>.dto.ts
│   └── <entity>-v2-<type>.dto.ts
├── models/
│   └── <entity>.model.ts
├── interfaces/
│   └── <entity>.interface.ts
└── tests/
    ├── unit/
    │   └── <file-being-tested>.spec.ts
    └── integration/
        └── <file-being-tested>.integration.spec.ts
```

## Import Ordering

Group imports in this order, with a blank line between groups:

1. NestJS core (`@nestjs/common`, `@nestjs/swagger`, etc.)
2. NestJS feature modules (`@nestjs/bullmq`, `@nestjs/config`, etc.)
3. Third-party libraries (`class-transformer`, `nock`, `@sentry/*`, etc.)
4. Workspace libraries (`@ws/*`)
5. Other module imports (relative `../../`)
6. Local imports (same module `../`)

## Enum Naming Convention

- **Enum names**: PascalCase — `PaymentMethodPreference`
- **Enum members**: PascalCase — `DirectDeposit`
- **Enum values (strings)**: lowercase snake_case — `'direct_deposit'`

```typescript
// CORRECT
export enum PaymentMethodPreference {
  Manual = 'manual',
  DirectDeposit = 'direct_deposit',
}

// WRONG — no SCREAMING_SNAKE for members, no PascalCase/SCREAMING for values
```

## LLM Comment Cleanup

At the end of every task, remove:

- Implementation guidance comments (`// TODO: implement`, `// Add logic here`)
- Explanatory comments added during generation
- Placeholder comments

Preserve:

- JSDoc `@param` / `@returns` annotations
- Existing user-written comments (ASK before removing)
- Necessary business logic explanations

## Shell Command Rules

- **Before running version-sensitive commands** (tests, builds): ASK the user which environment manager they use (mise, nvm, fnm, asdf)
- **Before running mutation commands** (install packages, modify git config, etc.): ASK for confirmation
- Read-only commands (`git status`, `ls`, type-checking) are fine without asking

## Module Registration

After creating a new module, register it in `app.module.ts` (add alphabetically).

## Resource Path Constants

Use constants from the `Resources` enum for path segments:

```typescript
@Get(`${Resources.Payrolls}/:payrollId`)
@Get(`${Resources.Companies}/:companyId/${Resources.Payrolls}`)
```

## Type Safety

**NEVER use `any`** — use proper interfaces, `Partial<T>`, `Pick<T, K>`, or `unknown` with type guards.
