import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial state of activities for resetting
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Compete in basketball games and tournaments",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis techniques and play matches",
        "schedule": "Saturdays, 9:00 AM - 11:00 AM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and visual arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["ava@mergington.edu"]
    },
    "Music Band": {
        "description": "Join the school band and perform in concerts",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["harper@mergington.edu", "ethan@mergington.edu"]
    }
}

@pytest.fixture
def client():
    # Reset activities to initial state before each test
    activities.clear()
    activities.update(initial_activities)
    return TestClient(app)

def test_get_activities(client):
    # Arrange: Client is set up with initial activities

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and response data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert len(data["Chess Club"]["participants"]) == 2

def test_signup_successful(client):
    # Arrange: Valid email and activity with space
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Success
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]

def test_signup_invalid_email(client):
    # Arrange: Invalid email
    activity_name = "Chess Club"
    email = "invalid-email"

    # Act: Signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Bad request
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]

def test_signup_activity_not_found(client):
    # Arrange: Non-existent activity
    activity_name = "NonExistent"
    email = "student@mergington.edu"

    # Act: Signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Not found
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_signup_already_signed_up(client):
    # Arrange: Email already in participants
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in initial

    # Act: Signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Bad request
    assert response.status_code == 400
    assert "Student is already signed up" in response.json()["detail"]

def test_signup_at_capacity(client):
    # Arrange: Fill to capacity, then try to add more
    activity_name = "Tennis Club"  # max 10, has 2
    emails = [f"extra{i}@mergington.edu" for i in range(8)]  # Add 8 more to reach 10
    for email in emails:
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Now at capacity
    extra_email = "over@mergington.edu"

    # Act: Try to signup one more
    response = client.post(f"/activities/{activity_name}/signup", params={"email": extra_email})

    # Assert: Bad request
    assert response.status_code == 400
    assert "Activity is at maximum capacity" in response.json()["detail"]

def test_unregister_successful(client):
    # Arrange: Email in activity
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act: Unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Success
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]

def test_unregister_invalid_email(client):
    # Arrange: Invalid email
    activity_name = "Chess Club"
    email = "invalid"

    # Act: Unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Bad request
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]

def test_unregister_activity_not_found(client):
    # Arrange: Non-existent activity
    activity_name = "Fake"
    email = "student@mergington.edu"

    # Act: Unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Not found
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_not_signed_up(client):
    # Arrange: Email not in activity
    activity_name = "Chess Club"
    email = "notsigned@mergington.edu"

    # Act: Unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert: Not found
    assert response.status_code == 404
    assert "Student not signed up" in response.json()["detail"]