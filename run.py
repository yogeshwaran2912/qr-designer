"""
QR Art Studio - Application Runner
Launches the Flask web server with port conflict resolution and terminal summary.
"""

import os
import sys
import socket
import webbrowser
from app import app


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def find_available_port(start_port: int = 5000, max_attempts: int = 20) -> int:
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    return start_port


if __name__ == "__main__":
    host = "127.0.0.1"
    port = find_available_port(5000)

    url = f"http://{host}:{port}"
    print("=" * 65)
    print("  🎨 QR ART STUDIO – Transform Images into Scannable QR Artwork")
    print("=" * 65)
    print(f"  • Local Server Running at: {url}")
    print(f"  • Input directory:        {os.path.abspath('input')}")
    print(f"  • Output directory:       {os.path.abspath('output')}")
    print(f"  • Reference sample:       {os.path.abspath('input/house1.png')}")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.\n")

    # If --open flag passed, open in browser
    if "--open" in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    app.run(host=host, port=port, debug=False)
