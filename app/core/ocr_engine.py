import pytesseract
import cv2
import numpy as np
from typing import Dict, Any, Optional
import re
from datetime import datetime
import os
import logging
import sys
import subprocess

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        # Set Tesseract path directly since we know it's installed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        logger.info(f"Using Tesseract from: {pytesseract.pytesseract.tesseract_cmd}")
        
        # OCR Configuration
        self.config = '--oem 3 --psm 6'
        self.amount_pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        self.date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
        
        # Test OCR functionality
        self._test_ocr()
        
    def _test_ocr(self):
        """Test OCR functionality with a simple image"""
        try:
            # Create a simple test image with text
            test_image = np.zeros((50, 200), dtype=np.uint8)
            test_image.fill(255)  # White background
            cv2.putText(test_image, "Test123", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Try to extract text
            result = pytesseract.image_to_string(test_image).strip()
            logger.info(f"OCR test result: {result}")
            
        except Exception as e:
            logger.error(f"OCR test failed: {str(e)}")
            raise RuntimeError("Failed to perform OCR test. Please check Tesseract installation.")
        
    def extract_text(self, image: np.ndarray, preprocess: bool = True) -> str:
        """Extract text from image using Tesseract"""
        try:
            if preprocess:
                # Additional preprocessing for better OCR
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                
                # Remove noise
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                
                # Perform OCR on cleaned image
                text = pytesseract.image_to_string(opening, config=self.config)
            else:
                text = pytesseract.image_to_string(image, config=self.config)
                
            logger.debug(f"Extracted text: {text.strip()}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error in OCR text extraction: {str(e)}")
            raise
            
    def extract_amount(self, amount_region: np.ndarray) -> float:
        """Extract and parse amount from check"""
        try:
            text = self.extract_text(amount_region)
            logger.debug(f"Amount region text: {text}")
            
            matches = re.findall(self.amount_pattern, text)
            if matches:
                # Clean and convert to float
                amount_str = matches[0].replace('$', '').replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    logger.error(f"Failed to convert amount: {amount_str}")
                    return 0.0
            return 0.0
        except Exception as e:
            logger.error(f"Error extracting amount: {str(e)}")
            return 0.0
        
    def extract_date(self, date_region: np.ndarray) -> Optional[datetime]:
        """Extract and parse date from check"""
        try:
            text = self.extract_text(date_region)
            logger.debug(f"Date region text: {text}")
            
            matches = re.findall(self.date_pattern, text)
            if matches:
                date_str = matches[0]
                # Try different date formats
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
                           '%m/%d/%y', '%m-%d-%y', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            return None
        except Exception as e:
            logger.error(f"Error extracting date: {str(e)}")
            return None
        
    def extract_micr(self, micr_region: np.ndarray) -> Dict[str, str]:
        """Extract MICR code components"""
        try:
            # Use specific OCR config for MICR
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(micr_region, config=config)
            logger.debug(f"MICR region text: {text}")
            
            # Clean and parse MICR text
            micr_text = ''.join(filter(str.isdigit, text))
            
            if len(micr_text) >= 9:  # Minimum length for valid MICR
                return {
                    'bank_code': micr_text[:3],
                    'account_number': micr_text[3:-4],
                    'check_number': micr_text[-4:]
                }
            else:
                logger.warning(f"Invalid MICR length: {len(micr_text)}")
                return {
                    'bank_code': '',
                    'account_number': '',
                    'check_number': ''
                }
        except Exception as e:
            logger.error(f"Error extracting MICR: {str(e)}")
            return {
                'bank_code': '',
                'account_number': '',
                'check_number': ''
            } 