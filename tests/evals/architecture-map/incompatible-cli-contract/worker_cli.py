import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    subcommands = parser.add_subparsers(dest="command", required=True)
    export = subcommands.add_parser("export", allow_abbrev=False)
    export.add_argument("output")
    export.add_argument("--output-format", choices=("json", "csv"), default="json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(f"exported {args.output_format} to {args.output}")


if __name__ == "__main__":
    main()
