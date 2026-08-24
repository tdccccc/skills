from api import handle_export


def main() -> None:
    status, body = handle_export()
    print(f"{status}: {body}")


if __name__ == "__main__":
    main()
