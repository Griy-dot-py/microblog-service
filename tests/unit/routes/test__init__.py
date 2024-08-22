from fastapi.testclient import TestClient


def test_not_found_handler(client: TestClient, users: list[dict]):
    unexisting_id = sum(u["id"] for u in users)
    
    response = client.get(f"/api/users/{unexisting_id}")
    assert response.status_code == 404


def test_not_own_handler(client: TestClient, users: list[dict], tweets: list[dict]):
    for u in users:
        for tw in tweets:
            if tw["author_id"] != u["id"]:
                user = u
                tweet = tw
                break
    
    response = client.delete(f"/api/tweets/{tweet["id"]}", headers={"api-key": user["api_key"]})
    assert response.status_code == 403
