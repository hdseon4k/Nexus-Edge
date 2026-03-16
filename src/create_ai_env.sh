#!/bin/bash

# =================================================================
# 1. 프로젝트 이름 및 경로 설정
# =================================================================
# 인자가 없으면 'AI_DEV_PROJECT' 사용
PROJECT_NAME=${1:-"AI_DEV_PROJECT"}
SESSION=$PROJECT_NAME

# 프로젝트 폴더 생성 및 이동
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME" || { echo "Failed to enter directory: $PROJECT_NAME"; exit 1; }

# 폴더 안에서의 파일 경로 설정
MEMORY_FILE="memory.json"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "--------------------------------------------------------"
echo ">>> Project Directory: $(pwd)"
echo ">>> Initializing Project: $SESSION"
echo "--------------------------------------------------------"

# =================================================================
# 2. 클린업 및 백업
# =================================================================
# 기존 세션 종료
tmux kill-session -t "$SESSION" 2>/dev/null
mkdir -p "$BACKUP_DIR"

# 메모리 백업
if [ -f "$MEMORY_FILE" ]; then
    cp "$MEMORY_FILE" "$BACKUP_DIR/memory_$TIMESTAMP.json"
    echo "✔ Previous memory backed up within project folder."
fi

# PM2 서버 초기화 (MCP Memory Server)
PM2_NAME="mcp-memory-$SESSION"
pm2 delete "$PM2_NAME" 2>/dev/null
# MCP 서버 실행 - 고유 프로젝트 경로 사용
# absolute path를 사용하여 안정성 확보
pm2 start mcp-server-memory --name "$PM2_NAME" -- --path "$(pwd)/$MEMORY_FILE"

# =================================================================
# 3. Tmux 세션 생성 및 2x2 분할
# =================================================================
# 새 세션 생성 (데몬 모드)
tmux new-session -d -s "$SESSION" -n "DevWorkspace"

# 2x2 그리드 생성 (안정성을 위해 -d 옵션 사용)
# .0 (Top) & .1 (Bottom)
tmux split-window -v -d -t "$SESSION:0"
# .0 (Top-Left) & .1 (Top-Right)
tmux split-window -h -d -t "$SESSION:0.0"
# .2 (Bottom-Left) & .3 (Bottom-Right)
tmux split-window -h -d -t "$SESSION:0.2"

# 레이아웃 균형 조정 및 패널 준비 대기
tmux select-layout -t "$SESSION:0" tiled
sleep 1

# 외관 설정 (Role 표시 최적화)
tmux set-option -t "$SESSION" pane-border-status top
# #{pane_index}에 따라 역할을 동적으로 표시 (가장 확실한 방법)
# 0: PLANNER, 1: RESEARCHER, 2: DEVELOPER, 3: OPERATOR
tmux set-option -t "$SESSION" pane-border-format \
" [ #{?pane_active,#[fg=cyan]#[bold],#[fg=white]}#{?#{==:#{pane_index},0},PLANNER,#{?#{==:#{pane_index},1},RESEARCHER,#{?#{==:#{pane_index},2},DEVELOPER,OPERATOR}}}#[default] ] "

# =================================================================
# 4. 에이전트 실행 (역할별 최적화)
# =================================================================

# 헬퍼 함수: Gemini 실행 (중복 실행 방지를 위해 clear 추가 및 대기 처리)
run_agent() {
    local pane_idx=$1
    local model=$2
    local role=$3
    local prompt="You are a $role for project [$PROJECT_NAME]. Please help me with the development process."
    
    echo ">>> Starting $role in pane $pane_idx..."
    # 터미널 초기화 후 명령어를 실행하여 버퍼 문제를 방지
    tmux send-keys -t "$SESSION:0.$pane_idx" "clear && source ~/.bashrc && gemini --model $model -i \"$prompt\"" C-m
    sleep 0.2
}

# 각 패널에 에이전트 할당
# PLANNER (Top-Left)
run_agent 0 "pro" "strategic planner"

# RESEARCHER (Top-Right)
run_agent 1 "flash" "researcher"

# DEVELOPER (Bottom-Left)
run_agent 2 "pro" "developer"

# OPERATOR (Bottom-Right)
tmux send-keys -t "$SESSION:0.3" "clear && echo \">>> Workdir: $(pwd)\" && echo \">>> Project: $PROJECT_NAME\" && ls -F" C-m

# 최종 포커스: PLANNER
tmux select-pane -t "$SESSION:0.0"

# 세션 연결
echo ">>> Attaching to session: $SESSION"
tmux attach-session -t "$SESSION"
