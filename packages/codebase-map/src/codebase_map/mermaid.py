"""Mermaid architecture diagram generator."""

import re
from typing import List

from codebase_map.dependencies import DependencyGraph
from codebase_map.modules import ModuleInfo


def sanitize_id(raw: str) -> str:
    """Sanitize identifier for Mermaid diagram node ID."""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", raw)
    if clean and clean[0].isdigit():
        clean = "node_" + clean
    return clean or "node"


def generate_mermaid_diagram(
    graph: DependencyGraph,
    modules: List[ModuleInfo],
    direction: str = "TD",
) -> str:
    """Generate Mermaid flowchart diagram from dependency graph and modules."""
    lines = [f"flowchart {direction}"]

    # Subgraph for logical modules
    module_node_ids = set()
    for mod in modules:
        mod_id = sanitize_id(f"subgraph_{mod.name}")
        lines.append(f"    subgraph {mod_id} [\"{mod.name} ({mod.role})\"]")
        for f in mod.files:
            file_full = f"{mod.name}/{f}" if mod.name != "." else f
            file_id = sanitize_id(file_full)
            module_node_ids.add(file_id)
            lines.append(f"        {file_id}[\"{f}\"]")
        lines.append("    end")

    # Render top internal dependency links
    seen_links = set()
    for edge in graph.edges:
        if edge.is_internal:
            src_id = sanitize_id(edge.source)
            tgt_id = sanitize_id(edge.target)
            link_key = (src_id, tgt_id)
            if link_key not in seen_links:
                seen_links.add(link_key)
                lines.append(f"    {src_id} --> {tgt_id}")

    # External dependencies node
    if graph.external_packages:
        lines.append("    subgraph external_deps [\"External Dependencies\"]")
        for pkg in sorted(graph.external_packages)[:10]:  # limit top 10
            pkg_id = sanitize_id(f"ext_{pkg}")
            lines.append(f"        {pkg_id}[(\"{pkg}\")]")
        lines.append("    end")

    return "\n".join(lines)
