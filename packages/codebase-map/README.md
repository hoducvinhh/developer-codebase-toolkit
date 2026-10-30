# codebase-map (`cbm`)

A developer CLI tool to visualize codebase structure, architecture modules, entry points, and dependencies.

## Installation
```bash
pip install -e packages/codebase-map
```

## Usage
```bash
# Full codebase analysis
cbm analyze .

# Directory tree view with depth control
cbm tree . --depth 2

# Dependency mapping
cbm deps .

# Architecture diagram generation (Mermaid)
cbm diagram .
```
