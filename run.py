#!/usr/bin/env python3
"""
Launcher wrapper for Turnitout similarity reduction pipeline.
Delegates to the packaged CLI entrypoint.
"""
import sys
import os

# Insert src directory to path to support running without installation
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from turnitout.cli import main

if __name__ == '__main__':
    main()
