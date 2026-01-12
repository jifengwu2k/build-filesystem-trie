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

## Example

Suppose the file layout is:

```
testdir/
  file1.txt
  subdir/
    file2.txt
```

Calling

```python
from build_filesystem_trie import build_filesystem_trie

prefix, trie = build_filesystem_trie('testdir')
```

- `prefix` will contain the absolute path components of the directory containing `testdir`.
- `trie` will be a TrieNode named `testdir`, with `is_end == False` and children `file1.txt` and `subdir`, and so on,
  representing the full directory structure under `testdir`.

Calling

```python
from build_filesystem_trie import build_filesystem_trie

prefix, trie = build_filesystem_trie('testdir/file1.txt')
```

- `prefix` will contain the absolute path components of the directory containing `testdir/file1.txt`.
- `trie` will be a TrieNode named `file1.txt`, with `is_end == True`.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).