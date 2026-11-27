import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Test Activity"
EXISTING_EMAIL = "existing@mergington.edu"
NEW_EMAIL = "new@mergington.edu"


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "A test activity",
            "schedule": "Mondays, 3:30 PM",
            "max_participants": 10,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, test_activities):
    # Arrange
    expected_activities = test_activities.copy()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client, test_activities):
    # Arrange
    email = NEW_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert email in test_activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_student(client, test_activities):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert email in test_activities[ACTIVITY_NAME]["participants"]
    assert test_activities[ACTIVITY_NAME]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": NEW_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_from_activity(client, test_activities):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {ACTIVITY_NAME}"}
    assert email not in test_activities[ACTIVITY_NAME]["participants"]


def test_unregister_returns_not_found_for_unregistered_student(client):
    # Arrange
    email = NEW_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
