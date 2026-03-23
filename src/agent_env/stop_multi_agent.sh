#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 종료할 프로젝트 설정
PROJECT_NAME=${1:-"AI_DEV_PROJECT"}
SESSION=$PROJECT_NAME
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo -e "${YELLOW}--------------------------------------------------------${NC}"
echo -e ">>> [${TIMESTAMP}] Stopping Project: ${GREEN}$PROJECT_NAME${NC}"
echo -e ">>> Localized Resource Cleanup..."
echo -e "${YELLOW}--------------------------------------------------------${NC}"

# 2. 필수 명령어 존재 확인 (tmux)
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}✘ Error: 'tmux' 명령어를 찾을 수 없습니다. 설치 여부를 확인하세요.${NC}"
fi

# 3. Tmux 세션 저장 및 종료
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo -e ">>> Saving Tmux session [$SESSION] state..."
    
    # tmux-resurrect 저장 스크립트 실행 시도
    RESURRECT_SAVE_SCRIPT="/home/hdseon/.tmux/plugins/tmux-resurrect/scripts/save.sh"
    if [ -f "$RESURRECT_SAVE_SCRIPT" ]; then
        tmux run-shell "$RESURRECT_SAVE_SCRIPT" > /dev/null 2>&1
        echo -e "${GREEN}✔${NC} Tmux session state saved."
    fi

    # 세션 종료 (Gemini CLI 및 stdio 기반 MCP 서버도 함께 종료됨)
    if tmux kill-session -t "$SESSION" 2>/dev/null; then
        echo -e "${GREEN}✔${NC} Tmux session [$SESSION] has been terminated."
    else
        echo -e "${RED}✘${NC} Failed to terminate Tmux session [$SESSION]."
    fi
else
    echo -e "ℹ No active Tmux session found for [$SESSION]."
fi

# 4. 상태 보고
echo -e "${YELLOW}--------------------------------------------------------${NC}"
if [ -d "$PROJECT_NAME" ]; then
    echo -e "${GREEN}✅ Cleanup complete for [$PROJECT_NAME].${NC}"
    echo "   - Project folder and history are preserved."
    [ -d "$PROJECT_NAME/backups" ] && echo "   - Database backups available in: $PROJECT_NAME/backups/"
else
    echo -e "${YELLOW}⚠ Warning: Project folder [$PROJECT_NAME/] not found.${NC}"
fi
echo -e "${YELLOW}--------------------------------------------------------${NC}"
