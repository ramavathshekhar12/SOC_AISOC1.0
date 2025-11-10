# Prompts for Developers (to narrate requirements)

## 1) Backend (Manager) Prompt
"Build a FastAPI service named **AI-SOC Manager** that exposes `/intake` for JSON events from agents, decodes them using a decoders YAML, evaluates a rules YAML with support for: `decoder` match, `contains`, `field_equals`, and `event_id`. For each matched rule, create an alert with fields {ts, rule_id, rule_name, level, tags, event} and index it into OpenSearch index `ai_soc-alerts`. Add a stubbed Active Response handler invoked via `actions` array in rules. Provide `/alerts?q=&limit=` endpoint to query latest alerts via OpenSearch. Include unit-testable modules for RulesEngine and Decoder."

## 2) Agent Prompt
"Create a Python client named **AI-SOC Agent** that tails specified files and detects modifications to a list of files by hashing (simple FIM). On new lines or hash changes, post an event to Manager `/intake` with fields: source, host, and `@raw`. Provide CLI flags `--manager`, `--token`, `--watch` (repeatable), and `--fim` (repeatable)."

## 3) PT Orchestrator Prompt
"Create a FastAPI service named **AI-SOC PT Orchestrator** that offers a safe `/nmap?target=` endpoint (IPv4 only). The service must enforce an `ALLOWED_CIDRS` allowlist via environment variable, reject targets outside allowlist, and execute `nmap -sV -T4` with a 120s timeout. Return stdout/stderr/rc and executed command. Never allow domain names and never run privileged scans."

## 4) AI Anomaly Service Prompt
"Create a FastAPI service named **AI-SOC Anomaly** implementing endpoints: `/train` with list of numeric feature vectors to fit an IsolationForest, and `/score` to return anomaly scores and labels for supplied vectors. Keep it stateless and minimal; persistence is out-of-scope."

## 5) Dashboard Prompt
"Create a minimal React (Vite) app that hits `VITE_MANAGER_API/alerts` and renders a simple table of alerts (ts, rule, level, tags, host, message). Keep styling minimal and avoid frameworks to reduce complexity."

## 6) Hardening / Next Prompts
- "Refactor Manager to support **mTLS** for agent connections (client cert validation) and JWT/OIDC for dashboard/admin users."
- "Extend Rules DSL to support **frequency/time-window** correlation and CDB allow/deny list lookups."
- "Add **Windows Event Log** and **Linux auditd/Sysmon** normalizers."
- "Implement **watchlists** (IPs, hashes, users) and matchers with auto‑enrichment (GeoIP/ASN)."
- "Add **ILM** and S3-compatible snapshots in OpenSearch with retention policies per index."
