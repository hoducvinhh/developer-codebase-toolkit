"""OpenAPI 3.0 and 3.1 parser with recursive $ref resolver."""

import copy
import json
from pathlib import Path
from typing import Any, Dict

import yaml


class OpenApiParser:
    """Parses OpenAPI documents from JSON or YAML and resolves $ref pointers."""

    def __init__(self, spec: Dict[str, Any]):
        self.raw_spec = spec
        self.resolved_spec = self._resolve_refs(copy.deepcopy(spec), spec)

    @classmethod
    def from_file(cls, path: str | Path) -> "OpenApiParser":
        p = Path(path).resolve()
        if not p.is_file():
            raise FileNotFoundError(f"OpenAPI spec not found: {p}")
        text = p.read_text(encoding="utf-8")
        if p.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
        return cls(data)

    def _resolve_pointer(self, ref: str, root_doc: Dict[str, Any]) -> Any:
        if not ref.startswith("#/"):
            return None
        parts = ref[2:].split("/")
        curr = root_doc
        for part in parts:
            part = part.replace("~1", "/").replace("~0", "~")
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return None
        return curr

    def _resolve_refs(self, node: Any, root_doc: Dict[str, Any], seen_refs: set = None) -> Any:
        if seen_refs is None:
            seen_refs = set()

        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                ref_str = node["$ref"]
                if ref_str in seen_refs:
                    # Circular reference guard
                    return {"$ref": ref_str, "type": "object", "circular": True}
                target = self._resolve_pointer(ref_str, root_doc)
                if target is not None:
                    seen_refs.add(ref_str)
                    resolved = self._resolve_refs(copy.deepcopy(target), root_doc, seen_refs)
                    seen_refs.remove(ref_str)
                    return resolved

            return {k: self._resolve_refs(v, root_doc, seen_refs) for k, v in node.items()}
        elif isinstance(node, list):
            return [self._resolve_refs(item, root_doc, seen_refs) for item in node]
        return node
