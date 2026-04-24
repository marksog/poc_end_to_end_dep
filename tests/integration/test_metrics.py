class TestMetricsEndpoint:
    """Tests for the /metrics Prometheus endpoint."""

    def test_metrics_endpoint_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_type(self, client):
        response = client.get("/metrics")
        assert "text/plain" in response.headers["content-type"] or \
               "text/plain" in response.headers.get("content-type", "")

    def test_metrics_include_request_counter(self, client):
        # Make a request first so the counter has data
        client.get("/health")
        response = client.get("/metrics")
        assert "http_requests_total" in response.text

    def test_metrics_include_duration_histogram(self, client):
        client.get("/health")
        response = client.get("/metrics")
        assert "http_request_duration_seconds" in response.text

    def test_metrics_track_different_status_codes(self, client):
        # Generate a 201
        client.post("/api/items", json={"name": "Test", "price": 10.0})
        # Generate a 404
        client.get("/api/items/nonexistent")
        # Generate a 200
        client.get("/api/items")

        response = client.get("/metrics")
        assert 'status_code="201"' in response.text
        assert 'status_code="404"' in response.text
        assert 'status_code="200"' in response.text