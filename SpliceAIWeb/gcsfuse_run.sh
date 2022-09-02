#!/usr/bin/env bash

set -eo pipefail

# Create mount directory for service
mkdir -p $MNT_DIR

echo "Mounting GCS Fuse."
gcsfuse --debug_gcs --debug_fuse --debug_fs --debug_http $BUCKET $MNT_DIR 
echo "Mounting completed."

gunicorn -b 0.0.0.0:8080 -t 1200 -w 4 spliceai_web.app:app

# Exit immediately when one of the background processes terminate.
wait -n