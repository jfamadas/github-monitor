from flask import Flask
from database.setup_database import DB_PATH
import sqlite3
import datetime

app = Flask(__name__)


@app.route("/events-by-type/<offset_minutes>", methods=["GET"])
def get_events_by_type(offset_minutes):
    """
    Return the total number of events grouped by the event type for a given offset (in minutes)
    :param offset_minutes: Time duration of the counting window (in minutes)
    :return: dictionary where the event type are the keys and the number of events the values.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    time_bound = int(datetime.datetime.now().timestamp()) - int(offset_minutes) * 60
    query = "SELECT type, count(id) as counter FROM events WHERE created_at >= ? GROUP BY type"
    data = cur.execute(query, [time_bound]).fetchall()
    result = {data[0][0]: data[0][1], data[1][0]: data[1][1], data[2][0]: data[2][1]}
    return result, 200


@app.route("/time-between-requests/<github_user>/<repository>", methods=["GET"])
def get_time_between_requests(github_user, repository):
    """
    Calculate the average time between pull requests for a given repository
    :param github_user: first part of the repository, which identifies its owner
    :param repository: second part of the repository, which identifies its name
    :return: average time (in seconds) between pull requests.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    query = """
        SELECT avg(created_at_diff) from (
            SELECT 
                created_at - lag(created_at,1) over (ORDER BY created_at) as created_at_diff
            FROM events where repo_name = ?
            )
    """
    full_repo = github_user + "/" + repository
    data = cur.execute(query, [full_repo]).fetchall()
    return {"average_time": data[0][0]}, 200


if __name__ == "__main__":
    app.run(debug=True)
