import re
from datetime import datetime, timezone

from flask import Flask, render_template, request, flash, redirect, url_for

from config import Config
from extensions import db
from models import Contact, Blog


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


def generate_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug


# -------------------------------------------
# Public Routes
# -------------------------------------------


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/blog")
def blog():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", None)
    query = Blog.query.filter_by(is_published=True)

    if category:
        query = query.filter_by(category=category)

    posts = query.order_by(Blog.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    categories = db.session.query(Blog.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template(
        "blog.html", posts=posts, categories=categories, current_category=category
    )


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("blog_detail.html", post=post)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Nama, email, dan pesan wajib diisi.", "danger")
            return redirect(url_for("contact"))

        entry = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(entry)
        db.session.commit()

        flash("Pesan berhasil dikirim! Terima kasih sudah menghubungi saya.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# -------------------------------------------
# Admin Routes — Blog
# -------------------------------------------


@app.route("/admin/blog")
def admin_blog_list():
    posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template("admin/blog_list.html", posts=posts)


@app.route("/admin/blog/new", methods=["GET", "POST"])
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
def admin_blog_edit(post_id):
    post = Blog.query.get_or_404(post_id)

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
def admin_blog_delete(post_id):
    post = Blog.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    flash("Artikel berhasil dihapus!", "success")
    return redirect(url_for("admin_blog_list"))


# -------------------------------------------
# Error Handlers
# -------------------------------------------


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
