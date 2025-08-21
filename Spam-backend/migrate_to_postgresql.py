"""
Migration script to transfer data from SQLite to PostgreSQL (Neon.tech)
Run this script to migrate your existing SQLite data to the new PostgreSQL database
"""
import sqlite3
import os
import json
from dotenv import load_dotenv
from database import db_manager
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_sqlite_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""
    
    sqlite_db_path = 'emails.db'  # Path to your existing SQLite database
    
    if not os.path.exists(sqlite_db_path):
        logger.error(f"SQLite database not found at {sqlite_db_path}")
        return False
    
    try:
        # Initialize PostgreSQL database
        logger.info("Initializing PostgreSQL database...")
        db_manager.init_database()
        
        # Connect to SQLite database
        logger.info("Connecting to SQLite database...")
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Migrate users table
        logger.info("Migrating users...")
        try:
            sqlite_cursor.execute("SELECT * FROM users")
            users = sqlite_cursor.fetchall()
            
            user_id_mapping = {}  # Map old SQLite IDs to new PostgreSQL IDs
            
            for user in users:
                # Check if user already exists in PostgreSQL
                existing_user = db_manager.get_user_by_email(user['email'])
                
                if existing_user:
                    logger.info(f"User {user['email']} already exists, skipping...")
                    user_id_mapping[user['id']] = existing_user['id']
                else:
                    # Create user in PostgreSQL
                    new_user_id = db_manager.create_user(user['email'], user['password_hash'])
                    user_id_mapping[user['id']] = new_user_id
                    logger.info(f"Migrated user: {user['email']}")
            
            logger.info(f"Migrated {len(users)} users")
            
        except sqlite3.OperationalError as e:
            logger.warning(f"Users table migration failed: {e}")
        
        # Migrate analysis_history table
        logger.info("Migrating analysis history...")
        try:
            sqlite_cursor.execute("SELECT * FROM analysis_history")
            analyses = sqlite_cursor.fetchall()
            
            migrated_count = 0
            for analysis in analyses:
                # Map old user_id to new user_id
                old_user_id = analysis['user_id']
                new_user_id = user_id_mapping.get(old_user_id)
                
                if new_user_id:
                    try:
                        db_manager.save_analysis(
                            user_id=new_user_id,
                            email_text=analysis['email_text'],
                            is_spam=bool(analysis['is_spam']),
                            confidence=float(analysis['confidence']),
                            analysis_type=analysis.get('analysis_type', 'text'),
                            ip_address=analysis.get('ip_address')
                        )
                        migrated_count += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate analysis record: {e}")
                else:
                    logger.warning(f"Skipping analysis record - user_id {old_user_id} not found")
            
            logger.info(f"Migrated {migrated_count} analysis records")
            
        except sqlite3.OperationalError as e:
            logger.warning(f"Analysis history migration failed: {e}")
        
        # Migrate contact_messages table
        logger.info("Migrating contact messages...")
        try:
            sqlite_cursor.execute("SELECT * FROM contact_messages")
            messages = sqlite_cursor.fetchall()
            
            migrated_count = 0
            for message in messages:
                try:
                    db_manager.save_contact_message(
                        name=message['name'],
                        email=message['email'],
                        message=message['message']
                    )
                    migrated_count += 1
                except Exception as e:
                    logger.error(f"Failed to migrate contact message: {e}")
            
            logger.info(f"Migrated {migrated_count} contact messages")
            
        except sqlite3.OperationalError as e:
            logger.warning(f"Contact messages migration failed: {e}")
        
        sqlite_conn.close()
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        logger.info("Verifying migration...")
        
        # Test database connection
        with db_manager.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_history")
            analysis_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contact_messages")
            contact_count = cursor.fetchone()[0]
            
            logger.info(f"PostgreSQL database contains:")
            logger.info(f"  - Users: {user_count}")
            logger.info(f"  - Analysis records: {analysis_count}")
            logger.info(f"  - Contact messages: {contact_count}")
            
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing if no existing data to migrate"""
    try:
        logger.info("Creating sample data for testing...")
        
        # Create a test user
        import bcrypt
        password_hash = bcrypt.hashpw("testpass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = db_manager.create_user("test@example.com", password_hash)
        
        # Create sample analysis records
        sample_analyses = [
            ("Congratulations! You've won $1000! Click here now!", True, 0.95, "text"),
            ("Meeting scheduled for tomorrow at 2 PM", False, 0.85, "text"),
            ("Get rich quick! Make money fast!", True, 0.92, "text"),
            ("Please review the attached document", False, 0.78, "text"),
            ("Limited time offer! Act now!", True, 0.88, "image")
        ]
        
        for email_text, is_spam, confidence, analysis_type in sample_analyses:
            db_manager.save_analysis(user_id, email_text, is_spam, confidence, analysis_type)
        
        # Create a sample contact message
        db_manager.save_contact_message(
            "Test User", 
            "test@example.com", 
            "This is a test contact message."
        )
        
        logger.info("Sample data created successfully!")
        logger.info("Test user credentials: test@example.com / testpass123")
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")

if __name__ == "__main__":
    print("🔄 SQLite to PostgreSQL Migration Tool")
    print("=" * 50)
    
    # Check if we have the required environment variables
    if not os.getenv('DATABASE_URL') and not all([
        os.getenv('DB_HOST'), 
        os.getenv('DB_NAME'), 
        os.getenv('DB_USER'), 
        os.getenv('DB_PASSWORD')
    ]):
        print("❌ PostgreSQL connection details not found!")
        print("Please set up your environment variables:")
        print("  - DATABASE_URL (or individual DB_* variables)")
        print("  - Check your .env file")
        exit(1)
    
    print("1. Migrate existing SQLite data")
    print("2. Create sample data for testing")
    print("3. Verify migration")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == "1":
        if migrate_sqlite_to_postgresql():
            verify_migration()
        else:
            print("❌ Migration failed!")
            
    elif choice == "2":
        create_sample_data()
        verify_migration()
        
    elif choice == "3":
        verify_migration()
        
    else:
        print("Invalid choice!")
    
    print("\n✅ Migration tool completed!")
