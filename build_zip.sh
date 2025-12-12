#!/usr/bin/env bash
# Build a source zip containing the package
rm -rf dist
mkdir -p dist
zip -r dist/triad-0.1.0.zip blockchain triad README.md pyproject.toml tests
