import os
import json
import logging
import re
from flask import Flask, render_template, request

from engine import evaluate_rules

# -----------------------------
# Config
# -----------------------------
RULES_FILE = os.getenv("RULES_FILE", "seattle_phase1_rules.json")
PORT = int(os.getenv("PORT", "5000"))

# New form schema validation
VALID_ZONING = {"NR", "RSL", "LOWRISE", "OTHER", "IDK"}
VALID_LOT_SIZE_RANGE = {"UNDER_3200", "3200_5000", "OVER_5000", "UNKNOWN"}
VALID_DETACHED_STRUCTURE = {"YES", "NO"}
VALID_ADU_TYPE = {"ATTACHED", "DETACHED_NEW", "CONVERT_EXISTING", "NOT_SURE"}
VALID_MOTIVATION = {"RENTAL_INCOME", "FAMILY_MEMBER", "PROPERTY_VALUE", "ALL"}
VALID_OWNER_OCCUPIED = {"YES", "NO"}
VALID_PRO_HELP = {"YES", "NO", "PLANNING"}
VALID_BIGGEST_CONCERN = {"COST", "ALLOWED", "TIMELINE", "WHERE_TO_START"}

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seattle_adu_app")

app = Flask(__name__)


# -----------------------------
# Helpers
# -----------------------------
def load_rules() -> dict | None:
    """Load rules JSON once at startup."""
    if not os.path.exists(RULES_FILE):
        logger.critical(f"Rules file missing: {RULES_FILE}")
        return None

    try:
        with open(RULES_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            logger.info(f"Rules loaded successfully from {RULES_FILE}")
            return data
    except json.JSONDecodeError as e:
        logger.critical(f"Invalid JSON in rules file: {e}")
        return None
    except Exception as e:
        logger.critical(f"Failed to load rules: {e}")
        return None


RULES_DATA = load_rules()


def preprocess_form_data(raw_data: dict) -> dict:
    """
    Clean form data:
    - strip strings
    - convert empty strings to None
    """
    cleaned = {}
    for k, v in raw_data.items():
        if isinstance(v, str):
            v = v.strip()
        cleaned[k] = None if v == "" else v
    return cleaned


def validate_input(clean: dict) -> tuple[bool, str | None]:
    """Server-side validation for the new under-2-min form."""
    errors: list[str] = []

    # Email
    email = (clean.get("email") or "").strip()
    if not email:
        errors.append("Email is required.")
    elif not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")

    def req_select(field: str, valid: set[str], label: str):
        val = clean.get(field)
        if not val:
            errors.append(f"{label} is required.")
            return
        if val not in valid:
            errors.append(f"Invalid {label.lower()} value.")

    req_select("zoning", VALID_ZONING, "Seattle zoning")
    req_select("lot_size_range", VALID_LOT_SIZE_RANGE, "Lot size range")
    req_select("detached_structure", VALID_DETACHED_STRUCTURE, "Detached structure")
    req_select("adu_type", VALID_ADU_TYPE, "ADU type")
    req_select("motivation", VALID_MOTIVATION, "Motivation")
    req_select("owner_occupied", VALID_OWNER_OCCUPIED, "Owner occupancy")
    req_select("pro_help", VALID_PRO_HELP, "Architect/contractor status")
    req_select("biggest_concern", VALID_BIGGEST_CONCERN, "Biggest concern")

    if errors:
        return False, " ".join(errors)
    return True, None


def build_payload(clean: dict) -> dict:
    """
    Payload passed to the rules engine + templates.
    Keeps only what we care about for evaluation and report personalization.
    """
    return {
        "email": clean.get("email"),
        "address": clean.get("address"),
        "zoning": clean.get("zoning"),
        "lot_size_range": clean.get("lot_size_range"),
        "detached_structure": clean.get("detached_structure"),
        "adu_type": clean.get("adu_type"),
        "motivation": clean.get("motivation"),
        "owner_occupied": clean.get("owner_occupied"),
        "pro_help": clean.get("pro_help"),
        "biggest_concern": clean.get("biggest_concern"),
    }


# -----------------------------
# Routes
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    if not RULES_DATA:
        return (
            "System Error: Rules configuration file is missing or invalid.",
            500,
        )
    return render_template("form.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    if not RULES_DATA:
        return "Rules not loaded", 500

    try:
        raw = request.form.to_dict()
        clean = preprocess_form_data(raw)

        ok, err = validate_input(clean)
        if not ok:
            logger.warning(f"Validation failed: {err}")
            return render_template("form.html", error=err), 400

        payload = build_payload(clean)

        logger.info(
            "Evaluating: zoning=%s lot=%s adu_type=%s",
            payload.get("zoning"),
            payload.get("lot_size_range"),
            payload.get("adu_type"),
        )

        results = evaluate_rules(payload, RULES_DATA)

        # results.html uses: results + inputs
        return render_template("result.html", results=results, inputs=payload)

    except Exception as e:
        logger.exception(f"Evaluation error: {e}")
        return "An internal error occurred. Please try again.", 500


# -----------------------------
# Local dev only
# (Production uses gunicorn + systemd)
# -----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=True)
