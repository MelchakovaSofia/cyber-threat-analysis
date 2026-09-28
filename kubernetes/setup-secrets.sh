#!/bin/bash
# Script to set up Kubernetes secrets for CTA deployment
# Usage: ./setup-secrets.sh

set -e

echo "Setting up Kubernetes secrets for Cyber Threat Analysis System"

# Check if required environment variables are set
if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable is required"
    echo "Usage: DB_PASSWORD=your_password ./setup-secrets.sh"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "Error: SECRET_KEY environment variable is required"
    echo "Generate one with: openssl rand -base64 32"
    echo "Usage: SECRET_KEY=your_secret ./setup-secrets.sh"
    exit 1
fi

# Set defaults for optional variables
DB_USER="${DB_USER:-cta}"
DB_HOST="${DB_HOST:-cta-postgres}"
DB_NAME="${DB_NAME:-cta_db}"

# Create the secret
kubectl create secret generic cta-secret \
  --from-literal=DATABASE_URL="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}" \
  --from-literal=SECRET_KEY="${SECRET_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secret 'cta-secret' created successfully!"
echo "Database URL: postgresql+psycopg2://${DB_USER}:***@${DB_HOST}:5432/${DB_NAME}"
echo "Secret Key: ***"