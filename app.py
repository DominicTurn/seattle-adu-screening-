import os
import json
import logging
from flask import Flask, render_template, request
from engine import evaluate_rules

# --- Configuration ---
RULES_FILE = 'seattle_phase1_rules.json'

# --- Validation Constants ---
VALID_ZONE_FAMILY = {'NR', 'RSL', 'LOWRISE', 'OTHER', 'UNKNOWN'}
VALID_ZONE_DETAIL = {'', 'NR1', 'NR2', 'NR3', 'RSL', 'LOWRISE', 'UNKNOWN'}
VALID_ADU_PLAN = {'AADU', 'DADU', 'BOTH', 'UNSURE'}
VALID_EXISTING_ADUS = {'', '0', '1', '2'}
VALID_ADDING_SECOND_ADU = {'', 'true', 'false'}
VALID_SECOND_ADU_CRITERIA = {'', 'GREEN', 'AFFORDABLE', 'UNKNOWN', 'NONE'}
VALID_REMOVING_PARKING = {'YES', 'NO', 'UNKNOWN'}
VALID_ACK_SEWER = {'YES', 'NO', 'UNKNOWN'}

# Numeric field limits (min, max)
NUMERIC_LIMITS = {
    'lot_size_sqft': (0, 1000000),
    'proposed_adu_sqft': (0, 5000)
}

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app')

app = Flask(__name__)

# --- Helper Functions ---
def load_rules():
    """Safely loads the JSON rules file."""
    if not os.path.exists(RULES_FILE):
        logger.critical(f"Rules file missing: {RULES_FILE}")
        return None
    try:
        with open(RULES_FILE, 'r', encoding='utf-8-sig') as f:
            logger.info("Rules loaded successfully.")
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.critical(f"Invalid JSON format in rules file: {e}")
        return None

# Load rules once at startup
RULES_DATA = load_rules()

def validate_input(raw_data):
    """
    Server-side validation of all form inputs.
    Returns (is_valid, error_message, cleaned_data)
    """
    errors = []
    
    # Validate zone_family (required)
    zone_family = raw_data.get('zone_family', '').strip()
    if not zone_family:
        errors.append('Zone Family is required.')
    elif zone_family not in VALID_ZONE_FAMILY:
        errors.append(f'Invalid Zone Family: {zone_family}')
    
    # Validate zone_detail (optional)
    zone_detail = raw_data.get('zone_detail', '').strip()
    if zone_detail and zone_detail not in VALID_ZONE_DETAIL:
        errors.append(f'Invalid Zone Detail: {zone_detail}')
    
    # Validate adu_plan (required)
    adu_plan = raw_data.get('adu_plan', '').strip()
    if not adu_plan:
        errors.append('ADU Plan is required.')
    elif adu_plan not in VALID_ADU_PLAN:
        errors.append(f'Invalid ADU Plan: {adu_plan}')
    
    # Validate existing_adus (optional, must be 0, 1, 2, or empty)
    existing_adus = raw_data.get('existing_adus', '').strip()
    if existing_adus and existing_adus not in VALID_EXISTING_ADUS:
        errors.append(f'Invalid Existing ADUs value: {existing_adus}. Must be 0, 1, or 2.')
    
    # Validate adding_second_adu (optional)
    adding_second = raw_data.get('adding_second_adu', '').strip()
    if adding_second and adding_second not in VALID_ADDING_SECOND_ADU:
        errors.append(f'Invalid Adding Second ADU value: {adding_second}')
    
    # Validate second_adu_criteria (optional)
    second_criteria = raw_data.get('second_adu_criteria', '').strip()
    if second_criteria and second_criteria not in VALID_SECOND_ADU_CRITERIA:
        errors.append(f'Invalid Second ADU Criteria: {second_criteria}')
    
    # Validate removing_required_parking (required)
    removing_parking = raw_data.get('removing_required_parking', '').strip()
    if not removing_parking:
        errors.append('Removing Required Parking is required.')
    elif removing_parking not in VALID_REMOVING_PARKING:
        errors.append(f'Invalid Removing Required Parking value: {removing_parking}')
    
    # Validate ack_sewer_capacity_charge (required)
    ack_sewer = raw_data.get('ack_sewer_capacity_charge', '').strip()
    if not ack_sewer:
        errors.append('Acknowledge Sewer Capacity Charge is required.')
    elif ack_sewer not in VALID_ACK_SEWER:
        errors.append(f'Invalid Acknowledge Sewer Charge value: {ack_sewer}')
    
    # Validate numeric fields with min/max limits
    for field_name, (min_val, max_val) in NUMERIC_LIMITS.items():
        field_value = raw_data.get(field_name, '').strip()
        if field_value:
            try:
                num_val = float(field_value)
                if num_val < min_val or num_val > max_val:
                    errors.append(f'{field_name} must be between {min_val} and {max_val}.')
                elif not num_val.is_integer() or num_val < 0:
                    errors.append(f'{field_name} must be a non-negative integer.')
            except ValueError:
                errors.append(f'{field_name} must be a valid number.')
    
    if errors:
        return False, ' '.join(errors), None
    
    return True, None, raw_data


def preprocess_form_data(raw_data):
    """
    Cleans form data to match JSON expected types.
    - Converts empty strings to None
    - Converts numeric strings to integers
    - Converts 'true'/'false' strings to booleans
    """
    cleaned = {}
    numeric_fields = ['lot_size_sqft', 'proposed_adu_sqft', 'existing_adus']
    
    for key, val in raw_data.items():
        # Strip whitespace if string
        val = val.strip() if isinstance(val, str) else val
        
        # Handle Empty
        if val == "":
            cleaned[key] = None
        
        # Handle Numbers (convert to int for whole numbers)
        elif key in numeric_fields:
            try:
                cleaned[key] = int(float(val))
            except ValueError:
                cleaned[key] = None
        
        # Handle Booleans (HTML forms send 'true'/'false' as strings)
        elif val == "true":
            cleaned[key] = True
        elif val == "false":
            cleaned[key] = False
        
        else:
            cleaned[key] = val
            
    return cleaned

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    if not RULES_DATA:
        return "<h3>System Error</h3><p>Rules configuration file is missing or invalid.</p>", 500
    return render_template('form.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if not RULES_DATA:
        return "Rules not loaded", 500
    
    try:
        # 1. Get Raw Data
        raw_data = request.form.to_dict()
        
        # 2. Server-side Validation
        is_valid, error_message, _ = validate_input(raw_data)
        if not is_valid:
            logger.warning(f"Validation failed: {error_message}")
            return render_template('form.html', error=error_message), 400
        
        # 3. Clean Data
        clean_inputs = preprocess_form_data(raw_data)
        
        logger.info(f"Processing evaluation for inputs: {clean_inputs.keys()}")

        # 4. Run Engine
        results = evaluate_rules(clean_inputs, RULES_DATA)
        
        # 5. Render Results
        return render_template('result.html', results=results)

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return "An internal error occurred. Please try again.", 500

if __name__ == '__main__':
    # Debug is True for MVP handoff purposes
    app.run(debug=True, port=5000)