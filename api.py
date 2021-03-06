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
    try:
        # Compute the "created_at" lower bound to query the database
        time_bound = int(datetime.datetime.now().timestamp()) - int(offset_minutes) * 60
    except:
        return {"TypeError": "Offset minutes must be an integer"}, 400
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    query = "SELECT type, count(id) as counter FROM events WHERE created_at >= ? GROUP BY type"
    data = cur.execute(query, [time_bound]).fetchall()

    # Initialize result in 0 for all types, so if data is empty for any or all types, it will return 0 instead of None.
    result = {"IssuesEvent": 0, "PullRequestEvent": 0, "WatchEvent": 0}
    for event_type, count in data:
        result[event_type] = count

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
            FROM events where repo_name = ? and type = "PullRequestEvent"
            )
    """
    full_repo = github_user + "/" + repository
    data = cur.execute(query, [full_repo]).fetchall()
    if data[0][0] is None:
        # This happens both if there is only one Pull Request or if there aren't any.
        return {"Insuficient Data": "The selected repository does not have enough Pull Requests "
                                    "to compute an average."}, 400
    return {"average_time": data[0][0]}, 200


if __name__ == "__main__":
    app.run(debug=True)
