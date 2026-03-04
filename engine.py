import logging

logger = logging.getLogger("adu_engine")


def evaluate_rules(inputs: dict, rules_data: dict) -> dict:
    """
    Main evaluation function.
    Returns structured result used by result.html
    """

    engine_config = rules_data.get("engine", {})
    rules = rules_data.get("rules", [])

    score = engine_config.get("scoring", {}).get("start", 100)

    reasons = []
    next_steps = []

    any_blocker = False

    for rule in rules:

        try:

            if not evaluate_condition(rule.get("when"), inputs):
                continue

            severity = rule.get("severity", "info")
            impact = rule.get("score_impact", 0)
            message = rule.get("message")

            score += impact

            if message:
                reasons.append({
                    "severity": severity,
                    "message": message
                })

            if severity == "blocker":
                any_blocker = True

        except Exception as e:
            logger.warning(f"Rule error {rule.get('id')}: {e}")

    decision = determine_label(score, any_blocker, engine_config)

    return {
        "score": score,
        "decision": decision,
        "reasons": reasons,
        "next_steps": build_next_steps(inputs)
    }


def evaluate_condition(condition: dict, inputs: dict) -> bool:
    """
    Recursive rule condition evaluator
    """

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
        return user_value in value

    if op == "not_in":
        return user_value not in value

    return False


def determine_label(score: int, any_blocker: bool, engine_config: dict) -> str:
    """
    Determine final readiness label
    """

    labels = engine_config.get("labels", [])

    for rule in labels:

        cond = rule.get("if", {})
        label = rule.get("label")

        if cond.get("any_blocker") and any_blocker:
            return label

        if "score_lt" in cond and score < cond["score_lt"]:
            return label

        if "score_gte" in cond and score >= cond["score_gte"]:
            return label

    return "POSSIBLE"


def build_next_steps(inputs: dict) -> list:
    """
    Simple recommendations engine
    """

    steps = []

    if inputs.get("zoning") == "IDK":
        steps.append(
            "Confirm your zoning using the Seattle GIS zoning map."
        )

    if inputs.get("pro_help") == "NO":
        steps.append(
            "Consider consulting an architect or ADU designer to verify feasibility."
        )

    if inputs.get("adu_type") == "DETACHED_NEW":
        steps.append(
            "Review Seattle detached ADU setback and lot coverage requirements."
        )

    if inputs.get("biggest_concern") == "COST":
        steps.append(
            "Typical Seattle ADU construction costs range from $250k to $400k depending on design."
        )

    if inputs.get("biggest_concern") == "TIMELINE":
        steps.append(
            "Permitting and construction timelines for Seattle ADUs often range from 8 to 14 months."
        )

    if inputs.get("biggest_concern") == "WHERE_TO_START":
        steps.append(
            "Start by confirming zoning, lot size, and existing structures on your property."
        )

    return steps
