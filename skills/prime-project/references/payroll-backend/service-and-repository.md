# Service & Repository Patterns — payroll-backend

## Service Conventions

### Responsibility Separation

- **Services**: Business logic, orchestration, external service calls, event emission
- **Repositories**: Data access only — no business logic
- **Controllers**: Request validation, auth, response transformation — no business logic

### Dependency Injection Order

Constructor parameters: `PrismaService`, repositories, other services, `EventEmitter2`

### Structured Logging

```typescript
private readonly logger = new Logger(YourService.name);

this.logger.log({
  message: 'Processing entity',
  entityId: id,
  meta: { namespace: 'your-flow' },
});

this.logger.error({
  message: 'Failed to process entity',
  error,
  entityId: id,
});
```

### Error Handling

- `NotFoundException` — entity not found
- `BadRequestException` — invalid input or business rule violation
- `InternalServerErrorException` — external service failures
- Always log errors and capture with `Sentry.captureException(error)`
- Pass cause: `throw new InternalServerErrorException('msg', { cause: error })`

### Data Transformation

- `plainToInstance()` — DB/external data to domain models
- `instanceToPlain()` — domain models to DB-ready data
- Always transform before returning from public methods

### Transaction Pattern

```typescript
return this.prismaService.client.$transaction(async (tx) => {
  const e1 = await tx.entity1.create({ data: ... });
  const e2 = await tx.entity2.create({ data: ... });
  return { e1, e2 };
});
```

### Event Emission

```typescript
this.eventEmitter.emit(PayrollEvents.Draft, context, entity, {
  additionalData: true,
});
```

---

## Repository Conventions

### Method Naming

| Method                             | Returns                              | Throws?             |
| ---------------------------------- | ------------------------------------ | ------------------- |
| `getUnique(where)`                 | entity or `null`                     | No                  |
| `getUniqueOrThrow(where)`          | entity                               | `NotFoundException` |
| `getUniqueWithRelations(where)`    | entity with relations or `null`      | No                  |
| `list(query)`                      | `[Entity[], number]` (items + count) | No                  |
| `create(data)`                     | entity                               | No                  |
| `updateById(id, data)`             | entity                               | No                  |
| `updateByRemoteId(remoteId, data)` | entity                               | No                  |
| `deleteById(id)`                   | `void`                               | No                  |
| `getManyByIds(ids)`                | entity[]                             | No                  |
| `exists(where)`                    | `boolean`                            | No                  |

### JSON Field Handling with Prisma

Prisma requires `Prisma.DbNull` for null JSON fields — plain `null` won't work:

```typescript
// Create — default to DbNull
jsonField: data.jsonField ?? Prisma.DbNull;

// Update — convert null to DbNull
jsonField: data.jsonField === null ? Prisma.DbNull : data.jsonField;

// Read — transform from JsonValue
jsonField: entity.jsonField
  ? plainToInstance(JsonModel, entity.jsonField)
  : null;
```

### Relation Loading

- Single entity: `relationLoadStrategy: 'join'`
- Lists: default query strategy (no option needed)

### Pagination Pattern

```typescript
const [entities, total] = await Promise.all([
  this.prismaService.client.entity.findMany({ where, orderBy, skip, take }),
  this.prismaService.client.entity.count({ where }),
]);
```

Use `composeOrderBy(field, sort)` from `common/utils/prisma`.

### Transaction Support

Accept `Prisma.TransactionClient` as parameter for transactional operations.

### Type Safety

Use Prisma's generated types: `Prisma.EntityWhereUniqueInput`, `Prisma.EntityCreateInput`, `Prisma.EntityGetPayload<{include: ...}>`.

## Anti-Patterns

- Authorization logic in services (belongs in controllers)
- Raw Prisma models returned from services (transform first)
- Swallowing errors silently (always log + Sentry)
- `any` type anywhere
- Business logic in repositories
- N+1 queries (use includes or batch)
