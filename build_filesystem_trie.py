import argparse
import errno
import json
import sys
from os import getcwd, listdir
from os.path import exists, isdir, join, split

from cowlist import COWList
from fspathverbs import Root, Parent, Current, Child, compile_to_fspathverbs
from tinytrie import TrieNode
from typing import Iterable, Tuple

if sys.version_info < (3,):
    FileNotFoundError = IOError


def build_filesystem_trie(
        path,  # type: str
        recurse_dotted=False,  # type: bool
):
    # type: (...) -> Tuple[COWList[str], TrieNode[str, str]]
    """
    Programmatically generate a trie representing a section of the filesystem, closely matching what the UNIX `tree` command outputs.

    Args:
        path (str): Path to either a file or directory, absolute or relative.
        recurse_dotted (bool, default False): Whether to recurse dotted (hidden) files and directories in a directory.

    Returns:
        Tuple[COWList[str], TrieNode[str, str]]:
            - prefix (COWList[str]): The absolute path components of the directory containing the file or directory.
            - trie (TrieNode): The trie rooted at the specified path, whether that path points to a file or a directory.
    """
    if not exists(path):
        raise FileNotFoundError(errno.ENOENT, 'No such file or directory: %s' % (path,))

    verbs = []
    verbs.extend(compile_to_fspathverbs(getcwd(), split))
    verbs.extend(compile_to_fspathverbs(path, split))

    absolute_path_components = COWList()
    for verb in verbs:
        if isinstance(verb, Root):
            absolute_path_components = COWList([verb.root])
        elif isinstance(verb, Parent):
            absolute_path_components, _ = absolute_path_components.pop()
        elif isinstance(verb, Current):
            pass
        elif isinstance(verb, Child):
            absolute_path_components = absolute_path_components.append(verb.child)

    def build_filesystem_trie_from_absolute_path_components(
            abspath_components,  # type: COWList[str]
    ):
        # type: (...) -> TrieNode[str, str]
        name = abspath_components[-1]
        abspath = join(*abspath_components)
        if isdir(abspath):
            root = TrieNode()
            root.value = name
            root.is_end = False
            children = listdir(abspath)
            for child in children:
                if not child.startswith('.') or recurse_dotted:
                    child_root = build_filesystem_trie_from_absolute_path_components(abspath_components.append(child))
                    root.children[child] = child_root
        else:
            root = TrieNode()
            root.value = name
            root.is_end = True

        return root

    return absolute_path_components[:-1], build_filesystem_trie_from_absolute_path_components(absolute_path_components)


def iterate_relative_path_components_is_dir_tuples(
        filesystem_trie_node,  # type: TrieNode[str, str]
        accumulated_relative_path_components=COWList(),  # type: COWList[str]
):
    # type: (...) -> Iterable[Tuple[COWList[str], bool]]
    """
    Recursively yields (relative_path_components, is_dir) tuples for each node in a filesystem trie.

    Args:
        filesystem_trie_node (TrieNode): Root node of the filesystem trie.
        accumulated_relative_path_components (COWList[str], optional): The accumulated relative path components to the current node (excluding the current node).

    Yields:
        Tuple[COWList[str], bool]:
            - relative_path_components: The path components from the trie root to the current node (relative to the prefix returned by build_filesystem_trie).
            - is_dir: False if the node represents a file; True if it represents a directory.

    Example:
        for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(trie):
            print("Is dir:", is_dir, "Components:", list(relative_path_components))
    """
    name = filesystem_trie_node.value
    is_file = filesystem_trie_node.is_end

    relative_path_components = accumulated_relative_path_components.append(name)
    yield relative_path_components, not is_file
    for child_filesystem_trie_node in filesystem_trie_node.children.values():
        for child_relative_path_components, child_is_dir in iterate_relative_path_components_is_dir_tuples(
                filesystem_trie_node=child_filesystem_trie_node,
                accumulated_relative_path_components=relative_path_components,
        ):
            yield child_relative_path_components, child_is_dir


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print a filesystem tree, analogous to `tree` command.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='File or directory path (absolute or relative). Defaults to current directory.'
    )
    parser.add_argument(
        '--recurse-dotted', action='store_true',
        help='Include dotted (hidden) files and directories.'
    )
    parser.add_argument(
        '--yaml', action='store_true',
        help='Print output as YAML-compatible structure.'
    )
    args = parser.parse_args()

    try:
        prefix, trie = build_filesystem_trie(
            args.path,
            recurse_dotted=args.recurse_dotted
        )
    except Exception as e:
        parser.error(str(e))

    if args.yaml:
        for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(trie):
            print(
                '%s- %s%s' % (
                    '  ' * (len(relative_path_components) - 1),
                    json.dumps(relative_path_components[-1]),
                    ':' if is_dir else '',
                )
            )
    else:
        for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(trie):
            print(
                '%s- %s%s' % (
                    '  ' * (len(relative_path_components) - 1),
                    relative_path_components[-1],
                    '/' if is_dir else '',
                )
            )