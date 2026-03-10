from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import uuid4
import uuid

app = Flask(__name__)

load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def normalize_uuid(value):
    if value is None:
        return None
    s = str(value)
    if len(s) != 36:
        return None
    parts = s.split("-")
    if [len(p) for p in parts] != [8, 4, 4, 4, 12]:
        return None
    return s.lower()


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
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
    dependent_id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    def to_dict(self):
        return {
            "dependent_id": self.dependent_id,
            "name": self.name,
            "user_id": self.user_id,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"
    appointment_id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid4())
    )
    customer_id = db.Column(
        db.String(36),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    staff_id = db.Column(
        db.String(36),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    time_booked = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(
        db.String(36),
        db.ForeignKey("services.service_id", ondelete="RESTRICT"),
        nullable=False,
    )

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
    service_id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid4())
    )
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
        db.String(36),
        db.ForeignKey("appointments.appointment_id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id = db.Column(
        db.String(36),
        db.ForeignKey("services.service_id", ondelete="CASCADE"),
        primary_key=True,
    )

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "service_id": self.service_id,
        }


class Review(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(
        db.String(36),
        db.ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    rating = db.Column(db.Integer, nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String(255))

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
    admin_exists = User.query.filter_by(role="admin").first() is not None
    role = "customer"
    if not admin_exists:
        role = "admin"
    new_user = User(
        email=data["email"], password=data["password"], name=data["name"], role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict(), 201


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return [user.to_dict() for user in users], 200


@app.route("/dependents", methods=["POST"])
def create_dependent():
    data = request.get_json()
    if "name" not in data or "user_id" not in data:
        return {"error": "Missing field: name or user_id"}, 400
    user_id = normalize_uuid(data["user_id"])
    if user_id is None:
        return {"error": "Invalid user_id"}, 400
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    new_dependent = Dependent(name=data["name"], user_id=user_id)
    db.session.add(new_dependent)
    db.session.commit()
    return new_dependent.to_dict(), 201


@app.route("/users/<string:user_id>/dependents", methods=["GET"])
def get_user_dependents(user_id):
    user_id = normalize_uuid(user_id)
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    dependents = Dependent.query.filter_by(user_id=user_id).all()
    return [d.to_dict() for d in dependents], 200


@app.route("/users/<string:user_id>/role", methods=["PATCH"])
def change_role(user_id):
    data = request.get_json()
    admin_id = normalize_uuid(data.get("admin_id"))
    role = data.get("role")
    if admin_id is None or role is None:
        return {"error": "admin_id and role required"}, 400
    admin = User.query.get(admin_id)
    if not admin:
        return {"error": "Admin user not found"}, 404
    if admin.role != "admin":
        return {"error": "Admins only"}, 403
    user_id = normalize_uuid(user_id)
    user = User.query.get_or_404(user_id)
    user.role = role
    db.session.commit()
    return user.to_dict(), 200


@app.route("/users", methods=["DELETE"])
@app.route("/users/<string:user_id>", methods=["DELETE"])
def delete_users(user_id=None):
    if user_id is None:
        users = User.query.all()
        if not users:
            return {"message": "No users to delete"}, 200
        count = len(users)
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return {"message": f"{count} users deleted"}, 200
    user_id = normalize_uuid(user_id)
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"message": f"User {user_id} deleted"}, 200


@app.route("/appointments", methods=["GET"])
def get_appointments():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM appointments;"))
        return [dict(row._mapping) for row in result]


@app.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()
    required = ["customer_id", "staff_id", "start_time", "end_time", "service_id"]
    for field in required:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400
    customer_id = normalize_uuid(data["customer_id"])
    staff_id = normalize_uuid(data["staff_id"])
    service_id = normalize_uuid(data["service_id"])
    customer = User.query.get(customer_id)
    staff = User.query.get(staff_id)
    if not customer:
        return {"error": "Customer not found"}, 404
    if not staff:
        return {"error": "Staff not found"}, 404
    start_time = datetime.fromisoformat(data["start_time"])
    end_time = datetime.fromisoformat(data["end_time"])
    new_appointment = Appointment(
        customer_id=customer_id,
        staff_id=staff_id,
        start_time=start_time,
        end_time=end_time,
        time_booked=datetime.utcnow(),
        service_id=service_id,
    )
    db.session.add(new_appointment)
    db.session.commit()
    return new_appointment.to_dict(), 201


@app.route("/appointments/<string:appointment_id>", methods=["PATCH"])
def update_appointment(appointment_id):
    appointment_id = normalize_uuid(appointment_id)
    if appointment_id is None:
        return {"error": "Invalid appointment_id"}, 400
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"error": "Appointment not found"}, 404
    data = request.get_json()
    if "customer_id" in data:
        customer_id = normalize_uuid(data["customer_id"])
        if customer_id is None:
            return {"error": "Invalid customer_id"}, 400
        customer = User.query.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}, 404
        appointment.customer_id = customer_id
    if "staff_id" in data:
        staff_id = normalize_uuid(data["staff_id"])
        if staff_id is None:
            return {"error": "Invalid staff_id"}, 400
        staff = User.query.get(staff_id)
        if not staff:
            return {"error": "Staff not found"}, 404
        appointment.staff_id = staff_id
    if "service_id" in data:
        service_id = normalize_uuid(data["service_id"])
        if service_id is None:
            return {"error": "Invalid service_id"}, 400
        service = Service.query.get(service_id)
        if not service:
            return {"error": "Service not found"}, 404
        appointment.service_id = service_id
    if "start_time" in data:
        appointment.start_time = datetime.fromisoformat(data["start_time"])
    if "end_time" in data:
        appointment.end_time = datetime.fromisoformat(data["end_time"])
    if appointment.end_time <= appointment.start_time:
        return {"error": "end_time must be after start_time"}, 400
    db.session.commit()
    return appointment.to_dict(), 200


@app.route("/appointments", methods=["DELETE"])
@app.route("/appointments/<string:appointment_id>", methods=["DELETE"])
def delete_appointments(appointment_id=None):
    if appointment_id is None:
        appointments = Appointment.query.all()
        if not appointments:
            return {"message": "No appointments to delete"}, 200
        count = len(appointments)
        for appt in appointments:
            db.session.delete(appt)
        db.session.commit()
        return {"message": f"{count} appointments deleted"}, 200
    appointment_id = normalize_uuid(appointment_id)
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"error": "Appointment not found"}, 404
    db.session.delete(appointment)
    db.session.commit()
    return {"message": f"Appointment {appointment_id} deleted"}, 200


@app.route("/users/<string:user_id>/appointments", methods=["GET"])
def get_user_appointments(user_id):
    user_id = normalize_uuid(user_id)
    if user_id is None:
        return {"error": "Invalid user_id"}, 400
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    appointments = Appointment.query.filter(
        (Appointment.customer_id == user_id) | (Appointment.staff_id == user_id)
    ).all()
    return [a.to_dict() for a in appointments], 200


@app.route("/appointment-service", methods=["GET"])
def get_appointment_service():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM appointment_services;"))
        return [dict(row._mapping) for row in result]


@app.route("/appointment-service", methods=["POST"])
def create_appointment_service():
    data = request.get_json()
    appointment_id = normalize_uuid(data["appointment_id"])
    service_id = normalize_uuid(data["service_id"])
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"error": "Appointment not found"}, 404
    service = Service.query.get(service_id)
    if not service:
        return {"error": "Service not found"}, 404
    new_link = AppointmentService(appointment_id=appointment_id, service_id=service_id)
    db.session.add(new_link)
    db.session.commit()
    return new_link.to_dict(), 201


@app.route("/reviews", methods=["POST"])
def create_review():
    data = request.get_json()
    if "rating" not in data:
        return {"error": "rating required"}, 400
    customer_id = data.get("customer_id")
    if customer_id is not None:
        customer_id = normalize_uuid(customer_id)
        user = User.query.get(customer_id)
        if not user:
            return {"error": "Customer not found"}, 404
    if "time_posted" in data:
        time_posted = datetime.fromisoformat(data["time_posted"])
    else:
        time_posted = datetime.now(ZoneInfo("America/New_York"))
    new_review = Review(
        customer_id=customer_id,
        rating=data["rating"],
        comment=data.get("comment"),
        time_posted=time_posted,
    )
    db.session.add(new_review)
    db.session.commit()
    return new_review.to_dict(), 201


@app.route("/reviews", methods=["DELETE"])
@app.route("/reviews/<string:review_id>", methods=["DELETE"])
def delete_reviews(review_id=None):
    if review_id is None:
        reviews = Review.query.all()
        if not reviews:
            return {"message": "No reviews to delete"}, 200
        count = len(reviews)
        for r in reviews:
            db.session.delete(r)
        db.session.commit()
        return {"message": f"{count} reviews deleted"}, 200
    review_id = normalize_uuid(review_id)
    review = Review.query.get(review_id)
    if not review:
        return {"error": "Review not found"}, 404
    db.session.delete(review)
    db.session.commit()
    return {"message": f"Review {review_id} deleted"}, 200


@app.route("/reviews", methods=["GET"])
def get_reviews():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM reviews;"))
        return [dict(row._mapping) for row in result]


@app.route("/services", methods=["POST"])
def create_service():
    data = request.get_json()
    if "service_name" not in data or "price" not in data:
        return {"error": "Missing field: service_name or price"}, 400
    new_service = Service(service_name=data["service_name"], price=data["price"])
    db.session.add(new_service)
    db.session.commit()
    return new_service.to_dict(), 201


@app.route("/service", methods=["GET"])
def get_service():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM services;"))
        return [dict(row._mapping) for row in result]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
