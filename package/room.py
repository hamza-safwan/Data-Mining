from flask import session
from flask_restful import Resource, Api, request
from package.model import conn


class Rooms(Resource):
  """This contain apis to carry out activity with all rooms"""

  def get(self):
    """Retrieve all the rooms and return in form of json"""

    room = conn.execute("SELECT * from room").fetchall()
    return room

  def post(self):
    """Add a room in the database, respecting bed limits if configured."""

    room = request.get_json(force=True)
    room_no = room["room_no"]
    room_type = room["room_type"]
    available = room["available"]

    # Enforce maximum number of beds/rooms if the current account profile sets a limit.
    user_id = session.get("user_id")
    if user_id:
      profile = conn.execute(
        "SELECT total_beds FROM account_profile WHERE user_id = ?",
        (user_id,),
      ).fetchone()
      if profile is not None:
        limit = profile.get("total_beds")
        if limit is not None:
          current_row = conn.execute(
            "SELECT COUNT(*) AS c FROM room"
          ).fetchone()
          if current_row["c"] >= limit:
            return {
              "errors": [
                "You have reached the maximum number of beds configured in your account profile."
              ]
            }, 400

    conn.execute(
      """INSERT INTO room(room_no, room_type, available) VALUES(?,?,?)""",
      (room_no, room_type, available),
    )
    conn.commit()
    return room


class Room(Resource):
  """This contain all api doing activity with single room"""

  def get(self, room_no):
    """Retrieve a single room details by its room_no"""

    room = conn.execute(
      "SELECT * FROM room WHERE room_no=?", (room_no,)
    ).fetchall()
    return room

  def delete(self, room_no):
    """Delete the room by its room_no"""

    conn.execute("DELETE FROM room WHERE room_no=?", (room_no,))
    conn.commit()
    return {"msg": "sucessfully deleted"}

  def put(self, room_no):
    """Update the room details by the room_no"""

    room = request.get_json(force=True)
    room_type = room["room_type"]
    available = room["available"]
    conn.execute(
      "UPDATE room SET room_type=?,available=? WHERE room_no=?",
      (room_type, available, room_no),
    )
    conn.commit()
    return room
