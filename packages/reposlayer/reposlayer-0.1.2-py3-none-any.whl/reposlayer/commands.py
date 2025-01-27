from counter.counter import Counter


def handle_count(args):
    counter_obj = Counter(
        dir_path=args.path,
        ignore=args.ignore,
        ignore_blank_lines=args.ignore_blank_lines,
        count_lines=args.count_lines,
        count_chars=args.count_chars,
    )
    counter_obj.count_dir()
