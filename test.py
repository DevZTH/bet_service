# %%
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


response = client.get("/bets")
assert response.status_code == 200


response = client.post("/bets", json = {"amount":10.00, "event_id":"test1" } )
assert response.status_code == 200
print(response.json()['message'])
assert response.json()['message'] == 'bet added'


response = client.put("/events/test1", json={"status":"WIN"})
assert response.status_code == 200


response = client.put("/events/test1", json={"status":"incorrect"})
assert response.status_code == 422

# %%
