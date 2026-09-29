#!/usr/bin/env bash
# Claude Studio Hub Manager Script

ACTION="${1:-status}"

case "$ACTION" in
  start)
    echo "Starting Claude Studio Hub & Nginx..."
    systemctl start claude-web-gui
    systemctl start nginx
    systemctl status claude-web-gui --no-pager
    ;;
  stop)
    echo "Stopping Claude Studio Hub..."
    systemctl stop claude-web-gui
    ;;
  restart)
    echo "Restarting Claude Studio Hub..."
    systemctl restart claude-web-gui
    systemctl restart nginx
    echo "Done!"
    ;;
  status)
    echo "=== Claude Web GUI Status ==="
    systemctl status claude-web-gui --no-pager
    echo ""
    echo "=== Nginx Status ==="
    systemctl status nginx --no-pager
    ;;
  logs)
    echo "Tailing logs (Press Ctrl+C to exit)..."
    journalctl -u claude-web-gui -f
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac
