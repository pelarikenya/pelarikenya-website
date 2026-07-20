# Pelarikenya — Portfolio Website

Premium personal portfolio website for **Akbar Maulana** — AI Developer, Full Stack Developer, and Runner.

**Live:** [pelarikenya.my.id](https://pelarikenya.my.id)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.14, Flask |
| Frontend | HTML5, Bootstrap 5, CSS3, JavaScript (Vanilla) |
| Database | SQLite (development), PostgreSQL (production) |
| Font | Google Fonts — Poppins |
| Icons | Bootstrap Icons |
| Deployment | Docker, Render |

## Features

- **Home** — Hero section, tech stack, about preview, featured projects, CTA
- **About** — Biography, skills grid, timeline, certificates
- **Projects** — Grid layout with category filter and search
- **Blog** — Dynamic articles with pagination and category filter
- **Contact** — Functional form with database storage
- **Admin Panel** — Blog CRUD at `/admin/blog`
- **Responsive** — Desktop, laptop, tablet, mobile
- **Animations** — Scroll-triggered fade-in and slide-up effects

## Project Structure

```
pelarikenya-website/
├── app.py                  # Flask application
├── config.py               # Configuration
├── extensions.py           # Flask extensions (SQLAlchemy)
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── database/               # SQLite database (auto-created)
├── static/
│   ├── css/style.css       # Design system & styles
│   ├── js/script.js        # Navbar, animations, filtering
│   └── img/                # Images
│       ├── profile.jpg
│       └── icons/
└── templates/
    ├── base.html           # Master template
    ├── home.html
    ├── about.html
    ├── projects.html
    ├── blog.html
    ├── blog_detail.html
    ├── contact.html
    ├── 404.html
    ├── partials/
    │   ├── navbar.html
    │   └── footer.html
    └── admin/
        ├── base.html
        ├── blog_list.html
        └── blog_form.html
```

## Getting Started

### Prerequisites

- Python 3.14+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/pelarikenya/pelarikenya-website.git
cd pelarikenya-website

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-change-in-production` | Flask secret key |
| `DATABASE_URL` | `sqlite:///database/pelarikenya.db` | Database URI |

### Run the App

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Admin Panel

Open [http://127.0.0.1:5000/admin/blog](http://127.0.0.1:5000/admin/blog) to manage blog posts.

## Routes

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/about` | About page |
| `/projects` | Projects page |
| `/blog` | Blog listing |
| `/blog/<slug>` | Blog article detail |
| `/contact` | Contact form |
| `/admin/blog` | Admin — blog management |
| `/admin/blog/new` | Admin — create post |
| `/admin/blog/<id>/edit` | Admin — edit post |

## Database Schema

### contacts

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String(100) | Sender name |
| email | String(120) | Sender email |
| subject | String(200) | Message subject |
| message | Text | Message content |
| created_at | DateTime | Timestamp (UTC) |

### blogs

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String(200) | Article title |
| slug | String(200) | URL-friendly slug |
| excerpt | String(300) | Short summary |
| content | Text | Article content |
| category | String(50) | Category (default: general) |
| is_published | Boolean | Published status |
| created_at | DateTime | Created timestamp |
| updated_at | DateTime | Last updated timestamp |

## Design System

- **Color Primary:** `#2563EB`
- **Color Secondary:** `#0F172A`
- **Color Accent:** `#38BDF8`
- **Font:** Poppins (300-800)
- **Border Radius:** `0.375rem` — `1.5rem`
- **Shadows:** Soft, card, hover variants

## License

MIT License. Built by [Akbar Maulana](https://github.com/pelarikenya).
