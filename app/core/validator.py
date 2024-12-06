from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import re

class CheckValidator:
    def __init__(self):
        self.validation_rules = {
            'date': self._validate_date,
            'amount': self._validate_amount,
            'micr': self._validate_micr,
            'signature': self._validate_signature
        }
        
    def validate_check(self, check_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate all check data"""
        errors = []
        
        for field, validator in self.validation_rules.items():
            is_valid, error = validator(check_data)
            if not is_valid:
                errors.append(error)
                
        return len(errors) == 0, errors
        
    def _validate_date(self, check_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate check date"""
        date = check_data.get('date')
        if not date:
            return False, "Date is missing"
            
        try:
            check_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Check if date is not in future
            if check_date > datetime.now():
                return False, "Post-dated check"
                
            # Check if date is not too old (e.g., 6 months)
            if check_date < datetime.now() - timedelta(days=180):
                return False, "Check is too old"
                
            return True, ""
            
        except ValueError:
            return False, "Invalid date format"
            
    def _validate_amount(self, check_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate check amount"""
        amount = check_data.get('amount_numeric')
        
        if not amount:
            return False, "Amount is missing"
            
        try:
            amount_float = float(amount)
            
            # Basic amount validation rules
            if amount_float <= 0:
                return False, "Amount must be positive"
            if amount_float > 10000000:  # Example limit
                return False, "Amount exceeds maximum limit"
                
            return True, ""
            
        except ValueError:
            return False, "Invalid amount format"
            
    def _validate_micr(self, check_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate MICR code"""
        micr = check_data.get('micr_code')
        
        if not micr:
            return False, "MICR code is missing"
            
        # Check MICR format (example pattern)
        micr_pattern = r'^\d{9}$'  # Simplified pattern
        if not re.match(micr_pattern, micr):
            return False, "Invalid MICR format"
            
        return True, ""
        
    def _validate_signature(self, check_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate signature verification"""
        signature_verified = check_data.get('signature_verified', False)
        
        if not signature_verified:
            return False, "Signature verification failed"
            
        return True, "" 