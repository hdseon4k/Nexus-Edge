#!/bin/bash

# 프로젝트 이름 설정
PROJECT_NAME=${1:-"AI_SINGLE_PROJECT"}

echo "================================================="
echo "  🛑 Stopping Environment: $PROJECT_NAME"
echo "================================================="

# 프로젝트 디렉토리로 이동
if [ -d "$PROJECT_NAME" ]; then
    cd "$PROJECT_NAME" || exit 1
else
    echo "❌ ERROR: Directory '$PROJECT_NAME' not found."
    exit 1
fi

echo "Workdir: $(pwd)"
echo ""

# --- 1. Backup the memory database ---
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
mkdir -p "backups"
BACKUP_FILE="backups/memory_${TIMESTAMP}.db"

if [ -f "memory.db" ]; then
    echo "Backing up 'memory.db' to '${BACKUP_FILE}'..."
    cp memory.db "${BACKUP_FILE}"
    if [ $? -eq 0 ]; then
        echo "✅ Backup successful."
    else
        echo "❌ ERROR: Backup failed."
    fi
else
    echo "ℹ️  'memory.db' not found, skipping backup."
fi

echo "-------------------------------------------------"

# --- 2. Shut down background agent services ---
# This will find and kill the 'npx' process running the sqlite server
# that is started by the Gemini CLI for this project.
echo "Shutting down background MCP server for this directory..."
# The '-f' flag matches against the full command string.
pkill -f "@modelcontextprotocol/server-sqlite.*${PWD}"

# Check the exit code of pkill. 0 means success, 1 means no process found.
if [ $? -le 1 ]; then
    echo "✅ Cleanup command finished."
else
    echo "❌ ERROR: Failed to execute cleanup command."
fi

echo ""
echo "================================================="
echo "  Environment cleanup complete: $PROJECT_NAME"
echo "================================================="
