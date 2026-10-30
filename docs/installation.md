# Installation & Setup Guide

This guide covers installing and configuring the `developer-code-toolkit`.

## Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- `pip` package manager.

## Local Monorepo Development Installation

Clone the repository and install packages in editable mode:

```bash
git clone https://github.com/developer-code-toolkit/developer-code-toolkit.git
cd developer-code-toolkit

# 1. Install common foundation
pip install -e shared/toolkit_common

# 2. Install desired CLI tools
pip install -e packages/codebase-map
pip install -e packages/env-checker
pip install -e packages/api-diff
pip install -e packages/dead-code-finder
pip install -e packages/code-complexity-cli
pip install -e packages/dependency-audit
```

## Verify Installation

```bash
cbm --version
envcheck --version
api-diff --help
dcf --version
ccx --version
da --version
```
