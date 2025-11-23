#Tushar Borole
#Python 2.7

from flask import session
from flask_restful import Resource, Api, request
from package.model import conn


class Departments(Resource):
  """This contain apis to carry out activity with all departments."""

  def get(self):
    """Retrieve all the departments and return in form of json."""

    # department = conn.execute("SELECT * from department").fetchall()
    department = conn.execute(
      "SELECT department_id, name, head_id, doc_first_name, doc_last_name "
      "FROM department INNER JOIN doctor ON doctor.doc_id = department.head_id"
    ).fetchall()
    return department

  def post(self):
    """Add a department, respecting account profile limits if configured."""

    department = request.get_json(force=True)
    department_id = department["department_id"]
    name = department["name"]
    head_id = department["head_id"]

    # Enforce maximum number of departments if the current account profile sets a limit.
    user_id = session.get("user_id")
    if user_id:
      profile = conn.execute(
        "SELECT total_departments FROM account_profile WHERE user_id = ?",
        (user_id,),
      ).fetchone()
      if profile is not None:
        limit = profile.get("total_departments")
        if limit is not None:
          current_row = conn.execute(
            "SELECT COUNT(*) AS c FROM department"
          ).fetchone()
          if current_row["c"] >= limit:
            return {
              "errors": [
                "You have reached the maximum number of departments configured in your account profile."
              ]
            }, 400

    conn.execute(
      """INSERT INTO department(department_id, name, head_id) VALUES(?,?,?)""",
      (department_id, name, head_id),
    )
    conn.commit()
    return department


class Department(Resource):
  """This contain all api doing activity with single department"""

  def get(self, department_id):
    """Retrieve a single department details by its id."""

    department = conn.execute(
      "SELECT * FROM department WHERE department_id=?", (department_id,)
    ).fetchall()
    return department

  # def delete(self, code):
  #   """Delete the appointment by its id"""
  #
  #   conn.execute("DELETE FROM department WHERE department_id=?", (code,))
  #   conn.commit()
  #   return {"msg": "sucessfully deleted"}

  def put(self, department_id):
    """Update the department details by the department id."""

    department = request.get_json(force=True)
    name = department["name"]
    head_id = department["head_id"]
    conn.execute(
      "UPDATE department SET name=?,head_id=? WHERE department_id=?",
      (name, head_id, department_id),
    )
    conn.commit()
    return department
