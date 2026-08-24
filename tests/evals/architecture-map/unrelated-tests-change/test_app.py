from app import handle_request


def test_handle_request():
    assert handle_request({"id": 1}) == {"ok": True, "id": 1}
