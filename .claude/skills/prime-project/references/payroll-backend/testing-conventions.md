# Testing Conventions — payroll-backend

## Test Locations

- Unit tests: `src/app/<module>/tests/unit/<file>.spec.ts`
- Integration tests: `src/app/<module>/tests/integration/<file>.integration.spec.ts`

## Test Commands — ALWAYS use nx, NEVER pnpm jest

```bash
# Unit tests
nx run payroll-backend:test:unit
nx run payroll-backend:test:unit --testPathPattern=<pattern>
nx run payroll-backend:test:unit --coverage

# Integration tests
nx run payroll-backend:test:integration
nx run payroll-backend:test:integration --testPathPattern=<pattern>
```

**If using a Node version manager**, prefix:

- mise: `mise exec -- nx run ...`
- nvm: `. ~/.nvm/nvm.sh && nvm use && nx run ...`
- fnm: `eval "$(fnm env)" && fnm use && nx run ...`
- asdf: `asdf exec nx run ...`

**ASK the user** which manager they use before running tests.

## Unit Test Patterns

### Mock Creation — `jest.Mocked<T>`

```typescript
let service: jest.Mocked<SomeService>;
service = {
  methodA: jest.fn(),
  methodB: jest.fn(),
} as unknown as jest.Mocked<SomeService>;
```

### Controller Unit Tests

- Instantiate controller directly with mocked dependencies (no `Test.createTestingModule`)
- Mock `AuthorizationService.getAuthorizationContext` with `AuthorizedWithAllCoreLocationsContext` / `UnauthorizedContext`
- Test authorization → ForbiddenException path
- Test happy path → correct DTO transformation

### Service Unit Tests

- Mock Sentry: `jest.mock('@sentry/nestjs')`
- Mock repositories, external services, event emitter
- Test not-found → NotFoundException
- Test create/update/delete flows
- Verify event emission

## Integration Test Patterns

### Setup

- Use `Test.createTestingModule({ imports: [AppModule] })`
- Override guards: `.overrideGuard(AuthenticationV2Guard).useValue({ canActivate: () => true })`
- Override GrowthBook: `.overrideProvider(GrowthbookService).useValue({...})`
- Override Kafka: `.overrideProvider(KafkaService).useValue({ emit: jest.fn() })`
- Override Prisma: `.overrideProvider(PrismaService).useValue(jestPrisma)` (auto-rollback)
- `jest.unmock('axios')` at top of file
- `nock.enableNetConnect('127.0.0.1')` in beforeAll

### Test Data — Prisma Fabbrica Factories

```typescript
import { CompanyFactory } from '../../../../test/factories/company.factory';
const company = await CompanyFactory.create();
const payroll = await PayrollFactory.create({
  company: { connect: { id: company.id } },
  status: 'draft',
});
```

### External Service Mocking — nock

```typescript
nock('https://api.external.com')
  .get('/endpoint')
  .query(true)
  .reply(200, { data: [] });

// Cleanup in afterAll:
nock.cleanAll();
```

### nockBack Fixtures

Integration tests use `nockBack` with recorded JSON fixtures in `tests/integration/api-request-fixtures/`. These record exact HTTP request/response sequences for external APIs (HRIS, CheckHQ, Core API).

**When code changes break nockBack tests:**

1. Add `nock.emitter.on('no match', (req) => console.log('NOCK_NO_MATCH:', req.method, req.hostname, req.path, Buffer.concat(req.requestBodyBuffers || []).toString().substring(0, 300)))` to find the exact mismatch.
2. Only change the exact values that differ in the fixture. Never add or remove recording entries — this shifts slots and cascades failures. Never bulk find-and-replace — different entries with the same value may come from different code paths.
3. Only modify values in `"body"` objects (requests), never in `"response"` objects.
4. Run the FULL integration suite after fixing (`nx run payroll-backend:test:integration`), not just the failing test.

**Common mismatch — `termination_date.gt`:** The HRIS employee search includes `termination_date.gt` as a 30-day lookback. `getPayableEmployeesByCompany` computes this with PT timezone (can produce off-by-one vs UTC). If switching code paths, the fixture date may need a 1-day adjustment.

### Request Headers (supertest)

Always include: `Authorization`, `x-core-company-id`, optionally `x-correlation-id`.

### Database State Verification

After mutations, verify with direct Prisma queries:

```typescript
const created = await prismaService.client.entity.findUnique({ where: { id } });
expect(created).not.toBeNull();
```

## Type Safety

**NEVER use `any`** in tests — use `jest.Mocked<T>` and `unknown`.

## Rules

- Use `it.only()` during development, **remove before committing**
- Test both success AND error paths
- Target 80%+ coverage (90%+ ideal)
- Don't share mutable state between tests — reset in `beforeEach`
- Don't test implementation details — test behavior
