import sqlite3
import requests
import time
from database.setup_database import DB_PATH
from dateutil import parser
from argparse import ArgumentParser


def get_rate_limit(token=None):
    """
    Gets the number of queries you can still make to the GitHub API. It resets every hour.
    :param token: GitHub token. If provided the maximum amount of queries/hour is 5000 instead of 60.
    :return: Number of remaining queries.
    """
    if token:
        r = requests.get("https://api.github.com/rate_limit", headers={"authorization": "token " + token})
        if r.status_code == 401:
            raise ValueError("GitHub token is incorrect or has expired.")
        else:
            return r.json()["resources"]["core"]["remaining"]
    else:
        return requests.get("https://api.github.com/rate_limit").json()["resources"]["core"]["remaining"]


def get_events(session, url, etag, db_cursor, db_connection, token=None):
    """
    Gets all WatchEvent, PullRequestEvent and IssuesEvent from the GitHub event API and saves them into an sqlite
    database.
    :param session: requests session to query the GitHub API
    :param url: url to query github API
    :param etag: Last query identifier. If the response is the same, the identifier is the same, so it is not processed.
    :param db_cursor: Cursor of the sqlite database.
    :param db_connection: Connection to the sqlite database.
    :param token: GitHub token (optional).
    :return: Query response identifier.
    """
    headers = {"accept": "application/vnd.github.v3+json",
               "If-None-Match": etag}
    if token:
        headers["authorization"] = "token " + token
    params = {"per_page": "100"}
    with session.get(url, headers=headers, params=params, stream=True) as response:
        if response.status_code == 304:
            print("STATUS 304: Resource has not changed.")
            return etag

        for event in response.json():
            if event["type"] in ["WatchEvent", "PullRequestEvent", "IssuesEvent"]:
                created_at = int(parser.parse(event.get("created_at")).timestamp())  # Parse the created_at to int
                insert_data = (event.get("id"), event.get("type"), event.get("repo").get("id"),
                               event.get("repo").get("name"), created_at)
                # The IGNORE in the query triggers when trying to insert an event that already exists in the database.
                query = "INSERT OR IGNORE INTO events (id, type, repo_id, repo_name, created_at) VALUES (?, ?, ?, ?, ?)"
                db_cursor.execute(query, insert_data)
        db_connection.commit()
        return response.headers["etag"]


if __name__ == "__main__":
    # Parse input parameters
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-t", "--token",
                            help="add a GitHub token, so rate limit is increased from 60 to 5000 queries/hour.")
    args = arg_parser.parse_args()

    # Reusable variables
    s = requests.Session()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    token = args.token

    # Updatable variables
    rate_limit = get_rate_limit(token)
    etag = ""  # Initialize etag empty

    while rate_limit > 0:
        etag = get_events(s, "https://api.github.com/events", etag, cur, con, token)
        time.sleep(1)  # With these sleep we are doing 3600 queries/hour so rate_limit should never be < 1400.
        rate_limit = get_rate_limit(token)
        print("===============================")
        print("RATE LIMIT: " + str(rate_limit))
        print("===============================")

    con.close()
    print("Maximum amount of queries/hour has been reached. Consider creating a GitHub token to increase it to 5000.")
