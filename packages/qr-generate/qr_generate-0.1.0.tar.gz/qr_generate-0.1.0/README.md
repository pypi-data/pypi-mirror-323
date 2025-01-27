# Generate files from templates

This code can be used to generate plain text files from templates.

## Examples

### Looping in a file
To generate a file that prints each value in a list, the following template can be written:

```python
template = """{{for v in values}}
print({{v}})
{{end for}}"""
```

A python script can then be used to generate the file:

```python
import generate

t = generate.parse(template)
values = [
    generate.substitute.Float(i)
    for i in [1.0, 4.0, 6.0]
]
print(t.substitute(loop_targets={"values": values}))
```

The items in the list `values` passed in as a loop target must be a subclass of
[Substitutor](generator/substitute.py).

### Templating with a folder

Alternatively, you could create a folder called `input_code` and create a file inside it containing the file `code.py` with contents:

```python
{{for v in values}}
print({{v}})
{{end for}}
```

and create a file in the directory called `__gen__.py` with contents:

```python
import generate
loop_targets = {"values": [
    generate.substitute.Float(i)
    for i in [1.0, 4.0, 6.0]
]}
```

You can then run:

```bash
python -m generate input_code output_code
```

This would create a directory called `output_code` containing a file `code.py` with the template replacements having been made.

### Generating multiple files from a .template file

When templating using a folder, a file for each entry in a list can be created by using a .template file. For example, if a file called
`p.template` was added to the `input_code` directory with the contents

```python
--
template: v in values
filename: p-{{v}}.py
--
print({{v}})
```

You can then run:

```bash
python -m generate input_code output_code
```

This would generate files called `p-1.0.py`, `p-4.0py`, and `p-6.0.py`.
