"""
Database utility functions for PostgreSQL (Railway) deployment
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', 5432)
        }

    @contextmanager
    def get_db_connection(self):
        """Get database connection with context manager"""
        conn = None
        try:
            if self.database_url:
                # Use DATABASE_URL if available (for Railway, Heroku, etc.)
                conn = psycopg2.connect(self.database_url)
            else:
                # Use individual config parameters
                conn = psycopg2.connect(**self.db_config)

            conn.autocommit = False
            yield conn

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reset_token VARCHAR(255),
                        reset_token_expires TIMESTAMP
                    )
                """)

                # Create analysis_history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        email_text TEXT NOT NULL,
                        is_spam BOOLEAN NOT NULL,
                        confidence FLOAT NOT NULL,
                        analysis_type VARCHAR(50) DEFAULT 'text',
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45)
                    )
                """)

                # Create contact_messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contact_messages (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_analysis_history_timestamp ON analysis_history(timestamp)
                """)

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def create_user(self, email, password_hash):
        """Create a new user"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                    (email, password_hash)
                )
                user_id = cursor.fetchone()[0]
                conn.commit()
                return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def save_analysis(self, user_id, email_text, is_spam, confidence, analysis_type='text', ip_address=None):
        """Save analysis to history"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analysis_history (user_id, email_text, is_spam, confidence, analysis_type, ip_address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, email_text, is_spam, confidence, analysis_type, ip_address))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise

    def get_user_history(self, user_id, limit=50):
        """Get user's analysis history"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT email_text, is_spam, confidence, analysis_type, timestamp
                    FROM analysis_history
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, limit))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []

    def get_user_stats(self, user_id):
        """Get user statistics"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_analyzed,
                        COUNT(CASE WHEN is_spam THEN 1 END) as spam_detected,
                        COUNT(CASE WHEN NOT is_spam THEN 1 END) as ham_detected,
                        AVG(confidence) as avg_confidence
                    FROM analysis_history
                    WHERE user_id = %s
                """, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                'total_analyzed': 0,
                'spam_detected': 0,
                'ham_detected': 0,
                'avg_confidence': 0.0
            }

    def save_contact_message(self, name, email, message):
        """Save contact form message"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO contact_messages (name, email, message)
                    VALUES (%s, %s, %s)
                """, (name, email, message))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving contact message: {e}")
            raise

    def update_reset_token(self, email, token, expires_at):
        """Update password reset token"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET reset_token = %s, reset_token_expires = %s
                    WHERE email = %s
                """, (token, expires_at, email))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating reset token: {e}")
            return False

    def get_user_by_reset_token(self, token):
        """Get user by reset token"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT * FROM users
                    WHERE reset_token = %s AND reset_token_expires > %s
                """, (token, datetime.now()))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by reset token: {e}")
            return None

    def update_password(self, user_id, new_password_hash):
        """Update user password and clear reset token"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET password_hash = %s, reset_token = NULL, reset_token_expires = NULL
                    WHERE id = %s
                """, (new_password_hash, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
