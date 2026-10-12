"""PyInstaller 진입점: FinClose 데스크톱 앱."""
import multiprocessing
import sys

from finclose.desktop import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
