# Security analysis

Perform a static, evidence-based review only unless a separate approved security test is requested. Look for:
- authentication and session/token handling;
- authorization and access-control checks;
- input validation and output encoding;
- injection risks (SQL/NoSQL/command/template);
- XSS, CSRF, SSRF, path traversal and unsafe deserialization exposure;
- cryptography and TLS configuration evidence;
- secret management and accidental secret exposure;
- sensitive logging and data handling;
- dependency and container scanning evidence;
- security headers, CORS and rate limiting;
- file upload/download controls.

Report finding, severity rationale, affected component, evidence, exploitability assumptions, impact, remediation direction and validation needed. Do not claim a vulnerability is exploitable without adequate evidence. Do not claim "secure" or "no vulnerabilities" from a limited scan. Never reproduce secret values; redact and identify only the file/key name and approximate location.
