# Controller Patterns — payroll-backend

## Base Controller Selection

| Controller Type   | Base Class                         | Path Prefix         | Auth                                                 |
| ----------------- | ---------------------------------- | ------------------- | ---------------------------------------------------- |
| Public V1         | `BaseV1Controller`                 | `/v1/`              | Bearer (AuthenticationGuard)                         |
| Public V2         | `BaseV2Controller`                 | `/v2/`              | Bearer (AuthenticationGuard + AuthenticationV2Guard) |
| Internal V1       | `InternalBaseV1Controller`         | `/v1/internal_api/` | API key (ApiKeyGuard)                                |
| Internal V2       | `InternalBaseV2Controller`         | `/v2/internal_api/` | API key (ApiKeyGuard)                                |
| CheckHQ Component | `BaseCheckhqComponentV1Controller` | Varies              | CheckHQ component                                    |

## Swagger/OpenAPI — Mandatory

Every endpoint **MUST** have:

- `@ApiTags()` on the class (use `OpenApiTags` enum)
- `@ApiOperation({ summary: '...' })` on each method
- Response decorator: `@ApiOkResponse`, `@ApiCreatedResponse`, `@ApiNoContentResponse`
- Response `type` specified in the decorator

## DO NOT Add Unnecessary @HttpCode()

NestJS defaults are correct. **Only** override when you need a **different** status code:

| Decorator   | Default Status | Override needed?                         |
| ----------- | -------------- | ---------------------------------------- |
| `@Get()`    | 200            | No                                       |
| `@Post()`   | 201            | Only if returning 200 (action endpoints) |
| `@Patch()`  | 200            | No                                       |
| `@Put()`    | 200            | No                                       |
| `@Delete()` | 200            | Only if returning 204                    |

**Before adding a non-default HttpCode**: ASK the user if the different status code is intended.

## Authorization Pattern

Public controllers: call `this.authorize(context)` at the **start** of every endpoint:

```typescript
private async authorize(context: UserRequestContext) {
  const authCtx = await this.authorizationService.getAuthorizationContext(
    context, [PayrollPermissions.PayrollOperations]
  );
  if (!authCtx.authorized) throw new ForbiddenException();
  return authCtx;
}
```

Internal controllers: no authorization (API key guard handles it).

## Request Context

- Use `@Context()` decorator to inject `UserRequestContext`
- Always the first parameter in endpoint methods

## Response Transformation

Always use `plainToInstance()` with `excludeExtraneousValues: true`. See `dto-and-expose-rules.md`.

## Pagination

For paginated endpoints, return `PaginatedDto<T>` from `@ws/ws-nestjs-common`. Use `@ApiPaginatedResponse(DtoClass)` decorator.

## Controller File Naming

- `<entity>.controller.ts` — Public V1
- `<entity>-v2.controller.ts` — Public V2
- `internal-<entity>.controller.ts` — Internal V1
- `internal-<entity>-v2.controller.ts` — Internal V2
- One controller per file

## Anti-Patterns

- Adding `@HttpCode()` for default behavior
- Skipping authorization in public endpoints
- Returning raw DB/service objects without DTO transformation
- Mixing V1 and V2 patterns in the same controller
- Forgetting to register controllers in the module
