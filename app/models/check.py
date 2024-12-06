from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from ..database import Base

class Check(Base):
    __tablename__ = 'checks'
    
    id = Column(Integer, primary_key=True)
    check_number = Column(String(50), nullable=False)
    amount_numeric = Column(Float, nullable=False, default=0.0)
    date = Column(String(20))
    bank_code = Column(String(20))
    account_number = Column(String(50))
    signature_verified = Column(Boolean, default=False)
    fraud_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        # Generate a random check number if none is provided or if it's empty
        if not kwargs.get('check_number'):
            kwargs['check_number'] = f"CHK-{str(uuid.uuid4())[:8]}"
        super().__init__(**kwargs)
    
    def to_dict(self):
        """Convert to dictionary with JSON serializable types"""
        return {
            'id': self.id,
            'check_number': str(self.check_number) if self.check_number else '',
            'amount_numeric': float(self.amount_numeric) if self.amount_numeric else 0.0,
            'date': str(self.date) if self.date else '',
            'bank_code': str(self.bank_code) if self.bank_code else '',
            'account_number': str(self.account_number) if self.account_number else '',
            'signature_verified': bool(self.signature_verified),
            'fraud_detected': bool(self.fraud_detected),
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 