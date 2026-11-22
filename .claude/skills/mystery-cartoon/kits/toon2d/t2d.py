#!/usr/bin/env python3
"""toon2d-shorts launcher: python t2d.py <command> <project> [options]  (python t2d.py --help)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if os.path.isdir(os.path.join(HERE, '.deps')):          # optional: pip install --target .deps -r requirements.txt
    sys.path.insert(0, os.path.join(HERE, '.deps'))

from toon2d.cli import main

if __name__ == '__main__':
    sys.exit(main())
