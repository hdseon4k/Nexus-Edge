#!/data/data/com.termux/files/usr/bin/bash
# Shell Script: Stop S24 Ultra Edge Server
# Located at ~/Nexus-Edge/scripts/stop_server.sh

DIR="/data/data/com.termux/files/home/Nexus-Edge"

PID=$(pgrep -f "python3.*src/app.py")
if [ -z "$PID" ]; then
    echo "🟡 S24 Ultra Server is NOT running."
else
    echo "🛑 Stopping S24 Ultra Server (PID: $PID)..."
    pkill -f "python3.*src/app.py"
    sleep 1
    CHECK=$(pgrep -f "python3.*src/app.py")
    if [ -z "$CHECK" ]; then
        echo "✅ Server STOPPED successfully."
    else
        echo "⚠️ Force killing server..."
        pkill -9 -f "python3.*src/app.py"
        echo "✅ Force killed."
    fi
fi
