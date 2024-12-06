import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
from typing import Union, List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.pdf']
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Noise reduction
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Deskew image
            coords = np.column_stack(np.where(denoised > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
                
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                denoised, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            logger.debug("Image preprocessing completed successfully")
            return rotated
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            return image
    
    def extract_regions(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract different regions from the check image using relative positioning"""
        try:
            height, width = image.shape[:2]
            
            # Define regions based on typical check layout
            regions = {
                # Amount is usually in the top right quadrant
                'amount': image[int(height*0.1):int(height*0.3),
                              int(width*0.65):int(width*0.95)],
                              
                # Date is usually in the top right corner
                'date': image[int(height*0.05):int(height*0.15),
                            int(width*0.7):int(width*0.95)],
                            
                # Signature is usually in the bottom right quadrant
                'signature': image[int(height*0.6):int(height*0.8),
                                 int(width*0.6):int(width*0.95)],
                                 
                # MICR is always at the bottom
                'micr': image[int(height*0.8):,
                            int(width*0.1):int(width*0.9)]
            }
            
            # Validate extracted regions
            for region_name, region in regions.items():
                if region.size == 0:
                    logger.warning(f"Empty region extracted: {region_name}")
                    regions[region_name] = np.zeros((100, 100), dtype=np.uint8)
            
            logger.debug("Regions extracted successfully")
            return regions
            
        except Exception as e:
            logger.error(f"Error extracting regions: {str(e)}")
            # Return empty regions if extraction fails
            return {
                'amount': np.zeros((100, 100), dtype=np.uint8),
                'date': np.zeros((100, 100), dtype=np.uint8),
                'signature': np.zeros((100, 100), dtype=np.uint8),
                'micr': np.zeros((100, 100), dtype=np.uint8)
            }
    
    def enhance_micr(self, micr_region: np.ndarray) -> np.ndarray:
        """Enhance MICR code region for better recognition"""
        try:
            # Convert to grayscale if needed
            if len(micr_region.shape) == 3:
                micr_region = cv2.cvtColor(micr_region, cv2.COLOR_BGR2GRAY)
            
            # Apply specific preprocessing for MICR
            # 1. Increase contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(micr_region)
            
            # 2. Remove noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # 3. Binarization
            enhanced = cv2.threshold(
                enhanced, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]
            
            # 4. Remove small noise
            kernel = np.ones((2,2), np.uint8)
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel)
            
            logger.debug("MICR region enhanced successfully")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing MICR region: {str(e)}")
            return micr_region