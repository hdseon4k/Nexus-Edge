#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 종료할 프로젝트 설정
PROJECT_NAME=${1:-"AI_DEV_PROJECT"}
SESSION=$PROJECT_NAME
PM2_NAME="mcp-memory-$SESSION"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo -e "${YELLOW}--------------------------------------------------------${NC}"
echo -e ">>> [${TIMESTAMP}] Stopping Project: ${GREEN}$PROJECT_NAME${NC}"
echo -e ">>> Localized Resource Cleanup..."
echo -e "${YELLOW}--------------------------------------------------------${NC}"

# 2. 필수 명령어 존재 확인 (tmux, pm2)
for cmd in tmux pm2; do
    if ! command -v "$cmd" &> /dev/null; then
        echo -e "${RED}✘ Error: '$cmd' 명령어를 찾을 수 없습니다. 설치 여부를 확인하세요.${NC}"
    fi
done

# 3. Tmux 세션 종료
if tmux has-session -t "$SESSION" 2>/dev/null; then
    if tmux kill-session -t "$SESSION" 2>/dev/null; then
        echo -e "${GREEN}✔${NC} Tmux session [$SESSION] has been terminated."
    else
        echo -e "${RED}✘${NC} Failed to terminate Tmux session [$SESSION]."
    fi
else
    echo -e "ℹ No active Tmux session found for [$SESSION]."
fi

# 4. PM2 MCP 서버 프로세스 종료 및 삭제
if pm2 describe "$PM2_NAME" > /dev/null 2>&1; then
    if pm2 delete "$PM2_NAME" > /dev/null 2>&1; then
        echo -e "${GREEN}✔${NC} PM2 process [$PM2_NAME] has been deleted."
    else
        echo -e "${RED}✘${NC} Failed to delete PM2 process [$PM2_NAME]."
    fi
else
    echo -e "ℹ No PM2 process found for [$PM2_NAME]."
fi

# 5. 상태 보고 및 폴더 확인
echo -e "${YELLOW}--------------------------------------------------------${NC}"
if [ -d "$PROJECT_NAME" ]; then
    echo -e "${GREEN}✅ Cleanup complete for [$PROJECT_NAME].${NC}"
    echo "   - Project folder [$PROJECT_NAME/] and its history are preserved."
    if [ -d "$PROJECT_NAME/backups" ]; then
        echo "   - Memory backups available in: $PROJECT_NAME/backups/"
    fi
else
    echo -e "${YELLOW}⚠ Warning: Project folder [$PROJECT_NAME/] does not exist in current path.${NC}"
fi
echo -e "${YELLOW}--------------------------------------------------------${NC}"
