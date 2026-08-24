from legacy_transform import transform


def handle_request(payload: str) -> str:
    return transform(payload)


def main() -> None:
    print(handle_request("daily papers"))


if __name__ == "__main__":
    main()
