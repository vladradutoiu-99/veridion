#!/bin/bash

TOKEN_PATH="/usr/share/kibana/config/kibana_service_token"
ENROLLMENT_TOKEN_PATH="/usr/share/kibana/config/enrollment_token"

echo "Waiting for Kibana service token..."

# Wait for the token file to exist
while [ ! -f "$TOKEN_PATH" ]; do
    sleep 2  # Wait for 2 seconds before checking again
done

echo "Kibana service token is available $(cat $TOKEN_PATH)."

echo "Waiting for Kibana enrollment token..."

while [ ! -f "$ENROLLMENT_TOKEN_PATH" ]; do
    sleep 2  # Wait for 2 seconds before checking again
done

echo "Kibana enrollment token is available $(cat $ENROLLMENT_TOKEN_PATH). Starting Kibana..."

# Start Kibana
exec /usr/local/bin/kibana-docker