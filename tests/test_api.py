"""API tests for app.py using FastAPI's TestClient (run after train.py)."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
FEATURES = json.loads(Path('config.json').read_text())['features']

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_metrics_endpoint():
    r = client.get('/metrics')
    assert r.status_code == 200
    body = r.json()
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in body
    assert body['student_id'] == 'FA23-BDS-025'

def test_predict_returns_one_label_per_record():
    records = [{f: 0.5 for f in FEATURES}, {f: -1.5 for f in FEATURES}]
    r = client.post('/predict', json={'records': records})
    assert r.status_code == 200
    body = r.json()
    assert len(body['predictions']) == 2
    assert set(body['predictions']) <= {0, 1}
    assert all(0.0 <= p <= 1.0 for p in body['probabilities'])

def test_predict_rejects_empty_request():
    r = client.post('/predict', json={'records': []})
    assert r.status_code == 422
