"""
API endpoint tests for the Mergington High School activities management system.
"""
import pytest


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds a participant to an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up twice for the same activity fails."""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Test the POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes a participant from an activity."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-existent participant fails."""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nobody@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister for nonexistent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test the complete workflow of signing up and then unregistering."""
        email = "workflow@mergington.edu"
        activity = "Programming%20Class"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Get activities to verify participant was added
        response2 = client.get("/activities")
        activities_data = response2.json()
        assert email in activities_data["Programming Class"]["participants"]
        
        # Unregister
        response3 = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response3.status_code == 200
        
        # Get activities to verify participant was removed
        response4 = client.get("/activities")
        activities_data = response4.json()
        assert email not in activities_data["Programming Class"]["participants"]
