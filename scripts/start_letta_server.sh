#!/bin/bash
#
# Start Letta server with Docker (LLM-agnostic configuration)
#
# This script starts a self-hosted Letta server that supports:
# - OpenAI (GPT models)
# - Anthropic (Claude models)
# - Ollama (local open-source models)
#
# Data is persisted in ~/.letta/.persist/pgdata
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Letta Server (Self-Hosted)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create a .env file with your configuration"
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ OPENAI_API_KEY not set${NC}"
    echo "OpenAI provider will not be available"
fi

# Create persistence directory
PERSIST_DIR="$HOME/.letta/.persist/pgdata"
mkdir -p "$PERSIST_DIR"
echo -e "${GREEN}✓ Persistence directory: $PERSIST_DIR${NC}"

# Check if container is already running
if docker ps | grep -q letta-server; then
    echo -e "${YELLOW}⚠ Letta server is already running${NC}"
    echo "Stopping existing container..."
    docker stop letta-server
    docker rm letta-server
fi

echo ""
echo -e "${GREEN}Starting Letta server...${NC}"
echo ""

# Start Letta server with all provider support
docker run -d \
  --name letta-server \
  -v "$PERSIST_DIR:/var/lib/postgresql/data" \
  -p 8283:8283 \
  --env-file .env \
  -e SECURE=true \
  letta/letta:latest

# Wait for server to be ready
echo ""
echo "Waiting for server to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8283/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Letta server is ready!${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Server failed to start${NC}"
    echo "Check logs with: docker logs letta-server"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Letta Server Started Successfully${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Server URL: http://localhost:8283"
echo "API Docs: http://localhost:8283/docs"
echo ""
echo "Configured providers:"
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "  ✓ OpenAI (model: $OPENAI_LLM_MODEL)"
fi
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "  ✓ Anthropic (model: $ANTHROPIC_LLM_MODEL)"
fi
echo "  ✓ Ollama (url: $OLLAMA_BASE_URL, model: $OLLAMA_LLM_MODEL)"
echo ""
echo "Default provider: $LLM_PROVIDER"
echo ""
echo "Useful commands:"
echo "  View logs:    docker logs -f letta-server"
echo "  Stop server:  docker stop letta-server"
echo "  Restart:      docker restart letta-server"
echo "  Remove:       docker stop letta-server && docker rm letta-server"
echo ""
