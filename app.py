from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import Counter
from flask import render_template, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
)



app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "default_password")
db = SQLAlchemy(app)

# -------------------
# MODELS
# -------------------


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    subject = db.relationship("Subject", backref=db.backref("teachers", lazy=True))


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False , default="Anonymous")
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    teacher = db.relationship("Teacher", backref=db.backref("reviews", lazy=True))


with app.app_context():
    db.create_all()


# -------------------
# ROUTES
# -------------------


@app.route("/")
def index():
    subjects = Subject.query.all()
    return render_template("index.html", subjects=subjects)


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    teacher_id = request.form.get("teacher")
    rating = request.form.get("rating")
    review_text = request.form.get("review")
    if not name:
        name = "Anonymous"
    if not review_text:
        review_text = " "
    if not name or not teacher_id or not rating or not review_text:
        return redirect(url_for("index"))

    review = Review(
        user_name=name,
        teacher_id=int(teacher_id),
        rating=int(rating),
        review_text=review_text,
    )

    db.session.add(review)
    db.session.commit()

    return redirect(url_for("index"))


# -------------------
# ADMIN
# -------------------


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    subject_id = request.args.get("subject_id")
    teacher_id = request.args.get("teacher_id")

    subjects = Subject.query.order_by(Subject.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()

    # filtering logic
    reviews_query = Review.query

    if teacher_id:
        reviews_query = reviews_query.filter_by(teacher_id=int(teacher_id))
    elif subject_id:
        reviews_query = reviews_query.join(Teacher).filter(
            Teacher.subject_id == int(subject_id)
        )

    reviews = reviews_query.order_by(Review.created_at.desc()).all()

    return render_template(
        "admin.html",
        subjects=subjects,
        teachers=teachers,
        reviews=reviews,
        selected_subject=subject_id,
        selected_teacher=teacher_id,
    )


@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

    return render_template("admin_login.html")


@app.route("/admin/add-subject", methods=["POST"])
def add_subject():
    name = request.form.get("name")

    if name:
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/delete-subject/<int:id>")
def delete_subject(id):
    subject = Subject.query.get_or_404(id)

    # delete teachers + their reviews
    for teacher in subject.teachers:
        Review.query.filter_by(teacher_id=teacher.id).delete()
        db.session.delete(teacher)

    db.session.delete(subject)
    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/add-teacher", methods=["POST"])
def add_teacher():
    name = request.form.get("name")
    subject_id = request.form.get("subject_id")

    if name and subject_id:
        teacher = Teacher(name=name, subject_id=int(subject_id))
        db.session.add(teacher)
        db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/delete-teacher/<int:id>")
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    Review.query.filter_by(teacher_id=id).delete()
    db.session.delete(teacher)
    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/delete-review/<int:id>")
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/admin/review/<int:id>")
def view_review(id):
    review = Review.query.get_or_404(id)
    return render_template("review_detail.html", review=review)


from collections import Counter
from flask import render_template, redirect, url_for, session


@app.route("/admin/teacher/<int:teacher_id>")
def admin_teacher_detail(teacher_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    teacher = Teacher.query.get_or_404(teacher_id)
    reviews = (
        Review.query.filter_by(teacher_id=teacher.id).order_by(Review.id.desc()).all()
    )

    total_reviews = len(reviews)

    if total_reviews > 0:
        avg_rating = round(sum(review.rating for review in reviews) / total_reviews, 1)

        rating_counter = Counter(review.rating for review in reviews)
        rating_distribution = {
            5: rating_counter.get(5, 0),
            4: rating_counter.get(4, 0),
            3: rating_counter.get(3, 0),
            2: rating_counter.get(2, 0),
            1: rating_counter.get(1, 0),
        }
    else:
        avg_rating = 0
        take_again_percent = 0
        rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    max_count = max(rating_distribution.values()) if total_reviews > 0 else 1

    return render_template(
        "admin_teacher.html",
        teacher=teacher,
        reviews=reviews,
        total_reviews=total_reviews,
        avg_rating=avg_rating,
        rating_distribution=rating_distribution,
        max_count=max_count,
    )


# -------------------
# RUN
# -------------------

if __name__ == "__main__":
    app.run(debug=False)
