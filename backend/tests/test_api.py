import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seeder import seed_database_if_empty

# Ensure database tables and benchmark seeds exist for tests
init_db()
seed_database_if_empty()

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "FastAPI" in data["service"]


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_get_providers():
    response = client.get("/api/products/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    stores = [p["store"] for p in data]
    assert "AMAZON" in stores
    assert "FLIPKART" in stores


def test_search_empty_returns_seeded_catalog():
    response = client.get("/api/products/search?query=")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["totalFound"] >= 1
    names = [r["productName"] for r in data["results"]]
    assert any("MacBook" in n or "iPhone" in n for n in names)


def test_get_product_details():
    response = client.get("/api/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["productId"] == 1
    assert "stores" in data
    assert len(data["stores"]) >= 1
    assert data["recommendation"] is not None


def test_get_product_history():
    response = client.get("/api/products/1/history")
    assert response.status_code == 200
    data = response.json()
    assert data["productId"] == 1
    assert "points" in data
    assert len(data["points"]) >= 1


def test_tracking_crud():
    track_req = {
        "storeProductId": 1,
        "userEmail": "test@example.com",
        "targetPrice": 70000.0,
        "targetDropPercentage": 5.0
    }
    headers = {"Authorization": "Bearer test-token-user-123"}
    resp = client.post("/api/tracking", json=track_req, headers=headers)
    assert resp.status_code == 200
    tracked = resp.json()
    tracking_id = tracked["id"]
    assert tracked["targetPrice"] == 70000.0

    list_resp = client.get("/api/tracking", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(i["id"] == tracking_id for i in items)

    check_resp = client.post(f"/api/tracking/{tracking_id}/check-now", headers=headers)
    assert check_resp.status_code == 200

    del_resp = client.delete(f"/api/tracking/{tracking_id}", headers=headers)
    assert del_resp.status_code == 204


def test_search_history_lifecycle():
    headers = {"Authorization": "Bearer test-token-user-456"}

    hist_req = {
        "query": "iPhone 15",
        "resultCount": 3,
        "topProductName": "iPhone 15",
        "topProductPrice": 65999.0,
        "topProductStore": "AMAZON"
    }
    post_resp = client.post("/api/history", json=hist_req, headers=headers)
    assert post_resp.status_code == 201

    get_resp = client.get("/api/history", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert any(h["query"] == "iPhone 15" for h in data)

    del_resp = client.delete("/api/history", headers=headers)
    assert del_resp.status_code == 204


def test_ai_prediction():
    response = client.get("/api/ai/predict/1")
    assert response.status_code == 200
    data = response.json()
    assert "aiDealScore" in data
    assert "recommendation" in data
    assert "confidence" in data


def test_ai_title_matching():
    payload = {
        "title_a": "Apple iPhone 15 (128 GB) - Black",
        "title_b": "Apple iPhone 15 128GB Black 5G Smartphone"
    }
    response = client.post("/api/ai/match-titles", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["isMatch"] is True


def test_search_domain_accuracy():
    response = client.get("/api/products/search?q=Kurtha+Sets")
    assert response.status_code == 200
    data = response.json()
    assert data["totalFound"] > 0
    first = data["results"][0]
    assert "Ethnic" in first["category"]
    assert "photo-1526170375885-4d8ecf77b99f" not in first["imageUrl"]
    assert first["lowestPrice"] > 0
    # Stores must have Amazon and Flipkart LIVE
    stores = {s["store"]: s for s in first["stores"]}
    assert "AMAZON" in stores
    assert "FLIPKART" in stores
    assert stores["AMAZON"]["status"] == "LIVE"
    assert stores["FLIPKART"]["status"] == "LIVE"
