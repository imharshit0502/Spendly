from flask import Flask, render_template, g, request, redirect, url_for, flash, abort, session
from database import db
from database.db import get_db, init_db, seed_db
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'dev-secret-key-123'

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



@app.route("/setup-db")
def setup_db():
    init_db()
    seed_db()
    return "Database initialized and seeded successfully!"

# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([name, email, password, confirm_password]):
            flash("All fields are required")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match")
            return render_template("register.html")

        try:
            db.create_user(name, email, password)
            flash("Account created successfully!")
            return redirect(url_for("login"))
        except Exception:
            # Since we only have the UNIQUE constraint on email,
            # we can assume it's a duplicate email.
            flash("Email already registered")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!")
            return redirect(url_for("profile"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Hardcoded data for UI validation in Step 4
    context = {
        "user": {
            "name": "Alex Rivera",
            "email": "alex.rivera@example.com",
            "member_since": "January 2024"
        },
        "stats": {
            "total_spent": "1,240.50",
            "transaction_count": 42,
            "top_category": "Dining"
        },
        "transactions": [
            {"date": "2023-10-20", "desc": "Whole Foods Market", "cat": "Groceries", "amt": "-£45.20"},
            {"date": "2023-10-19", "desc": "Apple Store", "cat": "Shopping", "amt": "-£129.00"},
            {"date": "2023-10-18", "desc": "Starbucks Coffee", "cat": "Dining", "amt": "-£5.45"},
        ],
        "categories": [
            {"name": "Dining", "total": "£450.00", "percent": 36},
            {"name": "Groceries", "total": "£320.00", "percent": 25},
            {"name": "Transport", "total": "£210.00", "percent": 17},
        ]
    }
    return render_template("profile.html", **context)



@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
