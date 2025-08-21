"""
Simplified database manager that works without PostgreSQL
Uses in-memory storage for development/testing
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os

logger = logging.getLogger(__name__)

class InMemoryDatabaseManager:
    """Simple in-memory database for development"""
    
    def __init__(self):
        self.users = {}  # id -> user_data
        self.analysis_history = []  # list of analysis records
        self.contact_messages = []  # list of contact messages
        self.next_user_id = 1
        self.data_file = 'simple_db.json'
        self.load_data()
    
    def load_data(self):
        """Load data from file if it exists"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.analysis_history = data.get('analysis_history', [])
                    self.contact_messages = data.get('contact_messages', [])
                    self.next_user_id = data.get('next_user_id', 1)
                logger.info("Data loaded from simple_db.json")
        except Exception as e:
            logger.warning(f"Could not load data: {e}")
    
    def save_data(self):
        """Save data to file"""
        try:
            data = {
                'users': self.users,
                'analysis_history': self.analysis_history,
                'contact_messages': self.contact_messages,
                'next_user_id': self.next_user_id
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Could not save data: {e}")
    
    def init_database(self):
        """Initialize database (no-op for in-memory)"""
        logger.info("Using in-memory database")
        return True
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user_id, user_data in self.users.items():
            if user_data['email'] == email:
                return {'id': int(user_id), **user_data}
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        user_data = self.users.get(str(user_id))
        if user_data:
            return {'id': user_id, **user_data}
        return None
    
    def create_user(self, email: str, password_hash: str) -> int:
        """Create a new user"""
        user_id = self.next_user_id
        self.next_user_id += 1
        
        self.users[str(user_id)] = {
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now(),
            'reset_token': None,
            'reset_token_expires': None
        }
        
        self.save_data()
        return user_id
    
    def save_analysis(self, user_id: int, email_text: str, is_spam: bool, 
                     confidence: float, analysis_type: str = 'text', 
                     ip_address: Optional[str] = None):
        """Save analysis to history"""
        self.analysis_history.append({
            'user_id': user_id,
            'email_text': email_text,
            'is_spam': is_spam,
            'confidence': confidence,
            'analysis_type': analysis_type,
            'timestamp': datetime.now(),
            'ip_address': ip_address
        })
        self.save_data()
    
    def get_user_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's analysis history"""
        user_history = [
            h for h in self.analysis_history 
            if h['user_id'] == user_id
        ]
        
        # Sort by timestamp (newest first)
        user_history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return user_history[:limit]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        user_history = [
            h for h in self.analysis_history 
            if h['user_id'] == user_id
        ]
        
        if not user_history:
            return {
                'total_analyzed': 0,
                'spam_detected': 0,
                'ham_detected': 0,
                'avg_confidence': 0.0
            }
        
        spam_count = sum(1 for h in user_history if h['is_spam'])
        ham_count = len(user_history) - spam_count
        avg_confidence = sum(h['confidence'] for h in user_history) / len(user_history)
        
        return {
            'total_analyzed': len(user_history),
            'spam_detected': spam_count,
            'ham_detected': ham_count,
            'avg_confidence': avg_confidence
        }
    
    def save_contact_message(self, name: str, email: str, message: str):
        """Save contact form message"""
        self.contact_messages.append({
            'name': name,
            'email': email,
            'message': message,
            'created_at': datetime.now()
        })
        self.save_data()
    
    def update_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Update password reset token"""
        for user_id, user_data in self.users.items():
            if user_data['email'] == email:
                user_data['reset_token'] = token
                user_data['reset_token_expires'] = expires_at
                self.save_data()
                return True
        return False
    
    def get_user_by_reset_token(self, token: str) -> Optional[Dict]:
        """Get user by reset token"""
        for user_id, user_data in self.users.items():
            if (user_data.get('reset_token') == token and 
                user_data.get('reset_token_expires') and
                user_data['reset_token_expires'] > datetime.now()):
                return {'id': int(user_id), **user_data}
        return None
    
    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """Update user password and clear reset token"""
        user_data = self.users.get(str(user_id))
        if user_data:
            user_data['password_hash'] = new_password_hash
            user_data['reset_token'] = None
            user_data['reset_token_expires'] = None
            self.save_data()
            return True
        return False

# Global database manager instance
db_manager = InMemoryDatabaseManager()
