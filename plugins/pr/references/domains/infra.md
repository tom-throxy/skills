# Infrastructure

Load when the change adds or alters services, deployables, datastores, queues, caches, cloud resources, IaC, CI/CD or runtime configuration.

- **Right shape for now plus expected growth**: does the setup fit today's load and the next order of magnitude, without building for the third? A Kubernetes cluster for a cron job is **over-provisioning complexity**; a single instance holding in-memory state for a growing service is **under-provisioning resilience**.
- **Fewer moving parts**: can an existing datastore, queue or service do this job? Each new component adds upgrades, monitoring, credentials, backups and failure modes. Prefer **boring technology** and managed services unless there is a stated reason.
- **Upgradeability**: how will this be upgraded or migrated in a year? Pinned versions, standard tooling and declarative config (IaC) make later change cheaper than hand-configured resources (**snowflake servers**, **click-ops**).
- **Failure isolation and blast radius**: what else goes down when this does? Is there a single point of failure that matters at this stakes profile?
- **State**: where does state live? Can instances be replaced or scaled out without losing it?
- **Cost**: what does it cost at today's load and at 10x? Is anything priced per request, per GB or per seat in a way that scales badly? Are idle resources left running?
- **Environments**: does it work the same way in local, staging and production? Do secrets and config come from the existing mechanism?
- **Security posture**: least-privilege credentials, nothing public that need not be, secrets not baked into images or config.
- **Deploy and rollback**: does the deploy order matter across services? Can it roll back without manual steps?
