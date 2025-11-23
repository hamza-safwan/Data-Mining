from flask import session
from flask_restful import Resource, request
from werkzeug.security import generate_password_hash, check_password_hash

from package.model import conn


def _serialize_user(row):
  if not row:
    return None
  return {
    "user_id": row["user_id"],
    "email": row["email"],
    "full_name": row.get("full_name"),
    "created_at": row.get("created_at"),
  }


def _set_session_for_user(user_row):
  """Store the minimal user identity details in the session."""
  session["user_id"] = user_row["user_id"]
  session["user_email"] = user_row["email"]
  session["user_full_name"] = user_row.get("full_name") or ""


class Signup(Resource):
  """API to register a new user account."""

  def post(self):
    payload = request.get_json(force=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    full_name = (payload.get("full_name") or "").strip()

    errors = []
    if not email:
      errors.append("Email is required.")
    if not password or len(password) < 6:
      errors.append("Password must be at least 6 characters long.")

    if errors:
      return {"errors": errors}, 400

    existing = conn.execute(
      "SELECT * FROM user WHERE email = ?", (email,)
    ).fetchone()
    if existing:
      return {"errors": ["Email is already registered."]}, 400

    password_hash = generate_password_hash(password)
    user_id = conn.execute(
      "INSERT INTO user(email, password_hash, full_name) VALUES(?,?,?)",
      (email, password_hash, full_name),
    ).lastrowid
    conn.commit()

    user_row = conn.execute(
      "SELECT * FROM user WHERE user_id = ?", (user_id,)
    ).fetchone()
    _set_session_for_user(user_row)

    return {"user": _serialize_user(user_row)}, 201


class Login(Resource):
  """API to log a user in and start a session."""

  def post(self):
    payload = request.get_json(force=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
      return {"errors": ["Email and password are required."]}, 400

    user_row = conn.execute(
      "SELECT * FROM user WHERE email = ?", (email,)
    ).fetchone()
    if not user_row:
      return {"errors": ["Invalid email or password."]}, 401

    if not check_password_hash(user_row["password_hash"], password):
      return {"errors": ["Invalid email or password."]}, 401

    _set_session_for_user(user_row)

    return {"user": _serialize_user(user_row)}, 200


class Logout(Resource):
  """API to log the current user out."""

  def post(self):
    session.pop("user_id", None)
    session.pop("user_email", None)
    session.pop("user_full_name", None)
    return {"message": "Logged out."}, 200


class CurrentUser(Resource):
  """API to fetch the currently authenticated user, if any."""

  def get(self):
    user_id = session.get("user_id")
    if not user_id:
      return {"authenticated": False, "user": None}, 200

    user_row = conn.execute(
      "SELECT * FROM user WHERE user_id = ?", (user_id,)
    ).fetchone()

    if not user_row:
      session.pop("user_id", None)
      session.pop("user_email", None)
      session.pop("user_full_name", None)
      return {"authenticated": False, "user": None}, 200

    _set_session_for_user(user_row)
    return {"authenticated": True, "user": _serialize_user(user_row)}, 200
