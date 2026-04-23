# tests/integration/test_api.py



class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestCreateItem:
    """Tests for POST /api/items."""

    def test_create_item_success(self, client, sample_item_payload):
        response = client.post("/api/items", json=sample_item_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Widget"
        assert data["price"] == 29.99
        assert "id" in data
        assert "created_at" in data

    def test_create_item_minimal(self, client):
        response = client.post("/api/items", json={"name": "Minimal", "price": 1.00})
        assert response.status_code == 201
        assert response.json()["description"] == ""
        assert response.json()["status"] == "active"

    def test_create_item_invalid_price(self, client):
        response = client.post("/api/items", json={"name": "Bad", "price": -10})
        assert response.status_code == 422  # Pydantic validation error

    def test_create_item_missing_name(self, client):
        response = client.post("/api/items", json={"price": 10.00})
        assert response.status_code == 422


class TestListItems:
    """Tests for GET /api/items."""

    def test_list_empty(self, client):
        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_after_create(self, client, created_item):
        response = client.get("/api/items")
        assert len(response.json()) == 1

    def test_list_filter_by_status(self, client):
        client.post("/api/items", json={"name": "Active", "price": 10.00, "status": "active"})
        client.post("/api/items", json={"name": "Inactive", "price": 20.00, "status": "inactive"})

        active = client.get("/api/items?status=active")
        assert len(active.json()) == 1
        assert active.json()[0]["name"] == "Active"

        inactive = client.get("/api/items?status=inactive")
        assert len(inactive.json()) == 1
        assert inactive.json()[0]["name"] == "Inactive"


class TestGetItem:
    """Tests for GET /api/items/{id}."""

    def test_get_existing_item(self, client, created_item):
        item_id = created_item["id"]
        response = client.get(f"/api/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Widget"

    def test_get_nonexistent_item(self, client):
        response = client.get("/api/items/does-not-exist")
        assert response.status_code == 404


class TestDeleteItem:
    """Tests for DELETE /api/items/{id}."""

    def test_delete_existing_item(self, client, created_item):
        item_id = created_item["id"]
        response = client.delete(f"/api/items/{item_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/api/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_item(self, client):
        response = client.delete("/api/items/does-not-exist")
        assert response.status_code == 404