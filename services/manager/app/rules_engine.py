from typing import List, Dict, Any
import yaml

class RulesEngine:
    def __init__(self, rules_path: str):
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f) or []

    def match(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        matched = []
        for rule in self.rules:
            m = rule.get("match", {})
            ok = True
            # Decoder match (optional)
            if "decoder" in m and event.get("decoder") != m["decoder"]:
                ok = False
            # contains on raw message
            if ok and "contains" in m:
                raw = (event.get("message") or event.get("@raw") or "")
                if m["contains"] not in raw:
                    ok = False
            # field_equals checks
            if ok and "field_equals" in m:
                for k, v in m["field_equals"].items():
                    if event.get(k) != v:
                        ok = False
                        break
            # Windows event_id check
            if ok and "event_id" in m:
                if event.get("event_id") != m["event_id"]:
                    ok = False

            if ok:
                matched.append(rule)
        return matched
