# Async, events and integrations

Load when the change adds or alters queues, background jobs, cron, webhooks, event publishing or consuming, streaming, or calls to third-party services.

- **Delivery semantics**: assume **at-least-once** delivery. Are consumers **idempotent**? What deduplicates a replayed webhook or redelivered message?
- **Ordering**: does correctness depend on events arriving in order? Most queues do not guarantee it across partitions or retries.
- **Dual writes**: does the code write to the database and publish an event as two separate steps? One can succeed without the other. Consider the **transactional outbox** pattern.
- **Failure handling**: what happens after the final retry? Is there a **dead-letter queue**, and does anyone look at it? Do retries use backoff with jitter, or can they cause a **retry storm**?
- **Back-pressure**: what happens when producers outpace consumers? Is queue depth bounded and monitored?
- **Timeouts**: does every outbound call have a timeout? Can a slow upstream exhaust workers or connections? Consider a **circuit breaker** for a flaky dependency.
- **Third-party limits**: rate limits, quotas, pricing per call, webhook signature verification, and API version pinning.
- **Contracts**: is the event or payload schema versioned? Who else consumes it? Adding a field is safe; renaming or removing one breaks consumers you may not know about.
- **Scheduling**: do cron jobs survive overlapping runs, missed runs, and multiple instances (needs a lock or leader election)? Which time zone do they run in?
- **Sync or async at all**: does this need to be async? A queue adds latency, operational load and failure modes. Use one for a concrete reason: slow work off the request path, absorbing spikes, or decoupling deploys.
