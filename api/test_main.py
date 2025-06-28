from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_qr_valid():
    response = client.post("/generate-qr/", json={"url": "http://example.com"})
    assert response.status_code == 200
    assert "qr_code_base64" in response.json()
    assert response.json()["qr_code_base64"].startswith("iVBOR")  # PNG magic header

def test_generate_qr_invalid_url():
    response = client.post("/generate-qr/", json={"url": "invalid-url"})
    assert response.status_code == 422  # Should fail validation

def test_generate_qr_missing_url():
    response = client.post("/generate-qr/", json={})
    assert response.status_code == 422  # Missing 'url' field