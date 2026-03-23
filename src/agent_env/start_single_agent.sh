#!/bin/bash

# =================================================================
# 1. 프로젝트 이름 및 경로 설정
# =================================================================
# 인자가 없으면 'AI_SINGLE_PROJECT' 사용
PROJECT_NAME=${1:-"AI_SINGLE_PROJECT"}

# 프로젝트 폴더 생성 및 이동
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME" || { echo "Failed to enter directory: $PROJECT_NAME"; exit 1; }

# Set the terminal title for easy identification
printf "\033]0;%s\007" "Gemini CLI: $PROJECT_NAME"

# --- Welcome Message ---
echo "================================================="
echo "  🚀 Starting AI Agent Environment: $PROJECT_NAME"
echo "================================================="
echo "Project Directory: $(pwd)"
echo "-------------------------------------------------"
echo ""

# Launch the Gemini CLI in the project directory
gemini

echo ""
echo "================================================="
echo "  ✅ Agent session closed by user."
echo "================================================="
