"""Generate from a folder."""

import typing
import os
from datetime import datetime

from generate.substitute import Substitutor


def join(*args):
    """Use os.path.join one two or more inputs."""
    if len(args) == 1:
        return args[0]
    return os.path.join(args[0], join(*args[1:]))


def _sub(
    content: str,
    vars: typing.Dict[str, Substitutor] = {},
    loop_targets: typing.Dict[str, typing.List[Substitutor]] = {},
    extra_subs: typing.Callable[[str], str] = lambda x: x,
) -> str:
    """Make substitutions to a string."""
    from generate import parse

    c = parse(extra_subs(content))
    return c.substitute(vars=vars, loop_targets=loop_targets)


def generate(
    input_folder: str,
    output_folder: str,
    subdir: str = "",
    print_timing: bool = False,
    vars: typing.Dict[str, Substitutor] = {},
    loop_targets: typing.Dict[str, typing.List[Substitutor]] = {},
    extra_subs: typing.Callable[[str], str] = lambda x: x,
):
    """Make substitutions and copy all files recursively in a directory."""
    for file_ in os.listdir(join(input_folder, subdir)):
        file = join(subdir, file_)
        if file_ in ["__gen__.py", "__pycache__"] or file_.startswith("."):
            continue
        if os.path.isdir(join(input_folder, file)):
            os.mkdir(join(output_folder, file))
            generate(
                input_folder,
                output_folder,
                file,
                print_timing=print_timing,
                vars=vars,
                loop_targets=loop_targets,
                extra_subs=extra_subs,
            )
        elif file.endswith(".template"):
            with open(join(input_folder, file)) as f:
                content = f.read()
            _, metadata_, content = content.split("--\n", 2)
            metadata = {}
            for line in metadata_.strip().split("\n"):
                var, value = line.split(":", 1)
                metadata[var.strip()] = value.strip()
            var, loop_over = metadata["template"].split(" ", 1)
            for v, loop_items in loop_targets.items():
                if loop_over == f"in {v}":
                    for i in loop_items:
                        if print_timing:
                            start = datetime.now()
                            print(f"{file} [{i}]", end="", flush=True)
                        filename = _sub(
                            metadata["filename"],
                            vars={var: i, **vars},
                            loop_targets=loop_targets,
                            extra_subs=extra_subs,
                        ).strip()
                        with open(join(output_folder, subdir, filename), "w") as f:
                            f.write(
                                _sub(
                                    content,
                                    vars={var: i, **vars},
                                    loop_targets=loop_targets,
                                    extra_subs=extra_subs,
                                )
                            )
                        if print_timing:
                            end = datetime.now()
                            print(f" (completed in {(end - start).total_seconds():.2f}s)")
                    break
            else:
                raise ValueError(f"Unsupported loop: {loop_over}")
        else:
            if print_timing:
                start = datetime.now()
                print(file, end="", flush=True)
            with open(join(input_folder, file)) as f:
                content = f.read()
            with open(join(output_folder, file), "w") as f:
                f.write(_sub(content, vars=vars, loop_targets=loop_targets, extra_subs=extra_subs))
            if print_timing:
                end = datetime.now()
                print(f" (completed in {(end - start).total_seconds():.2f}s)")
