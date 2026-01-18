"""Script to send test notification to admin users"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')
if not DATABASE_URI:
    print("❌ DATABASE_URI not found in .env")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Find admin users (role_id = 1 typically is Admin)
    result = session.execute(text("""
        SELECT u.id, u.username, u.full_name, r.name as role_name
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
        WHERE r.name = 'Admin'
    """))
    
    admin_users = result.fetchall()
    
    if not admin_users:
        print("❌ No admin users found")
        sys.exit(1)
    
    print(f"📋 Found {len(admin_users)} admin user(s):")
    for user in admin_users:
        print(f"   - {user.full_name} (@{user.username}) - Role: {user.role_name}")
    
    # Create test notifications for each admin
    for user in admin_users:
        session.execute(text("""
            INSERT INTO notifications (user_id, title, message, type, link, is_read, created_at)
            VALUES (:user_id, :title, :message, :type, :link, 0, :created_at)
        """), {
            'user_id': user.id,
            'title': 'Alo Vũ à em',
            'message': 'Đây là thông báo test được gửi lúc ' + datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
            'type': 'INFO',
            'link': '/profile',
            'created_at': datetime.now()
        })
    
    session.commit()
    print(f"✅ Successfully sent test notification to {len(admin_users)} admin(s)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    session.rollback()
finally:
    session.close()
