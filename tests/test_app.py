"""
Test cases for the High School Management System API
"""

import pytest


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check Chess Club details
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    
    # Verify the student was added
    activities_response = client.get("/activities")
    chess_club = activities_response.json()["Chess Club"]
    assert "newstudent@mergington.edu" in chess_club["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_registration(client):
    """Test that a student cannot register twice for the same activity"""
    email = "michael@mergington.edu"
    
    # Try to register the same student again
    response = client.post(
        f"/activities/Chess Club/signup?email={email}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already registered for this activity"


def test_unregister_from_activity_success(client):
    """Test successfully unregistering from an activity"""
    email = "michael@mergington.edu"
    
    # Unregister the student
    response = client.delete(
        f"/activities/Chess Club/unregister?email={email}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    
    # Verify the student was removed
    activities_response = client.get("/activities")
    chess_club = activities_response.json()["Chess Club"]
    assert email not in chess_club["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_registered(client):
    """Test unregistering a student who is not registered for the activity"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"


def test_signup_and_unregister_flow(client):
    """Test the complete flow of signing up and then unregistering"""
    email = "testflow@mergington.edu"
    activity = "Programming Class"
    
    # Sign up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Verify registration
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unregister_response.status_code == 200
    
    # Verify unregistration
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]


def test_multiple_students_signup(client):
    """Test multiple students signing up for the same activity"""
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    for email in students:
        response = client.post(f"/activities/Gym Class/signup?email={email}")
        assert response.status_code == 200
    
    # Verify all students are registered
    activities_response = client.get("/activities")
    gym_participants = activities_response.json()["Gym Class"]["participants"]
    for email in students:
        assert email in gym_participants
