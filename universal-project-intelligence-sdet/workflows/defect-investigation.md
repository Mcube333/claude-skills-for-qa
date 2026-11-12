# Workflow: defect investigation and root-cause analysis

1. Capture symptom, environment, build/version, reproduction steps, expected vs actual, frequency and impact.
2. Identify affected business workflow and subsystem.
3. Trace relevant UI/API/handler/service/data/event paths.
4. Inspect validation, state transitions, concurrency, retries, timeouts, feature flags and environment configuration.
5. Correlate logs/traces only if supplied or access is approved; redact sensitive values.
6. Develop ranked hypotheses with supporting and contradicting evidence.
7. Separate confirmed root cause from likely cause and unknowns.
8. Recommend reproduction, targeted tests, fix direction and regression scope.
9. Do not edit code or access production systems without explicit approval.
