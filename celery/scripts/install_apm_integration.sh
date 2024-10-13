#!/bin/bash

# Wait for Kibana to start
until $(curl --output /dev/null --silent --head --fail http://kibana:5601); do
    printf '.'
    sleep 5
done

# Install the APM integration
curl -X POST "http://kibana:5601/api/integrations/v1/packaged_apps/apm" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: application/json" \
    -u elastic:elastic