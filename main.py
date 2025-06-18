import sys
import os
from pathlib import Path

# Set BASE_DIR sebagai direktori utama proyek
BASE_DIR = Path(__file__).parent.absolute()

# Tambahkan BASE_DIR ke sys.path agar bisa import module App
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from App.application import PromanisApp


def main():
    """Entry point untuk aplikasi Promanis"""
    app = PromanisApp(BASE_DIR)
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()