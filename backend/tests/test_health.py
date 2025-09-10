import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, engine
from main import app

# Créer les tables une seule fois pour la session de tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_endpoint():
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'healthy'
    assert 'version' in data

@pytest.mark.parametrize('path', ['/api/v1', '/'])
def test_root_and_api_prefix(path):
    r = client.get(path)
    assert r.status_code in (200, 404)  # /api/v1 peut ne pas avoir d'index direct
