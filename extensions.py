from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = "admin_login"
login_manager.login_message = "Silakan login terlebih dahulu."
login_manager.login_message_category = "warning"
