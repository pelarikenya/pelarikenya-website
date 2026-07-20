import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

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
