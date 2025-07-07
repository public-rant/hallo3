import os
import socket
import subprocess
import sys
import json
import datetime

HOST = "0.0.0.0"
PORT = 5555

def fetch_usage(date):
    """Fetch total_usage in cents for a specific date (YYYY-MM-DD) using curl and pass."""
    try:
        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()
        url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={date}&end_date={date}"
        curl = subprocess.Popen(
            [
                "curl", "-s", url,
                "-H", f"Authorization: Bearer {OPENAI_API_KEY}"
            ],
            stdout=subprocess.PIPE
        )
        output, _ = curl.communicate()
        result = json.loads(output)
        return int(result.get("total_usage", 0))
    except Exception:
        return 0

def check_recent_costs():
    """Return True if there are costs for today or yesterday UTC, robust to API errors."""
    utc_today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    utc_yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        cost_today = fetch_usage(utc_today)
    except Exception:
        cost_today = 0
    try:
        cost_yesterday = fetch_usage(utc_yesterday)
    except Exception:
        cost_yesterday = 0

    return (cost_today + cost_yesterday) > 0

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"MCP circuit-breaker server running on port {PORT}...")
        while True:
            conn, addr = s.accept()
            with conn:
                data = b''
                while not data.endswith(b'\n'):
                    more = conn.recv(1024)
                    if not more:
                        break
                    data += more
                command = data.decode("utf-8").strip().upper()
                if command == "STATUS":
                    result = "TRUE\n" if check_recent_costs() else "FALSE\n"
                else:
                    result = "ERR Unknown Command\n"
                conn.sendall(result.encode("utf-8"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down.")
        sys.exit(0)
