import logging

logger = logging.getLogger(__name__)

# Stubbed Active Response (extend safely with approvals/audit)
def run_action(action_name: str, alert: dict) -> dict:
    logger.info("AR invoked: %s", action_name)
    # Example only: don't run dangerous commands here.
    if action_name == "notify":
        return {"status": "ok", "message": "Notification dispatched (stub)"}
    return {"status": "noop", "message": f"No handler for action {action_name}"}
