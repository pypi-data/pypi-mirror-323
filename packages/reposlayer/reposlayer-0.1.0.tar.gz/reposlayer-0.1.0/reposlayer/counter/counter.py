from pathlib import Path
import subprocess
import os


class Counter:
    def __init__(
        self,
        dir_path,
        ignore,
        ignore_blank_lines=False,
        count_lines=True,
        count_chars=True,
    ):
        self.dir_path = dir_path

        self.ignore = (
            set({".git", ".gitignore", ".DS_Store"}.update(ignore))
            if ignore
            else {".git", ".gitignore", ".DS_Store"}
        )
        self.ignore_blank_lines = ignore_blank_lines
        self.count_lines = count_lines
        self.count_chars = count_chars
        self.lines_count = 0
        self.char_count = 0

    def count_dir(self):
        if not os.path.exists(self.dir_path):
            print(f"{self.dir_path} not found")
            return
        if not os.path.isdir(self.dir_path):
            print(f"{self.dir_path} is not a directory")
            return
        print(f"Counting lines of code in {self.dir_path}")
        for root, dirs, files in os.walk(self.dir_path):
            root_path = Path(root)
            if check_ignore(root_path, self.ignore):
                dirs[:] = []  # ignore this directory and its subdirectories
                continue
            for file in files:
                file_path = root_path / file
                if check_ignore(file_path, self.ignore):
                    continue
                self.lines_count += count_file(file_path)
        print(f"Total lines of code: {self.lines_count} in {self.dir_path}")


def check_ignore(file_path, ignore):
    for ign in ignore:
        if ign in str(file_path):
            return True
    result = subprocess.run(
        ["/usr/bin/git", "check-ignore", str(file_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0


def count_file(file_path, ignore_blank_lines=False):
    lines = 0
    try:
        # skipcq: PTC-W6004
        with open(file_path) as f:
            for line in f:
                if line.strip() == "":
                    if ignore_blank_lines:
                        continue
                    lines += 1
                lines += 1
            print(f"{file_path}: {lines} lines")
            return lines
    except Exception as e:
        print(f"{file_path} not found, thrown error: {e}")
        return 0
