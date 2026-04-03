# RateMyDC

A student review platform for Dubai College teachers.

RateMyDC gives students a structured way to submit feedback on teachers, and gives administrators a single place to analyse and browse all reviews.

## Features

**Student reviews** — submit ratings and written feedback, with optional anonymous posting.

**Teacher insights** — average ratings, review distribution, and dedicated teacher pages.

**Search and navigation** — search by teacher name or filter by subject.

**Admin panel** — password-protected panel with sorting, filtering, and per-teacher analytics.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | SQLAlchemy, PostgreSQL |
| Frontend | HTML, CSS (custom styling), Jinja2 |

## Setup

1. Clone the repository
```bash
git clone https://github.com/colmali-prog/ratemydc.git
cd ratemydc
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file
```env
SECRET_KEY=your_secret_key
```

5. Run the app
```bash
flask run
```

## Project structure
```
ratemydc/
├── app.py
├── instance/          # database (git-ignored)
├── static/
├── templates/
├── .env               # git-ignored
└── requirements.txt
```

## Security

- No sensitive data is stored in the repository
- `.env`, database files, and cache files are excluded via `.gitignore`
- Admin access is password protected

## Planned improvements

- AI-generated summary of teacher reviews
- More granular rating categories
- User accounts and authentication
- Improved mobile responsiveness

## Disclaimer

> This project is intended for internal use within Dubai College. All reviews are user-generated and reflect personal opinions only.

## Author

Colm Ali 
