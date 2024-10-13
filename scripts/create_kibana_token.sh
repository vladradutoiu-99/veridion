#!/bin/bash
TOKEN_PATH="/usr/share/kibana/config/kibana_service_token"
ENROLLMENT_TOKEN_PATH="/usr/share/kibana/config/enrollment_token"

# Wait for Elasticsearch to be ready and generate a service account token for Kibana

# Start Elasticsearch
# /usr/local/bin/docker-entrypoint.sh &  # Run in the background
# ES_PID=$!

echo $ELASTIC_USERNAME $ELASTIC_PASSWORD

# Wait for Elasticsearch to be ready
until curl -u ${ELASTIC_USERNAME}:${ELASTIC_PASSWORD} -s ${ELASTIC_URL}:9200/_cluster/health?wait_for_status=yellow --connect-timeout 10 > /dev/null; do
  echo 'Waiting for Elasticsearch...'
  sleep 3
done

echo "Elasticsearch is up!"

if [ -f "$TOKEN_PATH" ]; then
    EXISTING_TOKEN=$(cat "$TOKEN_PATH")
    # echo "Revoking existing token: $EXISTING_TOKEN"
    echo "Existing token found: $EXISTING_TOKEN"
    # Revoke the existing token
    # curl -X DELETE -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD "http://localhost:9200/_security/service_tokens/$EXISTING_TOKEN"
else
    TOKEN=$(bin/elasticsearch-service-tokens create elastic/kibana default)
    TOKEN_VALUE=$(echo $TOKEN | awk '{print $NF}')

    # Save the generated token to a file that Kibana can read
    echo $TOKEN_VALUE > $TOKEN_PATH

    # Output the token for logging/debugging purposes (optional)
    echo "Kibana service account token generated: $TOKEN_VALUE"
fi

# Generating enrollment token

if [ -f "$ENROLLMENT_TOKEN_PATH" ]; then
    EXISTING_ENROLLMENT_TOKEN=$(cat "$ENROLLMENT_TOKEN_PATH")
    # echo "Revoking existing token: $EXISTING_TOKEN"
    echo "Existing enrollment token found: $EXISTING_ENROLLMENT_TOKEN"
    # Revoke the existing token
    # curl -X DELETE -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD "http://localhost:9200/_security/service_tokens/$EXISTING_TOKEN"
else

    RESPONSE = $(/usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana)

    echo "Response: $RESPONSE"

    # Extract the enrollment token using grep and sed
    ENROLLMENT_TOKEN=$(echo "$RESPONSE" | grep -o '"token": "[^"]*' | grep -o '[^"]*$')

    echo "Enrollment Token: $ENROLLMENT_TOKEN"

    # if [[ -z "$ENROLLMENT_TOKEN" ]]; then
    #     echo "Failed to retrieve the enrollment token. Check your Elasticsearch credentials or connection."
    #     exit 1
    # fi

    # # Print the enrollment token
    echo "Enrollment Token: $ENROLLMENT_TOKEN"
    echo $ENROLLMENT_TOKEN > $ENROLLMENT_TOKEN_PATH
fi

# Wait for the Elasticsearch process to finish
# echo "Waiting for Elasticsearch to finish..."
# wait $ES_PID