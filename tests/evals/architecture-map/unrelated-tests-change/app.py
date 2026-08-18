def handle_request(payload: dict) -> dict:
    return {"ok": True, "id": payload.get("id")}


if __name__ == "__main__":
    print(handle_request({"id": 1}))
