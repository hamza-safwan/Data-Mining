from flask import (
  Flask,
  send_from_directory,
  render_template,
  redirect,
  url_for,
  session,
  request,
)
from flask import send_from_directory

from flask_restful import Resource, Api
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.common import Common
from package.medication import Medication, Medications
from package.department import Departments, Department
from package.nurse import Nurse, Nurses
from package.room import Room, Rooms
from package.procedure import Procedure, Procedures
from package.prescribes import Prescribes, Prescribe
from package.undergoes import Undergoess, Undergoes
from package.auth import Signup, Login, Logout, CurrentUser
from package.model import conn

import json
import os
from functools import wraps

with open("config.json") as data_file:
  config = json.load(data_file)

app = Flask(__name__, static_url_path="")
app.secret_key = config.get("secret_key", "change-this-secret")
api = Api(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "profile_pics")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def login_required(view):
  @wraps(view)
  def wrapped(*args, **kwargs):
    if not session.get("user_id"):
      return redirect(url_for("login_page"))
    return view(*args, **kwargs)

  return wrapped


def _get_account_profile(user_id):
  """Return the account_profile row for the given user, or None."""
  return conn.execute(
    "SELECT * FROM account_profile WHERE user_id = ?", (user_id,)
  ).fetchone()


def _get_or_create_account_profile(user_id):
  profile = _get_account_profile(user_id)
  if profile:
    return profile
  conn.execute(
    """INSERT INTO account_profile(user_id, hospital_name, total_doctors,
total_departments, total_beds, profile_image)
VALUES (?, '', NULL, NULL, NULL, NULL);""",
    (user_id,),
  )
  conn.commit()
  return _get_account_profile(user_id)


api.add_resource(Patients, "/patient")
api.add_resource(Patient, "/patient/<int:id>")
api.add_resource(Doctors, "/doctor")
api.add_resource(Doctor, "/doctor/<int:id>")
api.add_resource(Appointments, "/appointment")
api.add_resource(Appointment, "/appointment/<int:id>")
api.add_resource(Common, "/common")
api.add_resource(Medications, "/medication")
api.add_resource(Medication, "/medication/<int:code>")
api.add_resource(Departments, "/department")
api.add_resource(Department, "/department/<int:department_id>")
api.add_resource(Nurses, "/nurse")
api.add_resource(Nurse, "/nurse/<int:id>")
api.add_resource(Rooms, "/room")
api.add_resource(Room, "/room/<int:room_no>")
api.add_resource(Procedures, "/procedure")
api.add_resource(Procedure, "/procedure/<int:code>")
api.add_resource(Prescribes, "/prescribes")
api.add_resource(Undergoess, "/undergoes")

# Auth APIs
api.add_resource(Signup, "/auth/signup")
api.add_resource(Login, "/auth/login")
api.add_resource(Logout, "/auth/logout")
api.add_resource(CurrentUser, "/auth/me")


# Routes
@app.route("/favicon.ico")
def favicon():
  return send_from_directory(
    os.path.join(app.root_path, "static"),
    "favicon.ico",
    mimetype="image/vnd.microsoft.icon",
  )


@app.route("/assets/<path:filename>")
def assets(filename):
  return send_from_directory(os.path.join(app.root_path, "assets"), filename)


@app.route("/")
def index():
  return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
  user_id = session["user_id"]
  profile = _get_or_create_account_profile(user_id)
  return render_template(
    "dashboard.html", active_page="dashboard", profile=profile
  )


@app.route("/patients")
@login_required
def patients_page():
  return render_template("patients.html", active_page="patients")


@app.route("/doctors")
@login_required
def doctors_page():
  return render_template("doctors.html", active_page="doctors")


@app.route("/appointments")
@login_required
def appointments_page():
  return render_template("appointments.html", active_page="appointments")


@app.route("/nurses")
@login_required
def nurses_page():
  return render_template("nurses.html", active_page="nurses")


@app.route("/rooms")
@login_required
def rooms_page():
  return render_template("rooms.html", active_page="rooms")


@app.route("/medications")
@login_required
def medications_page():
  return render_template("medications.html", active_page="medications")


@app.route("/departments")
@login_required
def departments_page():
  return render_template("departments.html", active_page="departments")


@app.route("/procedures")
@login_required
def procedures_page():
  return render_template("procedures.html", active_page="procedures")


@app.route("/prescribes-view")
@login_required
def prescribes_view_page():
  return render_template("prescribes_view.html", active_page="prescribes")


@app.route("/undergoes-view")
@login_required
def undergoes_view_page():
  return render_template("undergoes_view.html", active_page="undergoes")


@app.route("/account/profile", methods=["GET", "POST"])
@login_required
def account_profile_page():
  user_id = session["user_id"]
  profile = _get_or_create_account_profile(user_id)

  message = None
  error = None

  # Current utilization across this MedSync instance.
  usage = {
    "doctors": conn.execute("SELECT COUNT(*) AS c FROM doctor").fetchone()["c"],
    "departments": conn.execute(
      "SELECT COUNT(*) AS c FROM department"
    ).fetchone()["c"],
    "beds": conn.execute("SELECT COUNT(*) AS c FROM room").fetchone()["c"],
  }

  if request.method == "POST":
    hospital_name = (request.form.get("hospital_name") or "").strip()
    total_doctors_raw = request.form.get("total_doctors") or ""
    total_departments_raw = request.form.get("total_departments") or ""
    total_beds_raw = request.form.get("total_beds") or ""

    def _parse_int(val):
      val = (val or "").strip()
      if not val:
        return None
      try:
        parsed = int(val)
      except ValueError:
        return None
      return max(parsed, 0)

    total_doctors = _parse_int(total_doctors_raw)
    total_departments = _parse_int(total_departments_raw)
    total_beds = _parse_int(total_beds_raw)

    file = request.files.get("profile_image")
    profile_image_path = profile.get("profile_image")

    if file and file.filename:
      from werkzeug.utils import secure_filename

      filename = secure_filename(file.filename)
      name, ext = os.path.splitext(filename)
      ext = ext.lower()
      if ext not in [".png", ".jpg", ".jpeg", ".gif"]:
        error = "Profile picture must be a PNG, JPG, or GIF."
      else:
        new_filename = f"user_{user_id}{ext}"
        full_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
        file.save(full_path)
        profile_image_path = f"profile_pics/{new_filename}"

    # Ensure new limits are not less than currently utilized resources.
    if not error:
      if total_doctors is not None and usage["doctors"] > total_doctors:
        error = (
          "You already have more doctors than the limit you entered. "
          "Please choose a value that is at least "
          f"{usage['doctors']} or reduce your doctors first."
        )
      elif total_departments is not None and usage["departments"] > total_departments:
        error = (
          "You already have more departments than the limit you entered. "
          "Please choose a value that is at least "
          f"{usage['departments']} or reduce your departments first."
        )
      elif total_beds is not None and usage["beds"] > total_beds:
        error = (
          "You already have more rooms than the limit you entered. "
          "Please choose a value that is at least "
          f"{usage['beds']} or reduce your rooms first."
        )

    if not error:
      conn.execute(
        """UPDATE account_profile
SET hospital_name = ?, total_doctors = ?, total_departments = ?, total_beds = ?, profile_image = ?,
updated_at = datetime('now','localtime')
WHERE user_id = ?""",
        (
          hospital_name,
          total_doctors,
          total_departments,
          total_beds,
          profile_image_path,
          user_id,
        ),
      )
      conn.commit()
      profile = _get_account_profile(user_id)
      message = "Account profile updated."

  return render_template(
    "account_profile.html",
    active_page="account_profile",
    profile=profile,
    usage=usage,
    message=message,
    error=error,
  )


@app.route("/account/settings", methods=["GET", "POST"])
@login_required
def account_settings_page():
  from werkzeug.security import generate_password_hash, check_password_hash

  user_id = session["user_id"]
  message = None
  error = None

  if request.method == "POST":
    form_type = request.form.get("form_type")

    if form_type == "update_profile":
      full_name = (request.form.get("full_name") or "").strip()
      conn.execute(
        "UPDATE user SET full_name = ? WHERE user_id = ?", (full_name, user_id)
      )
      conn.commit()
      # Keep session in sync for navbar display.
      session["user_full_name"] = full_name
      message = "Profile details updated."

    elif form_type == "change_password":
      current_password = request.form.get("current_password") or ""
      new_password = request.form.get("new_password") or ""
      confirm_password = request.form.get("confirm_password") or ""

      if new_password != confirm_password:
        error = "New passwords do not match."
      elif len(new_password) < 6:
        error = "New password must be at least 6 characters long."
      else:
        user_row = conn.execute(
          "SELECT * FROM user WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not user_row or not check_password_hash(
          user_row["password_hash"], current_password
        ):
          error = "Current password is incorrect."
        else:
          new_hash = generate_password_hash(new_password)
          conn.execute(
            "UPDATE user SET password_hash = ? WHERE user_id = ?",
            (new_hash, user_id),
          )
          conn.commit()
          message = "Password updated successfully."

    elif form_type == "add_admin":
      admin_full_name = (request.form.get("admin_full_name") or "").strip()
      admin_email = (request.form.get("admin_email") or "").strip().lower()
      admin_password = request.form.get("admin_password") or ""

      if not admin_email or not admin_password:
        error = "Admin email and password are required."
      elif len(admin_password) < 6:
        error = "Admin password must be at least 6 characters long."
      else:
        existing = conn.execute(
          "SELECT * FROM user WHERE email = ?", (admin_email,)
        ).fetchone()
        if existing:
          error = "An account with that email already exists."
        else:
          pwd_hash = generate_password_hash(admin_password)
          conn.execute(
            "INSERT INTO user(email, password_hash, full_name) VALUES(?,?,?)",
            (admin_email, pwd_hash, admin_full_name),
          )
          conn.commit()
          message = "Admin account created."

    elif form_type == "remove_admin":
      target_id_raw = request.form.get("admin_id")
      try:
        target_id = int(target_id_raw)
      except (TypeError, ValueError):
        target_id = None

      if not target_id:
        error = "Invalid admin selected."
      elif target_id == user_id:
        error = "You cannot remove your own admin account from here."
      else:
        conn.execute("DELETE FROM user WHERE user_id = ?", (target_id,))
        conn.commit()
        message = "Admin removed."

  current_user_row = conn.execute(
    "SELECT * FROM user WHERE user_id = ?", (user_id,)
  ).fetchone()
  admins = conn.execute(
    "SELECT user_id, email, full_name, created_at FROM user ORDER BY created_at ASC"
  ).fetchall()

  return render_template(
    "account_settings.html",
    active_page="account_settings",
    current_user=current_user_row,
    admins=admins,
    message=message,
    error=error,
  )


@app.route("/logout")
@login_required
def logout_page():
  # Clear session and send user back to the marketing landing page.
  session.pop("user_id", None)
  session.pop("user_email", None)
  session.pop("user_full_name", None)
  return redirect(url_for("index"))


@app.route("/login")
def login_page():
  return render_template("login.html")


@app.route("/signup")
def signup_page():
  return render_template("signup.html")


if __name__ == "__main__":
  app.run(debug=True, host=config["host"], port=config["port"])
