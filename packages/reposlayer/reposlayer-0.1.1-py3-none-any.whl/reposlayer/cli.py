import argparse
import os
import commands


def main():
    # Instantiate the parser
    parser = argparse.ArgumentParser(
        prog="reposlayer",
        description="Python repository manager",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Valid subcommands",
        help="Additional help",
        dest="command",
    )
    subparsers.required = True

    count_parser = subparsers.add_parser(
        "count", help="Count lines of code in a file or directory"
    )

    count_parser.add_argument(
        "path",
        type=str,
        nargs="?",
        help="Path to file or directory",
        default=os.getcwd(),
    )

    count_parser.add_argument(
        "--ignore",
        nargs="*",
        action="append",
        help="""List of files or directories to ignore,
          in addition to your .gitignore file""",
    )

    count_parser.add_argument(
        "--ignore-blank-lines", action="store_true", help="Ignore blank lines"
    )

    count_parser.add_argument(
        "--count-lines", action="store_true", help="Count lines of code"
    )

    count_parser.add_argument(
        "--count-chars", action="store_true", help="Count characters of code"
    )

    count_parser.set_defaults(func=commands.handle_count)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()