import os, subprocess, shlex, ipaddress
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

ALLOWED_CIDRS = [c.strip() for c in os.getenv("ALLOWED_CIDRS", "127.0.0.1/32").split(",")]

app = FastAPI(title="AI-SOC PT Orchestrator", version="0.1.0")

def _allowed(target: str) -> bool:
    try:
        ip = ipaddress.ip_address(target)
        for cidr in ALLOWED_CIDRS:
            if ip in ipaddress.ip_network(cidr, strict=False):
                return True
        return False
    except ValueError:
        # domain names not allowed by default (to limit abuse)
        return False

class NmapResult(BaseModel):
    command: str
    stdout: str
    stderr: str
    rc: int

@app.get("/nmap", response_model=NmapResult)
def run_nmap(target: str = Query(..., description="IPv4 address only")):
    if not _allowed(target):
        raise HTTPException(status_code=403, detail="target not in allowlist")
    cmd = f"nmap -sV -T4 {shlex.quote(target)}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return {"command": cmd, "stdout": proc.stdout, "stderr": proc.stderr, "rc": proc.returncode}
