import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_optimize_scenarios(client: TestClient):
    """Test optimization endpoint."""
    response = client.post(
        "/api/v1/optimization/optimize",
        json={
            "brief": "Maximize sales for TV department",
            "constraints": {
                "max_discount": 25.0,
                "departments": ["TV"],
                "channels": ["online", "store"]
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "discount_percentage" in data[0]


def test_calculate_frontier(client: TestClient):
    """Test efficient frontier calculation."""
    scenarios = [
        {
            "id": "scenario-1",
            "name": "Conservative",
            "date_range": {
                "start_date": "2024-10-01",
                "end_date": "2024-10-07"
            },
            "departments": ["TV"],
            "channels": ["online"],
            "discount_percentage": 10.0
        },
        {
            "id": "scenario-2",
            "name": "Aggressive",
            "date_range": {
                "start_date": "2024-10-01",
                "end_date": "2024-10-07"
            },
            "departments": ["TV"],
            "channels": ["online"],
            "discount_percentage": 20.0
        }
    ]
    
    response = client.post("/api/v1/optimization/frontier", json=scenarios)
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert "coordinates" in data
    assert "pareto_optimal" in data
    assert len(data["coordinates"]) == 2


def test_rank_scenarios(client: TestClient):
    """Test scenario ranking endpoint."""
    scenarios = [
        {
            "id": "scenario-1",
            "name": "Conservative",
            "date_range": {
                "start_date": "2024-10-01",
                "end_date": "2024-10-07"
            },
            "departments": ["TV"],
            "channels": ["online"],
            "discount_percentage": 10.0
        },
        {
            "id": "scenario-2",
            "name": "Aggressive",
            "date_range": {
                "start_date": "2024-10-01",
                "end_date": "2024-10-07"
            },
            "departments": ["TV"],
            "channels": ["online"],
            "discount_percentage": 20.0
        }
    ]
    
    response = client.post(
        "/api/v1/optimization/rank",
        json={
            "scenarios": scenarios,
            "weights": {"sales": 0.6, "margin": 0.4}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "ranked_scenarios" in data
    assert "rationale" in data
    assert len(data["ranked_scenarios"]) == 2
