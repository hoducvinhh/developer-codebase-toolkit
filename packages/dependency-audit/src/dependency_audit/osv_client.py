"""OSV (Open Source Vulnerabilities) API client with offline caching."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from dependency_audit.models import DependencyItem, Vulnerability

OSV_API_URL = "https://api.osv.dev/v1/query"


class OsvClient:
    """Client for OSV API with disk caching for offline operation."""

    def __init__(self, cache_file: Optional[Path] = None, offline: bool = False):
        self.cache_file = cache_file or Path(".osv_cache.json")
        self.offline = offline
        self.cache: Dict[str, List[Dict[str, Any]]] = self._load_cache()

    def _load_cache(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.cache_file.is_file():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_cache(self) -> None:
        try:
            self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")
        except Exception:
            pass

    def check_vulnerabilities(self, items: List[DependencyItem]) -> List[Vulnerability]:
        """Check a list of dependency items for known vulnerabilities."""
        vulnerabilities: List[Vulnerability] = []

        for item in items:
            if not item.version or item.version in ("latest", "unknown"):
                continue

            cache_key = f"{item.ecosystem}:{item.name}:{item.version}"
            raw_vulns: List[Dict[str, Any]] = []

            if cache_key in self.cache:
                raw_vulns = self.cache[cache_key]
            elif not self.offline:
                try:
                    payload = {
                        "package": {
                            "name": item.name,
                            "ecosystem": item.ecosystem,
                        },
                        "version": item.version,
                    }
                    resp = requests.post(OSV_API_URL, json=payload, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_vulns = data.get("vulns", [])
                        self.cache[cache_key] = raw_vulns
                        self._save_cache()
                except Exception:
                    # Network timeout or failure: proceed gracefully
                    pass

            for v in raw_vulns:
                vuln_id = v.get("id", "UNKNOWN-VULN")
                summary = v.get("summary") or (v.get("details", "")[:120] if v.get("details") else "Security vulnerability detected")

                # Extract fixed version if available
                fixed = None
                for aff in v.get("affected", []):
                    for r in aff.get("ranges", []):
                        for event in r.get("events", []):
                            if "fixed" in event:
                                fixed = event["fixed"]

                # Extract severity
                sev = "high"
                if "database_specific" in v and "severity" in v["database_specific"]:
                    sev = str(v["database_specific"]["severity"]).lower()

                vulnerabilities.append(
                    Vulnerability(
                        id=vuln_id,
                        package=item.name,
                        ecosystem=item.ecosystem,
                        affected_version=item.version,
                        summary=summary,
                        severity=sev,
                        fixed_version=fixed,
                    )
                )

        return vulnerabilities
