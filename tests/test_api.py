"""REST API tests with requests + pytest."""
import pytest

pytestmark = pytest.mark.api

TRACK_FIELDS = {"id": int, "range_m": float, "azimuth_deg": float,
                "velocity_mps": float, "classification": str}


def test_health_returns_ok(api):
    resp = api.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_tracks_match_schema(api):
    tracks = api.get("/api/tracks").json()
    assert tracks, "expected at least one track"
    for track in tracks:
        assert set(track) == set(TRACK_FIELDS), f"unexpected fields in {track}"
        for field, kind in TRACK_FIELDS.items():
            assert isinstance(track[field], kind), f"{field} should be {kind.__name__}"


def test_tracks_values_are_physically_valid(api):
    for track in api.get("/api/tracks").json():
        assert track["range_m"] > 0
        assert 0 <= track["azimuth_deg"] < 360
        assert track["velocity_mps"] >= 0


def test_track_ids_are_unique(api):
    ids = [t["id"] for t in api.get("/api/tracks").json()]
    assert len(ids) == len(set(ids))


def test_login_success_returns_token(api):
    resp = api.post("/api/login", json={"username": "operator", "password": "radar123"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "operator"
    assert len(resp.json()["token"]) == 16


@pytest.mark.parametrize("username, password, expected_status", [
    ("operator", "wrong", 401),   # bad password
    ("nobody", "radar123", 401),  # unknown user
    ("", "radar123", 400),        # missing username
    ("operator", "", 400),        # missing password
])
def test_login_rejects_bad_input(api, username, password, expected_status):
    resp = api.post("/api/login", json={"username": username, "password": password})
    assert resp.status_code == expected_status
    assert "error" in resp.json()


def test_unknown_route_is_404(api):
    assert api.get("/api/does-not-exist").status_code == 404
