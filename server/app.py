from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test-db")
def db_test():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "<p>Database connection successful</p>"
    except Exception as e:
        return f"<p>Database connection failed: {str(e)}</p>"


@app.route("/users", methods=["GET"])
def get_users():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users;"))
        return [dict(row._mapping) for row in result]


@app.route("/dependents", methods=["GET"])
def get_dependents():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM dependents;"))
        return [dict(row._mapping) for row in result]


@app.route("/service", methods=["GET"])
def get_service():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM service;"))
        return [dict(row._mapping) for row in result]


@app.route("/appointments", methods=["GET"])
def get_appointments():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM appointments;"))
        return [dict(row._mapping) for row in result]


@app.route("/appointment-service", methods=["GET"])
def get_appointment_service():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM appointment_service;"))
        return [dict(row._mapping) for row in result]


@app.route("/reviews", methods=["GET"])
def get_reviews():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM reviews;"))
        return [dict(row._mapping) for row in result]


if __name__ == "__main__":
    app.run(debug=True)
