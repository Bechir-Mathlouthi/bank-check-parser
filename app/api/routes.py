from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
import uuid
from ..core.check_parser import CheckParser
from ..models.check import Check
from ..database import get_db, init_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)
check_parser = CheckParser()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/checks/upload', methods=['POST'])
def upload_check():
    """Handle check image upload and processing"""
    try:
        # Debug logging
        logger.debug("Files in request: %s", request.files)
        logger.debug("Request form data: %s", request.form)
        
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        logger.debug("Received file: %s, type: %s", file.filename, file.content_type)
        
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            logger.error("Invalid file type: %s", file.filename)
            return jsonify({'error': f'Invalid file type. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
            
        try:
            # Read file contents
            file_bytes = file.read()
            
            # Parse check
            check_data = check_parser.parse_check(file_bytes)
            
            # Convert any non-serializable types
            check_data = {
                'amount_numeric': float(check_data.get('amount_numeric', 0.0)),
                'date': str(check_data.get('date')) if check_data.get('date') else None,
                'bank_code': str(check_data.get('bank_code', '')),
                'account_number': str(check_data.get('account_number', '')),
                'check_number': str(check_data.get('check_number', '')),
                'fraud_detected': bool(check_data.get('fraud_detected', False)),
                'signature_verified': bool(check_data.get('signature_verified', False))
            }
            
            # Save to database
            db = next(get_db())
            check = Check(**check_data)
            db.add(check)
            db.commit()
            
            # Get the data after save to include generated check number
            saved_data = check.to_dict()
            
            logger.debug("Check processed successfully: %s", saved_data)
            return jsonify({
                'message': 'Check processed successfully',
                'check_data': saved_data
            }), 200
            
        except Exception as e:
            logger.error("Error processing file: %s", str(e))
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return jsonify({'error': str(e)}), 500

@api.route('/checks/<check_id>', methods=['GET'])
def get_check(check_id):
    """Retrieve check details"""
    try:
        db = next(get_db())
        check = db.query(Check).filter(Check.id == check_id).first()
        
        if not check:
            return jsonify({'error': 'Check not found'}), 404
            
        return jsonify(check.to_dict()), 200
    except Exception as e:
        logger.error("Error retrieving check: %s", str(e))
        return jsonify({'error': str(e)}), 500

@api.route('/checks', methods=['GET'])
def get_all_checks():
    """Retrieve all checks"""
    try:
        db = next(get_db())
        checks = db.query(Check).all()
        return jsonify([check.to_dict() for check in checks]), 200
    except Exception as e:
        logger.error("Error retrieving checks: %s", str(e))
        return jsonify({'error': str(e)}), 500 