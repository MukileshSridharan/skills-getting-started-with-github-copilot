from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # ensure test email starts absent
    activity = client.get("/activities").json()[activity_name]
    if email in activity["participants"]:
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200

    unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert unregister_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_error():
    response = client.delete("/activities/Chess Club/unregister?email=missing@mergington.edu")
    assert response.status_code == 404
