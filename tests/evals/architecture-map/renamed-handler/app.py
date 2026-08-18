def process_v2(payload: dict) -> dict:
    return {"result": payload.get("value", 0) * 2}


def audit_log(entry: dict) -> None:
    print(entry)


def handle_request(payload: dict) -> dict:
    audit_log({"source": "api"})
    return process_v2(payload)


if __name__ == "__main__":
    print(handle_request({"value": 3}))
