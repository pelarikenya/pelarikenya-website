import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "database", "pelarikenya.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ensure database directory exists
    db_dir = os.path.join(basedir, "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
