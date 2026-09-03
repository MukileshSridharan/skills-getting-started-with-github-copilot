from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    # Arrange
    path = "/"

    # Act
    response = client.get(path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_records(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    records = response.json()
    assert set(records) == set(activities)
    assert all(
        set(record) == {"description", "schedule", "max_participants", "participants"}
        for record in records.values()
    )


def test_signup_adds_participant_to_activity_with_spaces(client):
    # Arrange
    email = "student@mergington.edu"
    path = f"/activities/Chess Club/signup?email={email}"

    # Act
    response = client.post(path)
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    path = "/activities/Chess Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}


def test_signup_rejects_unknown_activity(client):
    # Arrange
    path = "/activities/Unknown Club/signup?email=student@mergington.edu"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = "student@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    path = f"/activities/Chess Club/unregister?email={email}"

    # Act
    response = client.delete(path)
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_rejects_missing_participant(client):
    # Arrange
    path = "/activities/Chess Club/unregister?email=missing@mergington.edu"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    path = "/activities/Unknown Club/unregister?email=student@mergington.edu"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}