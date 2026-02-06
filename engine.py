import logging
from typing import Dict, List, Any, Set

# Configure logging
logger = logging.getLogger(__name__)

def evaluate_rules(user_inputs: Dict[str, Any], rules_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates user inputs against the loaded JSON rules configuration.
    
    Args:
        user_inputs: Dictionary of sanitized form data.
        rules_config: The loaded JSON rules object.
        
    Returns:
        Dict containing decision, score, reasons, and next_steps.
    """
    try:
        # 1. Safely extract core configs
        engine_settings = rules_config.get('engine', {})
        rules_list = rules_config.get('rules', [])
        
        # 2. Initialize State
        current_score = engine_settings.get('scoring', {}).get('start', 100)
        triggered_reasons: List[str] = []
        triggered_next_steps: Set[str] = set() # Set prevents duplicates
        is_blocked = False

        # 3. Iterate Rules
        for rule in rules_list:
            rule_id = rule.get('id', 'unknown')
            
            try:
                # Check condition strictly
                if _check_condition(rule.get('when', {}), user_inputs):
                    
                    # Apply Score Impact
                    current_score += rule.get('score_impact', 0)
                    
                    # Collect Message
                    if 'message' in rule:
                        triggered_reasons.append(rule['message'])
                    
                    # Collect Next Steps
                    if 'next_steps' in rule:
                        for step in rule['next_steps']:
                            triggered_next_steps.add(step)
                            
                    # Check for Blockers
                    if rule.get('severity') == 'blocker':
                        is_blocked = True
                        
            except Exception as e:
                # Log error but continue processing other rules
                logger.error(f"Error processing rule {rule_id}: {e}")
                continue

        # 4. Determine Final Label
        final_decision = _determine_label(engine_settings, current_score, is_blocked)
        
        return {
            "decision": final_decision,
            "score": current_score,
            "reasons": triggered_reasons,
            "next_steps": list(triggered_next_steps)
        }

    except Exception as e:
        logger.critical(f"Critical Engine Failure: {e}")
        return {
            "decision": "ERROR",
            "score": 0,
            "reasons": ["An internal error occurred during evaluation."],
            "next_steps": []
        }

def _check_condition(condition: Dict[str, Any], inputs: Dict[str, Any]) -> bool:
    """
    Recursively checks logic conditions (all, any, field comparisons).
    """
    # Base Case: Always True
    if condition.get('always') is True:
        return True

    # Recursive Case: ALL (AND)
    if 'all' in condition:
        return all(_check_condition(sub, inputs) for sub in condition['all'])

    # Recursive Case: ANY (OR)
    if 'any' in condition:
        return any(_check_condition(sub, inputs) for sub in condition['any'])

    # Field Comparison
    if 'field' in condition:
        field = condition['field']
        operator = condition.get('op')
        target = condition.get('value')
        user_val = inputs.get(field)

        # Helper: Numeric Conversion for comparisons
        if isinstance(target, (int, float)) and user_val is not None:
            try:
                if str(user_val).strip() != "":
                    user_val = float(user_val)
            except ValueError:
                pass # Keep as string if conversion fails

        # Operator Logic
        if operator == 'eq': return user_val == target
        if operator == 'neq': return user_val != target
        if operator == 'gt': return user_val is not None and user_val > target
        if operator == 'lt': return user_val is not None and user_val < target
        if operator == 'gte': return user_val is not None and user_val >= target
        if operator == 'lte': return user_val is not None and user_val <= target
        if operator == 'in': return user_val in (target if isinstance(target, list) else [])
        if operator == 'is_null':
            is_empty = (user_val is None) or (str(user_val).strip() == "")
            return is_empty if target is True else not is_empty

    return False

def _determine_label(settings: Dict[str, Any], score: int, is_blocked: bool) -> str:
    """Maps score/blockers to a decision label."""
    labels = settings.get('labels', [])
    
    # Priority 1: Hard Blockers
    if is_blocked:
        return "UNLIKELY"
        
    # Priority 2: Score Thresholds
    for rule in labels:
        cond = rule.get('if', {})
        label = rule.get('label', 'UNKNOWN')
        
        if cond.get('any_blocker') and is_blocked: return label
        if 'score_lt' in cond and score < cond['score_lt']: return label
        if 'score_gte' in cond and score >= cond['score_gte']: return label
            
    return "POSSIBLE" # Default fallback