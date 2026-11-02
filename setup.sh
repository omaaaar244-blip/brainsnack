#!/bin/sh
# Fetch Twemoji SVGs (CC-BY 4.0) into assets/twemoji if missing.
cd "$(dirname "$0")"
[ -d assets/twemoji ] && exit 0
tmp=$(mktemp -d); (cd "$tmp" && npm i -s @twemoji/svg@15 >/dev/null 2>&1)
mkdir -p assets/twemoji && cp "$tmp"/node_modules/@twemoji/svg/*.svg assets/twemoji/ && rm -rf "$tmp"
