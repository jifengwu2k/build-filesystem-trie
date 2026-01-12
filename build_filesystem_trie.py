import errno
import sys
from os import getcwd, listdir
from os.path import exists, isdir, join, split

from cowlist import COWList
from fspathverbs import Root, Parent, Current, Child, compile_to_fspathverbs
from tinytrie import TrieNode
from typing import Tuple

if sys.version_info < (3,):
    FileNotFoundError = IOError


def build_filesystem_trie(
        path,  # type: str
):
    # type: (...) -> Tuple[COWList[str], TrieNode[str, str]]
    """
    Programmatically generate a trie representing a section of the filesystem, closely matching what the UNIX `tree` command outputs.

    Args:
        path (str): Path to either a file or directory, absolute or relative.

    Returns:
        Tuple[COWList[str], TrieNode[str, str]]:
            - prefix (COWList[str]): The absolute path components of the directory containing the file or directory.
            - trie (TrieNode): The trie rooted at the specified path, whether that path points to a file or a directory.

    Example:
        prefix, trie = extract_prefix_and_build_filesystem_trie_from_path('some/directory/or/file')
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
                child_root = build_filesystem_trie_from_absolute_path_components(abspath_components.append(child))
                root.children[child] = child_root
        else:
            root = TrieNode()
            root.value = name
            root.is_end = True

        return root

    return absolute_path_components[:-1], build_filesystem_trie_from_absolute_path_components(absolute_path_components)
