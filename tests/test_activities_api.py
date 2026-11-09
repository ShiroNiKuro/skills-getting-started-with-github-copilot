import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = copy.deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arrange
    activity_name = "Basketball Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[activity_name]["participants"] == []


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    activity_path = quote(activity_name, safe="")
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    activity_path = quote(activity_name, safe="")
    email = "student@example.com"
    app_module.activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert app_module.activities[activity_name]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.post(
        f"/activities/{activity_path}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404


def test_delete_removes_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    activity_path = quote(activity_name, safe="")
    email = "student@example.com"
    app_module.activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email not in activities_response.json()[activity_name]["participants"]


def test_delete_returns_not_found_for_unregistered_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404


def test_delete_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404