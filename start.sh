#!/bin/bash
# Create tables if no migration versions exist (first deploy)
if [ ! "$(ls -A migrations/versions/ 2>/dev/null)" ]; then
    echo "No migrations found, creating tables..."
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Tables created')
"
    # Generate initial migration
    flask db migrate -m 'initial migration'
    flask db upgrade
else
    echo "Running migrations..."
    flask db upgrade
fi

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
