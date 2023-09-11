#!/bin/sh

# File: grafana-export.sh

### ---set-me-up---
HOST="https://<instance>.grafana.net"
KEY="sfgsdfsdwerrwerwr324535346trg"
###

# Set directory to .n8n folder in user's home directory
SCRIPT_DIR="$HOME/.n8n/grafana_export"

# Create directories if they don't exist
if [ ! -d "$SCRIPT_DIR/dashboards" ] ; then
    mkdir -p "$SCRIPT_DIR/dashboards"
fi
if [ ! -d "$SCRIPT_DIR/folders" ] ; then
    mkdir -p "$SCRIPT_DIR/folders"
fi

# Fetch and save dashboards
for dash in $(curl -s -k -H "Authorization: Bearer $KEY" "$HOST/api/search?query=" | jq -r '.[] | select(.type == "dash-db") | .uid'); do
  curl -s -k -H "Authorization: Bearer $KEY" "$HOST/api/dashboards/uid/$dash" \
    | jq '. |= (.folderUid=.meta.folderUid) | del(.meta) | del(.dashboard.id) + {overwrite: true}' \
    > "$SCRIPT_DIR/dashboards/${dash}.json"
  echo "Dashboard: ${dash} saved."
done

# Fetch and save folders
for folder in $(curl -s -k -H "Authorization: Bearer $KEY" "$HOST/api/folders" | jq -r '.[] | .uid'); do
  curl -s -k -H "Authorization: Bearer $KEY" "$HOST/api/folders/$folder" \
    | jq '. | del(.id) + {overwrite: true}' \
    > "$SCRIPT_DIR/folders/${folder}.json"
  echo "Folder: ${folder} saved."
done
