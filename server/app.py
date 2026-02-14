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


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="customer")
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
            "name": self.name,
        }


class Dependent(db.Model):
    __tablename__ = "dependents"
    dependent_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    def to_dict(self):
        return {
            "dependent_id": self.dependent_id,
            "name": self.name,
            "user_id": self.user_id,
        }


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(
        email=data["email"],
        password=data["password"],
        name=data["name"],
        role="customer",
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict(), 201


@app.route("/dependents", methods=["POST"])
def create_dependent():
    name = request.form.get("name")
    user_id = request.form.get("user_id")
    new_dep = Dependent(name=name, user_id=int(user_id))
    db.session.add(new_dep)
    db.session.commit()
    return new_dep.to_dict(), 201


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return [user.to_dict() for user in users], 200


"""
@app.route("/test-query", methods=["GET"])
def test_query():
    try:
        users = User.query.all()
        dependents = Dependent.query.all()

        return {
            "users": [u.to_dict() for u in users],
            "dependents": [d.to_dict() for d in dependents]
        }

    except Exception as e:
        return {"error": str(e)}
"""

"""
@app.route("/test-insert")
def test_insert():
    try:
        # create a user
        new_user = User(
            email="testuser@email.com",
            password="hashedpassword",
            role="customer",
            name="Test User"
        )

        db.session.add(new_user)
        db.session.commit()

        # create a dependent linked to that user
        new_dependent = Dependent(
            name="Child One",
            user_id=new_user.user_id
        )

        db.session.add(new_dependent)
        db.session.commit()

        return {
            "user": new_user.to_dict(),
            "dependent": new_dependent.to_dict()
        }
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
"""


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
