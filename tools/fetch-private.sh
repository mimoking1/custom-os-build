#!/usr/bin/env bash
# Fetch the private payload (draft release "tahmeel-private", visible only to repo writers) into build/private.
set -euo pipefail
mkdir -p build/private
API="https://api.github.com/repos/${GITHUB_REPOSITORY}"
curl -fsS -H "Authorization: Bearer ${GH_TOKEN}" "$API/releases?per_page=100" > /tmp/rels.json
python3 - <<'PY' > /tmp/private-assets.txt
import json
for r in json.load(open('/tmp/rels.json')):
    if r.get('tag_name') == 'tahmeel-private':
        for a in r['assets']: print(a['id'], a['name'])
PY
[ -s /tmp/private-assets.txt ] || { echo "private payload release not found"; exit 1; }
while read -r id name; do
  curl -fsSL -H "Authorization: Bearer ${GH_TOKEN}" -H "Accept: application/octet-stream" "$API/releases/assets/$id" -o "build/private/$name"
done < /tmp/private-assets.txt
ls -la build/private
