"""Generate files from templates in a directory."""

import argparse
import os
import shutil
import sys

from generate.folder import generate

parser = argparse.ArgumentParser(description="Generate files from templates in a directory")
parser.add_argument("input_dir", metavar="input_dir", nargs=1, default=None, help="Input directory")
parser.add_argument(
    "output_dir", metavar="output_dir", nargs=1, default=None, help="Output directory"
)
parser.add_argument("--clear-output-dir", action="store_true", help="Clear the output directory")
parser.add_argument("--print-timing", action="store_true", help="Print timing for every file")
args = parser.parse_args()

input_dir = args.input_dir[0]
output_dir = args.output_dir[0]

if os.path.isdir(output_dir):
    if args.clear_output_dir:
        shutil.rmtree(output_dir)
    else:
        print("output_dir exists. Rerun with --clear-output-dir")
        exit()

os.mkdir(output_dir)

sys.path.append(input_dir)
try:
    from __gen__ import vars
except (ImportError, FileNotFoundError):
    vars = {}
try:
    from __gen__ import loop_targets
except (ImportError, FileNotFoundError):
    loop_targets = {}
try:
    from __gen__ import extra_subs
except (ImportError, FileNotFoundError):

    def extra_subs(x):
        """Extra substitutions."""
        return x


generate(
    input_dir,
    output_dir,
    vars=vars,
    loop_targets=loop_targets,
    extra_subs=extra_subs,
    print_timing=args.print_timing,
)
