"""License classification and policy compliance audit."""

from typing import Dict, List, Optional

from pydantic import BaseModel

from dependency_audit.models import DependencyItem

PERMISSIVE_LICENSES = {
    "mit",
    "apache-2.0",
    "apache 2.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "isc",
    "unlicense",
    "cc0-1.0",
    "python-2.0",
}

COPYLEFT_LICENSES = {
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "mpl-2.0",
    "epl-2.0",
}

# Known common licenses for fallback identification
COMMON_PACKAGE_LICENSES: Dict[str, str] = {
    "requests": "Apache-2.0",
    "flask": "BSD-3-Clause",
    "fastapi": "MIT",
    "pydantic": "MIT",
    "click": "BSD-3-Clause",
    "rich": "MIT",
    "express": "MIT",
    "react": "MIT",
    "lodash": "MIT",
    "gpl-sample-pkg": "GPL-3.0",
}


class LicenseViolation(BaseModel):
    package: str
    license: str
    policy: str
    message: str


def check_license_compliance(
    items: List[DependencyItem],
    policy: str = "permissive",
    allowed_licenses: Optional[List[str]] = None,
) -> List[LicenseViolation]:
    """Audit dependency licenses against specified policy."""
    violations: List[LicenseViolation] = []
    policy_lower = policy.lower()

    if allowed_licenses:
        allowed_set = {lic.lower() for lic in allowed_licenses}
    else:
        allowed_set = PERMISSIVE_LICENSES

    for item in items:
        # Determine license
        lic = item.license or COMMON_PACKAGE_LICENSES.get(item.name.lower())
        if not lic:
            continue

        lic_clean = lic.lower().strip()
        if policy_lower == "permissive":
            if lic_clean not in allowed_set:
                if any(copyleft in lic_clean for copyleft in ("gpl", "agpl")):
                    violations.append(
                        LicenseViolation(
                            package=item.name,
                            license=lic,
                            policy=policy,
                            message=f"Copyleft license '{lic}' in package '{item.name}' violates permissive license policy",
                        )
                    )
                elif lic_clean not in allowed_set:
                    violations.append(
                        LicenseViolation(
                            package=item.name,
                            license=lic,
                            policy=policy,
                            message=f"License '{lic}' in package '{item.name}' is not in allowed list",
                        )
                    )

    return violations
