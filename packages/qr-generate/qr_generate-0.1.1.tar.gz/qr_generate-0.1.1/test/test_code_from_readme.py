import generate
import os
import sys


def test_looping_in_a_file():
    template = "{{for v in values}}\nprint({{v}})\n{{end for}}"

    t = generate.parse(template)
    values = [generate.substitute.Float(i) for i in [1.0, 4.0, 6.0]]
    output = t.substitute(loop_targets={"values": values})

    assert output == "print(1.0)\nprint(4.0)\nprint(6.0)\n"


def test_folder_templating():
    path = os.path.dirname(os.path.realpath(__file__))
    i = os.path.join(path, "input_dir")
    o = os.path.join(path, "output_dir")
    assert os.system(f"{sys.executable} -m generate {i} {o} --clear-output-dir") == 0

    assert set(os.listdir(o)) == {"code.py", "p-1.0.py", "p-4.0.py", "p-6.0.py"}
    with open(os.path.join(o, "code.py")) as f:
        assert f.read() == "print(1.0)\nprint(4.0)\nprint(6.0)\n"

    for n in ["1.0", "4.0", "6.0"]:
        with open(os.path.join(o, f"p-{n}.py")) as f:
            assert f.read() == f"print({n})\n"
