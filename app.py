import os
import re
import logging
from datetime import datetime, timezone
from functools import wraps

import bleach
import markdown
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, flash, redirect, url_for, abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from markupsafe import Markup

from config import Config
from extensions import db, csrf, login_manager, migrate
from models import Contact, Blog, Project, User

load_dotenv()


ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    "h2", "h3", "h4", "h5", "h6",
    "p", "br", "pre", "code",
    "blockquote", "ul", "ol", "li",
    "img", "hr", "table", "thead", "tbody", "tr", "th", "td",
    "a", "strong", "em", "span", "div",
]

ALLOWED_ATTRIBUTES = {
    **bleach.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
    "span": ["class"],
    "div": ["class"],
}


def render_markdown(text):
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br", "sane_lists", "smarty"],
    )
    return Markup(sanitize_html(html))


def sanitize_html(raw_html):
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


def generate_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Pelarikenya website started")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_now():
        from datetime import datetime, timezone
        return {"now": datetime.now(timezone.utc)}

    with app.app_context():
        db.create_all()

    register_routes(app)
    register_error_handlers(app)

    return app


def register_routes(app):

    # -------------------------------------------
    # Public Routes
    # -------------------------------------------

    @app.route("/")
    def home():
        featured_projects = Project.query.filter_by(is_featured=True).order_by(
            Project.sort_order.asc()
        ).limit(3).all()
        return render_template("home.html", featured_projects=featured_projects)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/projects")
    def projects():
        category = request.args.get("category", None)
        query = Project.query

        if category:
            query = query.filter_by(category=category)

        all_projects = query.order_by(Project.sort_order.asc()).all()
        categories = db.session.query(Project.category).distinct().all()
        categories = [c[0] for c in categories]

        return render_template(
            "projects.html",
            projects=all_projects,
            categories=categories,
            current_category=category,
        )

    @app.route("/blog")
    def blog():
        page = request.args.get("page", 1, type=int)
        category = request.args.get("category", None)
        search = request.args.get("q", "").strip()
        query = Blog.query.filter_by(is_published=True)

        if category:
            query = query.filter_by(category=category)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Blog.title.ilike(search_term),
                    Blog.excerpt.ilike(search_term),
                    Blog.content.ilike(search_term),
                )
            )

        posts = query.order_by(Blog.created_at.desc()).paginate(
            page=page, per_page=6, error_out=False
        )
        categories = db.session.query(Blog.category).distinct().all()
        categories = [c[0] for c in categories]

        return render_template(
            "blog.html",
            posts=posts,
            categories=categories,
            current_category=category,
            search_query=search,
        )

    @app.route("/blog/<slug>")
    def blog_detail(slug):
        post = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()
        safe_content = render_markdown(post.content)
        return render_template("blog_detail.html", post=post, safe_content=safe_content)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            # Honeypot check — bots fill this, humans don't
            if request.form.get("website"):
                flash("Pesan berhasil dikirim!", "success")
                return redirect(url_for("contact"))

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            subject = request.form.get("subject", "").strip()
            message = request.form.get("message", "").strip()

            if not name or not email or not message:
                flash("Nama, email, dan pesan wajib diisi.", "danger")
                return redirect(url_for("contact"))

            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, email):
                flash("Format email tidak valid.", "danger")
                return redirect(url_for("contact"))

            entry = Contact(name=name, email=email, subject=subject, message=message)
            db.session.add(entry)
            db.session.commit()

            flash("Pesan berhasil dikirim! Terima kasih sudah menghubungi saya.", "success")
            return redirect(url_for("contact"))

        return render_template("contact.html")

    # -------------------------------------------
    # Admin Routes — Auth
    # -------------------------------------------

    @app.route("/admin/register", methods=["GET", "POST"])
    def admin_register():
        # Only accessible when no admin user exists yet
        if User.query.first():
            abort(404)

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            if not name or not email or not password:
                flash("Semua field wajib diisi.", "danger")
                return redirect(url_for("admin_register"))

            if len(password) < 6:
                flash("Password minimal 6 karakter.", "danger")
                return redirect(url_for("admin_register"))

            if password != confirm:
                flash("Konfirmasi password tidak cocok.", "danger")
                return redirect(url_for("admin_register"))

            if User.query.filter_by(email=email).first():
                flash("Email sudah terdaftar.", "danger")
                return redirect(url_for("admin_register"))

            user = User(name=name, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash("Akun admin berhasil dibuat!", "success")
            return redirect(url_for("admin_blog_list"))

        return render_template("admin/register.html")

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_blog_list"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                flash(f"Selamat datang, {user.name}!", "success")
                return redirect(url_for("admin_blog_list"))

            flash("Email atau password salah.", "danger")
        return render_template("admin/login.html")

    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        logout_user()
        return redirect(url_for("home"))

    # -------------------------------------------
    # Admin Routes — Blog
    # -------------------------------------------

    @app.route("/admin/blog")
    @admin_required
    def admin_blog_list():
        posts = Blog.query.order_by(Blog.created_at.desc()).all()
        return render_template("admin/blog_list.html", posts=posts)

    @app.route("/admin/blog/new", methods=["GET", "POST"])
    @admin_required
    def admin_blog_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            excerpt = request.form.get("excerpt", "").strip()
            content = request.form.get("content", "").strip()
            category = request.form.get("category", "general").strip()
            is_published = request.form.get("is_published") == "on"

            if not title or not content:
                flash("Judul dan konten wajib diisi.", "danger")
                return redirect(url_for("admin_blog_new"))

            slug = generate_slug(title)

            existing = Blog.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{int(datetime.now(timezone.utc).timestamp())}"

            post = Blog(
                title=title,
                slug=slug,
                excerpt=excerpt,
                content=content,
                category=category,
                is_published=is_published,
            )
            db.session.add(post)
            db.session.commit()

            flash("Artikel berhasil dibuat!", "success")
            return redirect(url_for("admin_blog_list"))

        return render_template("admin/blog_form.html", post=None)

    @app.route("/admin/blog/<int:post_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_blog_edit(post_id):
        post = db.get_or_404(Blog, post_id)

        if request.method == "POST":
            post.title = request.form.get("title", "").strip()
            post.excerpt = request.form.get("excerpt", "").strip()
            post.content = request.form.get("content", "").strip()
            post.category = request.form.get("category", "general").strip()
            post.is_published = request.form.get("is_published") == "on"

            if not post.title or not post.content:
                flash("Judul dan konten wajib diisi.", "danger")
                return redirect(url_for("admin_blog_edit", post_id=post_id))

            new_slug = generate_slug(post.title)
            if new_slug != post.slug:
                existing = Blog.query.filter_by(slug=new_slug).first()
                if existing:
                    new_slug = f"{new_slug}-{int(datetime.now(timezone.utc).timestamp())}"
                post.slug = new_slug

            db.session.commit()

            flash("Artikel berhasil diupdate!", "success")
            return redirect(url_for("admin_blog_list"))

        return render_template("admin/blog_form.html", post=post)

    @app.route("/admin/blog/<int:post_id>/delete", methods=["POST"])
    @admin_required
    def admin_blog_delete(post_id):
        post = db.get_or_404(Blog, post_id)
        db.session.delete(post)
        db.session.commit()

        flash("Artikel berhasil dihapus!", "success")
        return redirect(url_for("admin_blog_list"))

    # -------------------------------------------
    # Admin Routes — Projects
    # -------------------------------------------

    @app.route("/admin/projects")
    @admin_required
    def admin_project_list():
        projects = Project.query.order_by(Project.sort_order.asc()).all()
        return render_template("admin/project_list.html", projects=projects)

    @app.route("/admin/projects/new", methods=["GET", "POST"])
    @admin_required
    def admin_project_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            icon = request.form.get("icon", "bi-robot").strip()
            category = request.form.get("category", "web").strip()
            tech_stack = request.form.get("tech_stack", "").strip()
            github_url = request.form.get("github_url", "").strip()
            demo_url = request.form.get("demo_url", "").strip()
            is_featured = request.form.get("is_featured") == "on"
            sort_order = request.form.get("sort_order", 0, type=int)

            if not title or not description or not tech_stack:
                flash("Judul, deskripsi, dan tech stack wajib diisi.", "danger")
                return redirect(url_for("admin_project_new"))

            project = Project(
                title=title,
                description=description,
                icon=icon,
                category=category,
                tech_stack=tech_stack,
                github_url=github_url or None,
                demo_url=demo_url or None,
                is_featured=is_featured,
                sort_order=sort_order,
            )
            db.session.add(project)
            db.session.commit()

            flash("Project berhasil dibuat!", "success")
            return redirect(url_for("admin_project_list"))

        return render_template("admin/project_form.html", project=None)

    @app.route("/admin/projects/<int:project_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_project_edit(project_id):
        project = db.get_or_404(Project, project_id)

        if request.method == "POST":
            project.title = request.form.get("title", "").strip()
            project.description = request.form.get("description", "").strip()
            project.icon = request.form.get("icon", "bi-robot").strip()
            project.category = request.form.get("category", "web").strip()
            project.tech_stack = request.form.get("tech_stack", "").strip()
            project.github_url = request.form.get("github_url", "").strip() or None
            project.demo_url = request.form.get("demo_url", "").strip() or None
            project.is_featured = request.form.get("is_featured") == "on"
            project.sort_order = request.form.get("sort_order", 0, type=int)

            if not project.title or not project.description or not project.tech_stack:
                flash("Judul, deskripsi, dan tech stack wajib diisi.", "danger")
                return redirect(url_for("admin_project_edit", project_id=project_id))

            db.session.commit()

            flash("Project berhasil diupdate!", "success")
            return redirect(url_for("admin_project_list"))

        return render_template("admin/project_form.html", project=project)

    @app.route("/admin/projects/<int:project_id>/delete", methods=["POST"])
    @admin_required
    def admin_project_delete(project_id):
        project = db.get_or_404(Project, project_id)
        db.session.delete(project)
        db.session.commit()

        flash("Project berhasil dihapus!", "success")
        return redirect(url_for("admin_project_list"))

    # -------------------------------------------
    # Admin Routes — Contacts
    # -------------------------------------------

    @app.route("/admin/contacts")
    @admin_required
    def admin_contact_list():
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        return render_template("admin/contact_list.html", contacts=contacts)

    @app.route("/admin/contacts/<int:contact_id>")
    @admin_required
    def admin_contact_detail(contact_id):
        contact = db.get_or_404(Contact, contact_id)
        return render_template("admin/contact_detail.html", contact=contact)

    @app.route("/admin/contacts/<int:contact_id>/delete", methods=["POST"])
    @admin_required
    def admin_contact_delete(contact_id):
        contact = db.get_or_404(Contact, contact_id)
        db.session.delete(contact)
        db.session.commit()

        flash("Pesan berhasil dihapus!", "success")
        return redirect(url_for("admin_contact_list"))


def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
