import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from opensearchpy import OpenSearch
from rules_engine import RulesEngine
from decoder import Decoder
from active_response import run_action

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
AGENT_SHARED_TOKEN = os.getenv("AGENT_SHARED_TOKEN", "changeme")

index_alerts = "ai_soc-alerts"

app = FastAPI(title="AI-SOC Manager", version="0.1.0")

# Clients
os_client = OpenSearch(
    hosts=[OPENSEARCH_URL],
    http_compress=True
)

# bootstrap index
if not os_client.indices.exists(index=index_alerts):
    os_client.indices.create(index=index_alerts)

rules = RulesEngine("/app/rules.yml")
decoder = Decoder("/app/decoders.yml")

class IntakeEvent(BaseModel):
    source: str
    host: str
    @raw: str | None = None
    message: str | None = None
    extra: dict | None = None

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

@app.post("/intake")
def intake(event: IntakeEvent, x_agent_token: str = Header(None)):
    if x_agent_token != AGENT_SHARED_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")
    e = event.model_dump()
    # decode
    e, used = decoder.apply(e)
    # evaluate rules
    hits = rules.match(e)
    alerts = []
    for r in hits:
        alert = {
            "ts": _now_iso(),
            "rule_id": r["id"],
            "rule_name": r.get("name"),
            "level": r.get("level", 1),
            "tags": r.get("tags", []),
            "event": e
        }
        # actions
        for act in r.get("actions", []):
            ar = run_action(act, alert)
            alert.setdefault("actions", []).append({"name": act, "result": ar})

        os_client.index(index=index_alerts, body=alert)
        alerts.append(alert)
    return {"matched": len(hits), "alerts": alerts}

@app.get("/alerts")
def search_alerts(q: str | None = None, limit: int = 50):
    body = {"size": limit, "sort": [{"ts": {"order": "desc"}}]}
    if q:
        body["query"] = {"query_string": {"query": q}}
    else:
        body["query"] = {"match_all": {}}
    res = os_client.search(index=index_alerts, body=body)
    return [hit["_source"] for hit in res["hits"]["hits"]]
