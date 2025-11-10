from typing import Dict, Any, Tuple, Optional, List
import yaml

class Decoder:
    def __init__(self, decoders_path: str):
        with open(decoders_path, "r", encoding="utf-8") as f:
            self.decoders = yaml.safe_load(f) or []

    def apply(self, event: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
        raw = event.get("@raw", "") or event.get("message", "")
        for d in self.decoders:
            detects: List[str] = d.get("detect", [])
            if all(str(x) in str(raw) for x in detects):
                out = dict(event)
                out["decoder"] = d["name"]
                fields = d.get("fields", {})
                for k, source in fields.items():
                    if source == "@raw":
                        out[k] = raw
                    else:
                        out[k] = event.get(source)
                return out, d["name"]
        return event, None
