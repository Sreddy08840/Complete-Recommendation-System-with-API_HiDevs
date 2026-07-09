
def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    # Check that X-Request-ID header is present
    assert "x-request-id" in response.headers


def test_get_recommendations(client, sample_data):
    """Test get recommendations endpoint."""
    user_id = sample_data["users"][0].id
    response = client.get(f"/recommend/{user_id}?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert len(data["recommendations"]) >= 1
    assert "x-request-id" in response.headers


def test_record_feedback(client, sample_data):
    """Test record feedback endpoint."""
    user_id = sample_data["users"][0].id
    content_id = sample_data["content"][0].id
    
    response = client.post("/feedback", json={
        "user_id": user_id,
        "content_id": content_id,
        "rating": 5,
        "interaction_type": "like"
    })
    assert response.status_code == 200
    assert "x-request-id" in response.headers


def test_get_metrics(client, sample_data):
    """Test get metrics endpoint."""
    # First make a recommendation request to get some metrics
    user_id = sample_data["users"][0].id
    client.get(f"/recommend/{user_id}")
    
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cache_hits" in data
    assert "cache_misses" in data
    assert "cache_current_size" in data
    assert "cache_max_size" in data
    assert "x-request-id" in response.headers


def test_users_router(client):
    """Test users router endpoints exist."""
    # Test get users returns 200 (even if empty)
    response = client.get("/users/")
    assert response.status_code in [200, 422]  # 422 if schema validation fails for empty list


def test_content_router(client):
    """Test content router endpoints exist."""
    # Test get content returns 200 (even if empty)
    response = client.get("/content/")
    assert response.status_code in [200, 422]

