from fastapi.testclient import TestClient
from api.main import app
client=TestClient(app)
def test_health():
    assert client.get('/health').json()=={'status':'ok'}
def test_empty_payload():
    assert client.post('/analyze',json={'events':[]}).status_code==422
def test_prediction():
    payload={'events':[{'timestamp':'2026-10-24T08:00:00Z','level':'ERROR','service':'web','status':503,'duration_ms':3000,'bytes_sent':1200,'message':'Gateway timeout'}]}
    r=client.post('/analyze',json=payload)
    assert r.status_code==200,r.text
    assert r.json()['total']==1
    assert isinstance(r.json()['events'][0]['is_anomaly'],bool)
