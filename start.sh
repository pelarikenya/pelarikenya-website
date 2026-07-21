#!/bin/bash
# Run migrations before starting the app
flask db upgrade

# Create admin if not exists
python -c "
from app import app, db
from models import User
with app.app_context():
    if not User.query.first():
        admin = User(name='Akbar', email='admin@pelarikenya.my.id', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin created')
"

# Start gunicorn
exec gunicorn app:app --bind 0.0.0.0:5000 --workers 4 --timeout 120
