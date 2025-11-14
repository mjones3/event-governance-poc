#!/bin/bash
# Script to pre-pull Docker base images
# Run this when you have good network access (VPN off or good connectivity)

echo "Pulling base images for BioPro services..."

# Pull Maven build image
echo "1/2 Pulling maven:3.9-eclipse-temurin-17..."
docker pull maven:3.9-eclipse-temurin-17

# Pull runtime image
echo "2/2 Pulling eclipse-temurin:17-jre-alpine..."
docker pull eclipse-temurin:17-jre-alpine

echo ""
echo "✅ Base images cached successfully!"
echo "You can now run: docker compose up -d --build"
