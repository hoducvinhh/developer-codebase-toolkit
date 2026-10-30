"""Directory structure analysis and tree generation."""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from toolkit_common.filesystem.walker import SafeWalker


class TreeNode(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int = 0
    file_count: int = 0
    children: List["TreeNode"] = Field(default_factory=list)


def build_tree(root_dir: str | Path, max_depth: Optional[int] = 3) -> TreeNode:
    """Build a hierarchical tree node structure up to max_depth."""
    root = Path(root_dir).resolve()
    walker = SafeWalker(root=root, max_depth=max_depth)

    all_files = list(walker.walk_files())
    root_node = TreeNode(name=root.name or str(root), path=str(root), is_dir=True)
    dirs: Dict[Path, TreeNode] = {root: root_node}

    for f in all_files:
        rel = f.relative_to(root)
        current = root
        for part in rel.parts[:-1]:
            parent_dir = current
            current = current / part
            if current not in dirs:
                node = TreeNode(name=part, path=str(current), is_dir=True)
                dirs[current] = node
                dirs[parent_dir].children.append(node)
            dirs[current].file_count += 1
        root_node.file_count += 1

        try:
            size = f.stat().st_size
        except OSError:
            size = 0

        file_node = TreeNode(name=f.name, path=str(f), is_dir=False, size=size)
        dirs[current].children.append(file_node)

    return root_node
