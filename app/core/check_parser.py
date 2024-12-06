from typing import Dict, Any, Optional
import numpy as np
import cv2
from PIL import Image
import io
import logging
from .image_processor import ImageProcessor
from .ocr_engine import OCREngine
from .fraud_detector import FraudDetector

logger = logging.getLogger(__name__)

class CheckParser:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.ocr_engine = OCREngine()
        self.fraud_detector = FraudDetector()
        
    def parse_check(self, image_data: bytes) -> Dict[str, Any]:
        """Parse check image and extract information"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Preprocess image
            logger.debug("Preprocessing image...")
            processed_image = self.image_processor.preprocess_image(image)
            
            # Extract regions
            logger.debug("Extracting regions...")
            regions = self.image_processor.extract_regions(processed_image)
            
            # Extract amount
            logger.debug("Extracting amount...")
            amount = self.ocr_engine.extract_amount(regions['amount'])
            
            # Extract date
            logger.debug("Extracting date...")
            date = self.ocr_engine.extract_date(regions['date'])
            date_str = date.strftime('%Y-%m-%d') if date else None
            
            # Extract MICR data
            logger.debug("Processing MICR region...")
            enhanced_micr = self.image_processor.enhance_micr(regions['micr'])
            micr_data = self.ocr_engine.extract_micr(enhanced_micr)
            
            # Fraud detection
            logger.debug("Running fraud detection...")
            is_fraudulent, fraud_confidence = self.fraud_detector.detect_fraud(image)
            
            # Signature verification
            logger.debug("Analyzing signature...")
            signature_analysis = self.fraud_detector.analyze_signature(regions['signature'])
            
            # Prepare results
            check_data = {
                'amount_numeric': amount,
                'date': date_str,
                'bank_code': micr_data['bank_code'],
                'account_number': micr_data['account_number'],
                'check_number': micr_data['check_number'],
                'fraud_detected': is_fraudulent,
                'signature_verified': signature_analysis['confidence'] > 0.7
            }
            
            logger.info(f"Successfully parsed check: {check_data}")
            return check_data
            
        except Exception as e:
            logger.error(f"Error parsing check: {str(e)}")
            raise