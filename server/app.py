from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or "sqlite:///dev.db"
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
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    def to_dict(self):
        return {
            "dependent_id": self.dependent_id,
            "name": self.name,
            "user_id": self.user_id,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    staff_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    time_booked = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)  

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "customer_id": self.customer_id,
            "staff_id": self.staff_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "time_booked": self.time_booked.isoformat(),
            "service_id": self.service_id,
        }


class Service(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "price": self.price,
        }


class AppointmentService(db.Model):
    __tablename__ = "appointment_services"
    appointment_id = db.Column(
        db.Integer, db.ForeignKey("appointments.appointment_id", ondelete="CASCADE"), nullable=False
    )
    service_id = db.Column(
        db.Integer, db.ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False
    )

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "service_id": self.service_id,
        }


class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "customer_id": self.customer_id,
            "rating": self.rating,
            "time_posted": self.time_posted.isoformat(),
            "comment": self.comment,
        }


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
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
    data = request.get_json()
    new_dep = Dependent(name=data["name"], user_id=int(data["user_id"]))
    db.session.add(new_dep)
    db.session.commit()
    return new_dep.to_dict(), 201


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return [user.to_dict() for user in users], 200


@app.route("/users/<int:user_id>/dependents", methods=["GET"])
def get_user_dependents(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    dependents = Dependent.query.filter_by(user_id=user_id).all()
    return [d.to_dict() for d in dependents], 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted"}, 200


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/test-db")
def db_test():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
