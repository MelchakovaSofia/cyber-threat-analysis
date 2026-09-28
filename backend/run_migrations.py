#!/usr/bin/env python3
"""Script to run Alembic migrations."""
import os
import sys
import subprocess

# Change to the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add the backend directory to Python path
sys.path.insert(0, backend_dir)

def run_migrations():
    """Run Alembic upgrade to head."""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Migration output:")
        print(result.stdout)
        if result.stderr:
            print("Migration errors:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)