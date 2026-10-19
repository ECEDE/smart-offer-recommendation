import os
import tempfile
from fastapi.testclient import TestClient

# Set isolated test DB before importing the app.
_tmp=tempfile.TemporaryDirectory()
os.environ["SMART_OFFER_DB"] = os.path.join(_tmp.name,"test.db")
from app.main import app, initialize, eligible_tariffs
initialize()
client=TestClient(app)

def test_health():
    assert client.get("/health").json()=={"status":"ok"}

def test_customer_seed():
    assert len(client.get("/customers").json())==30
    assert client.get("/customers/999").status_code==404

def test_eligibility_boundaries():
    customer={"current_gb":20,"current_price":300,"usage_gb":15}
    tariffs=[{"id":i,"gb":gb,"price":400,"active":1} for i,gb in enumerate([14,15,20,25,26],1)]
    assert [x["gb"] for x in eligible_tariffs(customer,tariffs)]==[15,20,25]

def test_recommend_and_accept():
    result=client.post("/customers/1/recommendations").json()
    assert "run_id" in result
    assert len(result["offers"])<=4
    if result["offers"]:
        tariff=result["offers"][0]
        path=f"/recommendation-runs/{result['run_id']}/acceptances"
        assert client.post(path,json={"tariff_id":tariff["tariff_id"]}).status_code==200
        assert client.post(path,json={"tariff_id":tariff["tariff_id"]}).status_code==409
    assert client.get("/dashboard/metrics").status_code==200
