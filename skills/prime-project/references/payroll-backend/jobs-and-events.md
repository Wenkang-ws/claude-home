# Jobs & Events — payroll-backend

## Event Listeners

### Location & Naming

- `src/app/<module>/listeners/<entity>.listener.ts`

### Key Rules

- **Listeners MUST swallow errors** — never throw from event handlers (breaks main flow)
- Always wrap handler body in try/catch, log error + `Sentry.captureException(error)`
- Use `@OnEvent(EventName)` decorator from `@nestjs/event-emitter`
- Define event constants in `src/constants/event-emitter.constant.ts`

### Emitting Events

```typescript
this.eventEmitter.emit(YourEvents.Created, context, entity);
```

---

## Background Jobs (BullMQ)

### CRITICAL: Queue Selection

**DO NOT create new queues.** Ask the user whether to create a new queue or reuse an existing one.

Existing queues (from `src/constants/queues.constant.ts`):

| Enum                                        | Queue Name                           | Purpose                        |
| ------------------------------------------- | ------------------------------------ | ------------------------------ |
| `PayrollServiceJobQueues.CatchAllJobQueue`  | `payroll-notification-queue`         | General catch-all queue        |
| `CheckhqJobQueues.CheckhqJobQueue`          | `checkhq-processing-queue`           | CheckHQ-related processing     |
| `PayrollQueueNames.RegisterTeamMemberIssue` | `payroll-register-team-member-issue` | Team member issue registration |
| `PayrollQueueNames.RegisterEmployeeIssue`   | `payroll-register-employee-issue`    | Employee issue registration    |
| `BenefitQueue.ScheduledSync`                | `benefit-scheduled-sync`             | Benefit sync                   |

### Job Pattern

- `@Injectable()` class with `async perform(data)` method
- Located in `src/app/<module>/jobs/<purpose>.job.ts`
- **Jobs SHOULD throw errors** to trigger BullMQ retries (opposite of listeners!)
- Always log + `Sentry.captureException(error)` before re-throwing

### Job Registration — CRITICAL

Jobs **MUST** be registered with explicit name for processor resolution:

```typescript
// In module providers:
{ provide: YourJob.name, useClass: YourJob }
```

Without this, the processor's `moduleRef.resolve(job.name, ...)` will fail silently.

### Processor Pattern

- Extend `WorkerHostBaseProcessor` (in `src/app/common/jobs/`)
- Use `ModuleRef.resolve()` with `ContextIdFactory.create()` to resolve job instances
- Standard processor already exists for `CatchAllJobQueue` — usually no need to create new ones

### Enqueuing Jobs

```typescript
await this.jobQueue.add(YourJob.name, data, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 5000 },
  removeOnComplete: true,
  removeOnFail: false,
});
```

### Bulk Enqueue

```typescript
await this.jobQueue.addBulk(
  items.map((data) => ({
    name: YourJob.name,
    data,
    opts: { attempts: 3, backoff: { type: 'exponential', delay: 5000 } },
  }))
);
```

### Module Setup for Queues

```typescript
imports: [
  BullModule.registerQueue({ name: QueueName }),
  BullBoardModule.forFeature({ name: QueueName, adapter: BullMQAdapter }),
],
```

## Error Handling Summary

| Component       | Error Strategy                                       |
| --------------- | ---------------------------------------------------- |
| Event listeners | **Swallow** — catch, log, Sentry, never throw        |
| Jobs            | **Throw** — catch, log, Sentry, re-throw for retries |

## Anti-Patterns

- Creating new queues without asking
- Throwing from event handlers
- Forgetting `{ provide: Job.name, useClass: Job }` registration
- Missing `perform()` method on job classes
- `any` for job data — define interfaces
