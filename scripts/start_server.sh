#!/data/data/com.termux/files/usr/bin/bash
# Shell Script: Start S24 Ultra Edge Server
# Located at ~/Nexus-Edge/scripts/start_server.sh

DIR="/data/data/com.termux/files/home/Nexus-Edge"
cd "$DIR" || exit 1

# Check if already running
PID=$(pgrep -f "python3.*src/app.py")
if [ -n "$PID" ]; then
    echo "🟢 S24 Ultra Server is already RUNNING (PID: $PID)"
else
    echo "🚀 Starting S24 Ultra Server in background..."
    nohup python3 "$DIR/src/app.py" > "$DIR/server.log" 2>&1 &
    sleep 1
    NEW_PID=$(pgrep -f "python3.*src/app.py")
    if [ -n "$NEW_PID" ]; then
        echo "🎉 Server STARTED successfully! (PID: $NEW_PID)"
    else
        echo "❌ Failed to start server. Check logs."
    fi
fi
