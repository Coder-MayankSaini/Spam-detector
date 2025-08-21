#!/usr/bin/env python3
"""
Quick setup script for PostgreSQL version
"""
import os
import shutil
import sys

def setup_postgresql_version():
    """Set up the project to use PostgreSQL instead of SQLite"""
    
    print("🔄 Setting up PostgreSQL version...")
    
    backend_dir = "Spam-backend"
    
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return False
    
    try:
        # Backup original app.py
        original_app = os.path.join(backend_dir, "app.py")
        postgresql_app = os.path.join(backend_dir, "app_postgresql.py")
        backup_app = os.path.join(backend_dir, "app_sqlite_backup.py")
        
        if os.path.exists(original_app) and not os.path.exists(backup_app):
            print("📋 Backing up original SQLite version...")
            shutil.copy2(original_app, backup_app)
        
        # Replace app.py with PostgreSQL version
        if os.path.exists(postgresql_app):
            print("🔄 Switching to PostgreSQL version...")
            shutil.copy2(postgresql_app, original_app)
        else:
            print("❌ PostgreSQL version not found!")
            return False
        
        print("✅ Successfully switched to PostgreSQL version!")
        print("📋 Original SQLite version backed up as app_sqlite_backup.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def revert_to_sqlite():
    """Revert back to SQLite version"""
    
    print("🔄 Reverting to SQLite version...")
    
    backend_dir = "Spam-backend"
    original_app = os.path.join(backend_dir, "app.py")
    backup_app = os.path.join(backend_dir, "app_sqlite_backup.py")
    
    try:
        if os.path.exists(backup_app):
            shutil.copy2(backup_app, original_app)
            print("✅ Successfully reverted to SQLite version!")
            return True
        else:
            print("❌ SQLite backup not found!")
            return False
            
    except Exception as e:
        print(f"❌ Revert failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🗄️ Database Version Switcher")
    print("=" * 40)
    
    print("1. Switch to PostgreSQL (for production)")
    print("2. Revert to SQLite (for development)")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == "1":
        if setup_postgresql_version():
            print("\n✅ PostgreSQL setup complete!")
            print("\nNext steps:")
            print("1. Set up Neon.tech database")
            print("2. Configure environment variables")
            print("3. Run: python migrate_to_postgresql.py")
            print("4. Deploy using DEPLOYMENT_GUIDE.md")
        else:
            print("\n❌ Setup failed!")
            
    elif choice == "2":
        if revert_to_sqlite():
            print("\n✅ Reverted to SQLite version!")
            print("You can now run the development version normally.")
        else:
            print("\n❌ Revert failed!")
            
    elif choice == "3":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
