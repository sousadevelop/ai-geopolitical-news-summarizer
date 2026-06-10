from __future__ import annotations

from fastapi.testclient import TestClient


def test_sources_create_list_and_conflict(client: TestClient) -> None:
    payload = {
        "name": "Global Feed",
        "url": "https://feeds.example.com/global.xml",
        "region": "global",
        "language": "en",
        "enabled": True,
    }

    created = client.post("/sources", json=payload)
    assert created.status_code == 201
    source = created.json()
    assert source["name"] == "Global Feed"
    assert source["region"] == "global"

    listed = client.get("/sources", params={"region": "global", "enabled": "true"})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [source["id"]]

    conflict = client.post("/sources", json=payload)
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "source_conflict"
