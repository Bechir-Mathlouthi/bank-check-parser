import pytest
import numpy as np
from app.core.check_parser import CheckParser
from app.core.image_processor import ImageProcessor
from app.core.ocr_engine import OCREngine
from app.core.fraud_detector import FraudDetector

@pytest.fixture
def check_parser():
    return CheckParser()

@pytest.fixture
def sample_check_image():
    # Create a sample check image for testing
    image = np.zeros((1000, 2000, 3), dtype=np.uint8)
    # Add some test patterns
    image[200:400, 1200:1800] = 255  # Amount region
    image[100:200, 1400:1800] = 255  # Date region
    image[600:800, 1200:1800] = 255  # Signature region
    image[800:1000, :] = 255  # MICR region
    return image.tobytes()

def test_check_parsing(check_parser, sample_check_image):
    # Test basic check parsing
    result = check_parser.parse_check(sample_check_image)
    
    assert isinstance(result, dict)
    assert 'amount_numeric' in result
    assert 'date' in result
    assert 'fraud_detected' in result
    assert 'fraud_confidence' in result

def test_fraud_detection(check_parser, sample_check_image):
    # Test fraud detection
    result = check_parser.parse_check(sample_check_image)
    
    assert isinstance(result['fraud_detected'], bool)
    assert 0 <= result['fraud_confidence'] <= 1

def test_invalid_image():
    parser = CheckParser()
    with pytest.raises(Exception):
        parser.parse_check(b'invalid image data') 