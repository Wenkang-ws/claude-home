# DTO & @Expose() Rules — payroll-backend

## CRITICAL: Response DTO @Expose() Requirement

**Every property** on a response DTO **MUST** have `@Expose()`. We **always** use `excludeExtraneousValues: true` with `plainToInstance()`. Properties missing `@Expose()` are **silently stripped** from the response.

```typescript
// In controller — ALWAYS:
return plainToInstance(YourResponseDto, result, {
  excludeExtraneousValues: true,
});
```

## Response DTO Rules

- `@Expose()` on **every** field
- `@ApiProperty()` with `description`, `type`, and `nullable: true` where applicable
- `@Type(() => NestedDto)` for nested objects and arrays
- Money/amounts as `string` type (never `number`)
- Dates as `Date` type in responses

```typescript
// Nested objects require both @Type and @Expose
@Type(() => NestedDto)
@Expose()
nested: NestedDto | null;

// Arrays of nested objects
@Type(() => ItemDto)
@Expose()
items: ItemDto[];

// Money — always string
@ApiProperty({ type: String, example: '100.00' })
@Expose()
amount: string;
```

## Request DTO Rules

- `@ApiProperty()` for required fields, `@ApiPropertyOptional()` for optional
- Appropriate validation decorators (`@IsString()`, `@IsUUID()`, `@IsEnum()`, etc.)
- `@Transform()` for type coercion:
  - Booleans from query strings: `@Transform(({ value }) => value === 'true' || value === true)`
  - Array params: `@Transform(({ value }) => (Array.isArray(value) ? value : [value]))`

## Query DTO Rules

- Extend `PaginationDto` from `@ws/ws-nestjs-common`
- Define sort fields as a local enum
- Default sort: `createdAt` descending

## DTO File Naming

| Type     | Pattern                            | Example                            |
| -------- | ---------------------------------- | ---------------------------------- |
| Request  | `<action>-<entity>-request.dto.ts` | `create-payroll-request.dto.ts`    |
| Response | `<entity>-response.dto.ts`         | `payroll-response.dto.ts`          |
| Query    | `<action>-<entity>-query.dto.ts`   | `list-payrolls-query.dto.ts`       |
| Internal | `internal-<entity>-<type>.dto.ts`  | `internal-payroll-response.dto.ts` |
| V2       | `<entity>-v2-<type>.dto.ts`        | `payroll-v2-response.dto.ts`       |

## Update/Patch DTOs

All fields optional with `@ApiPropertyOptional()`, `@IsOptional()`, and validators.

## Anti-Patterns

- Missing `@Expose()` on response properties — fields silently disappear
- `number` for monetary amounts — use `string`
- Missing `@Type()` on nested objects — nested data won't transform
- Mixing request and response DTOs — keep them separate
- `any` type in DTOs — always use proper types
