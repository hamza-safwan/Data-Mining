from flask import session
from flask_restful import Resource, Api, request
from package.model import conn


class Doctors(Resource):
  """APIs to carry out activity with all doctors."""

  def get(self):
    """Retrieve list of all the doctors."""

    doctors = conn.execute(
      "SELECT * FROM doctor ORDER BY doc_date DESC"
    ).fetchall()
    return doctors

  def post(self):
    """Add a new doctor, respecting account profile limits if configured."""

    doctorInput = request.get_json(force=True)
    doc_first_name = doctorInput["doc_first_name"]
    doc_last_name = doctorInput["doc_last_name"]
    doc_ph_no = doctorInput["doc_ph_no"]
    doc_address = doctorInput["doc_address"]

    # Enforce maximum number of doctors if the current account profile sets a limit.
    user_id = session.get("user_id")
    if user_id:
      profile = conn.execute(
        "SELECT total_doctors FROM account_profile WHERE user_id = ?",
        (user_id,),
      ).fetchone()
      if profile is not None:
        limit = profile.get("total_doctors")
        if limit is not None:
          current_row = conn.execute(
            "SELECT COUNT(*) AS c FROM doctor"
          ).fetchone()
          if current_row["c"] >= limit:
            return {
              "errors": [
                "You have reached the maximum number of doctors configured in your account profile."
              ]
            }, 400

    doctorInput["doc_id"] = conn.execute(
      """INSERT INTO doctor(doc_first_name, doc_last_name, doc_ph_no, doc_address)
            VALUES(?,?,?,?)""",
      (doc_first_name, doc_last_name, doc_ph_no, doc_address),
    ).lastrowid
    conn.commit()
    return doctorInput


class Doctor(Resource):
  """APIs carrying out the activity with a single doctor."""

  def get(self, id):
    """Get the details of the doctor by the doctor id."""

    doctor = conn.execute(
      "SELECT * FROM doctor WHERE doc_id=?", (id,)
    ).fetchall()
    return doctor

  def delete(self, id):
    """Delete the doctor by its id."""

    conn.execute("DELETE FROM doctor WHERE doc_id=?", (id,))
    conn.commit()
    return {"msg": "sucessfully deleted"}

  def put(self, id):
    """Update the doctor by its id."""

    doctorInput = request.get_json(force=True)
    doc_first_name = doctorInput["doc_first_name"]
    doc_last_name = doctorInput["doc_last_name"]
    doc_ph_no = doctorInput["doc_ph_no"]
    doc_address = doctorInput["doc_address"]
    conn.execute(
      "UPDATE doctor SET doc_first_name=?,doc_last_name=?,doc_ph_no=?,doc_address=? WHERE doc_id=?",
      (doc_first_name, doc_last_name, doc_ph_no, doc_address, id),
    )
    conn.commit()
    return doctorInput
