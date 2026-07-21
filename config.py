import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))


def _get_secret_key():
    key = os.environ.get("SECRET_KEY", "")
    if not key or key == "dev-secret-change-in-production":
        # Auto-generate and persist a key so sessions survive restarts
        key_file = os.path.join(basedir, ".secret_key")
        if os.path.exists(key_file):
            with open(key_file) as f:
                key = f.read().strip()
        else:
            key = secrets.token_hex(32)
            with open(key_file, "w") as f:
                f.write(key)
    return key


class Config:
    SECRET_KEY = _get_secret_key()

    db_uri = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "database", "pelarikenya.db"),
    )

    # If SQLite path is relative, make it absolute
    if db_uri.startswith("sqlite:///") and not db_uri.startswith("sqlite:////"):
        relative_path = db_uri.replace("sqlite:///", "")
        if not os.path.isabs(relative_path):
            db_uri = "sqlite:///" + os.path.join(basedir, relative_path)

    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ensure database directory exists
    db_dir = os.path.dirname(db_uri.replace("sqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
