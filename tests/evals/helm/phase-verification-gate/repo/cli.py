import argparse

from slug import slugify


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Print the URL slug for an article title.")
    parser.add_argument("title")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print(args.title.lower())


if __name__ == "__main__":
    main()
