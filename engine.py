import logging

logger = logging.getLogger("adu_engine")


def evaluate_rules(inputs: dict, rules_data: dict) -> dict:
    """
    Main evaluation function.
    Returns structured result used by result.html

    Output:
      {
        "score": int,
        "decision": str,
        "reasons": [str, ...],
        "next_steps": [str, ...]
      }
    """
    engine_config = rules_data.get("engine", {})
    rules = rules_data.get("rules", [])

    score = engine_config.get("scoring", {}).get("start", 100)

    reasons: list[str] = []
    next_steps_set: set[str] = set()

    any_blocker = False

    for rule in rules:
        try:
            if not evaluate_condition(rule.get("when"), inputs):
                continue

            severity = rule.get("severity", "info")
            impact = rule.get("score_impact", 0)
            message = rule.get("message")

            score += impact

            # Option A: store reasons as strings (template prints cleanly)
            if message:
                reasons.append(message)

            # Pull next steps directly from rules JSON (if present)
            for step in (rule.get("next_steps") or []):
                if step and isinstance(step, str):
                    next_steps_set.add(step)

            if severity == "blocker":
                any_blocker = True

        except Exception as e:
            logger.warning(f"Rule error {rule.get('id')}: {e}")

    decision = determine_label(score, any_blocker, engine_config)

    # Add dynamic next steps (based on inputs)
    for step in build_next_steps(inputs):
        next_steps_set.add(step)

    return {
        "score": score,
        "decision": decision,
        "reasons": reasons,
        "next_steps": sorted(next_steps_set)
    }


def evaluate_condition(condition: dict, inputs: dict) -> bool:
    """Recursive rule condition evaluator."""
    if not condition:
        return False

    if condition.get("always") is True:
        return True

    if "all" in condition:
        return all(evaluate_condition(c, inputs) for c in condition["all"])

    if "any" in condition:
        return any(evaluate_condition(c, inputs) for c in condition["any"])

    field = condition.get("field")
    op = condition.get("op")
    value = condition.get("value")

    user_value = inputs.get(field)

    if op == "eq":
        return user_value == value

    if op == "neq":
        return user_value != value

    if op == "in":
        return user_value in (value or [])

    if op == "not_in":
        return user_value not in (value or [])

    return False


def determine_label(score: int, any_blocker: bool, engine_config: dict) -> str:
    """Determine final readiness label."""
    labels = engine_config.get("labels", [])

    # Blockers override
    for rule in labels:
        cond = rule.get("if", {})
        label = rule.get("label", "POSSIBLE")
        if cond.get("any_blocker") and any_blocker:
            return label

    # Then score thresholds
    for rule in labels:
        cond = rule.get("if", {})
        label = rule.get("label", "POSSIBLE")

        if "score_lt" in cond and score < cond["score_lt"]:
            return label

        if "score_gte" in cond and score >= cond["score_gte"]:
            return label

    return "POSSIBLE"


def build_next_steps(inputs: dict) -> list[str]:
    """Simple recommendations engine based on inputs."""
    steps: list[str] = []

    if inputs.get("zoning") == "IDK":
        steps.append("Confirm your zoning using Seattle’s GIS zoning map.")

    if inputs.get("pro_help") == "NO":
        steps.append("Consider consulting an architect or ADU designer to verify feasibility early.")

    if inputs.get("adu_type") in ("DETACHED_NEW", "CONVERT_EXISTING"):
        steps.append("Review Seattle detached ADU setback and lot coverage requirements.")

    if inputs.get("biggest_concern") == "COST":
        steps.append("Price check: Seattle ADU builds commonly land in the $250k–$400k range depending on scope and site.")

    if inputs.get("biggest_concern") == "TIMELINE":
        steps.append("Timeline check: permitting + build is often 8–14 months depending on review path and contractor schedule.")

    if inputs.get("biggest_concern") == "WHERE_TO_START":
        steps.append("Start with: confirm zoning + lot size + whether a conversion structure is viable, then talk to a designer.")

    return steps
