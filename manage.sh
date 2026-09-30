#!/usr/bin/env bash
# Claude Studio Hub Manager Script (Port 80 & Port 443 Support)

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ACTION="${1:-status}"
PID_FILE="${DIR}/logs/uvicorn.pid"
LOG_FILE="${DIR}/logs/app.log"

mkdir -p "${DIR}/logs"

start_uvicorn() {
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo " Claude Hub backend is already running (PID: $(pgrep -f 'uvicorn app.main:app')). "
    else
        echo "Starting Claude Hub backend on 127.0.0.1:8080..."
        nohup "${DIR}/.venv/bin/python3" -m uvicorn app.main:app --host 127.0.0.1 --port 8080 > "${LOG_FILE}" 2>&1 &
        echo $! > "${PID_FILE}"
        sleep 1
        echo "Claude Hub backend started."
    fi
}

stop_uvicorn() {
    echo "Stopping Claude Hub backend..."
    pkill -f "uvicorn app.main:app" || true
    rm -f "${PID_FILE}"
}

start_nginx() {
    echo "Checking Nginx reverse proxy..."
    if ! pgrep -x "nginx" > /dev/null; then
        service nginx start || nginx
    else
        service nginx reload || nginx -s reload || true
    fi
}

stop_nginx() {
    echo "Stopping Nginx..."
    service nginx stop || pkill -x nginx || true
}

case "$ACTION" in
  start)
    echo "=== Starting Claude Studio Hub (Port 80 & Port 443) ==="
    start_uvicorn
    start_nginx
    $0 status
    ;;
  stop)
    echo "=== Stopping Claude Studio Hub ==="
    stop_uvicorn
    stop_nginx
    echo "Done!"
    ;;
  restart)
    echo "=== Restarting Claude Studio Hub ==="
    stop_uvicorn
    sleep 1
    start_uvicorn
    service nginx reload || nginx -s reload || service nginx restart
    echo "Done!"
    $0 status
    ;;
  status)
    echo "=========================================================="
    echo "          Claude Studio Hub Status (Port 80 / 443)         "
    echo "=========================================================="
    echo -n "1. Backend (Uvicorn 127.0.0.1:8080): "
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo "RUNNING (PID: $(pgrep -f 'uvicorn app.main:app' | tr '\n' ' '))"
    else
        echo "STOPPED"
    fi

    echo -n "2. Reverse Proxy (Nginx Port 80 & 443): "
    if pgrep -x "nginx" > /dev/null; then
        echo "RUNNING (PID: $(pgrep -x 'nginx' | tr '\n' ' '))"
    else
        echo "STOPPED"
    fi

    echo ""
    echo "=== Active Listening Ports ==="
    ss -tulpn | grep -E ":80 |:443 |:8080 " || true
    echo "=========================================================="
    ;;
  logs)
    echo "Tailing backend logs (Press Ctrl+C to exit)..."
    tail -f "${LOG_FILE}"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac
