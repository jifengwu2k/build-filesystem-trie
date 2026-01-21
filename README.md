# `build-filesystem-trie`

Programmatically generate a trie representing a section of the filesystem, closely matching what the UNIX `tree` command
outputs.

For both file or directory paths, absolute or relative, the function returns a tuple containing:

- The absolute path components of the directory containing the file or directory.
- The trie rooted at the specified path, whether that path points to a file or a directory.

Trie Node Semantics:

- All nodes have a `value` (the file or directory name).
- All nodes have an `is_end` flag: `True` if the node represents a file, `False` for a directory.
- Directory nodes have a `.children` dict mapping containing file and directory names to child nodes.

## Installation

```commandline
pip install build-filesystem-trie
```

## Example

Suppose the file layout is:

```
- testdir/
  - file1.txt
  - subdir/
    - file2.txt
```

Running

```python
from build_filesystem_trie import build_filesystem_trie, iterate_relative_path_components_is_dir_tuples

prefix, trie = build_filesystem_trie('testdir')

for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(trie):
    print(
        '%s- %s%s' % (
            '  ' * (len(relative_path_components) - 1),
            relative_path_components[-1],
            '/' if is_dir else '',
        )
    )
```

prints:

```
- testdir/
  - file1.txt
  - subdir/
    - file2.txt
```

- `prefix` will contain the absolute path components of **the directory containing `testdir`**.
- `trie` will be a `TrieNode` named `testdir`, with `is_end == False` and children `TrieNode`s named `file1.txt` and `subdir`, representing the full directory structure under `testdir`.

> By default, skips dotted (hidden) files and directories in a directory.
> 
> To recurse dotted (hidden) files and directories in a directory, pass the argument `recurse_dotted=True`

- `relative_path_components` will contain the relative path components of a file or directory, **relative to the directory containing `testdir`**.
  - It is possible to use `os.path.join(*prefix, *relative_path_components)` to obtain the absolute path of the file or directory.
- `is_dir` is `False` for files and `True` for directories.

This is analogous to the output of the UNIX `tree` command.

## Command-line Usage

You can also print a tree from the command line:

```bash
python -m build_filesystem_trie path/to/your/file_or_directory
```

By default, it skips dotted (hidden) files and directories.  
To include hidden files/directories, use:

```bash
python -m build_filesystem_trie path/to/dir --recurse-dotted
```

Example output:

```
- testdir/
  - file1.txt
  - subdir/
    - file2.txt
```

To generate a **YAML filesystem tree**, use:

```bash
python -m build_filesystem_trie path/to/dir --yaml
```

Example output:

```yaml
- "testdir":
  - "file1.txt"
  - "subdir":
    - "file2.txt"
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).