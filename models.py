from datetime import datetime, timezone

from extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Contact {self.name} — {self.email}>"


class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    excerpt = db.Column(db.String(300), nullable=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="general")
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Blog {self.title}>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False, default="bi-robot")
    category = db.Column(db.String(50), nullable=False, default="web")
    tech_stack = db.Column(db.String(300), nullable=False)
    github_url = db.Column(db.String(300), nullable=True)
    demo_url = db.Column(db.String(300), nullable=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def get_tech_list(self):
        return [t.strip() for t in self.tech_stack.split(",") if t.strip()]

    def __repr__(self):
        return f"<Project {self.title}>"
