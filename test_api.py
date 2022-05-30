import requests

BASE = "http://127.0.0.1:5000/"
time_request = "time-between-requests/thoth-station/prescriptions"

response = requests.get(BASE + time_request)
print(response.json())
input()
response = requests.get(BASE + "video/2")
print(response.json())
