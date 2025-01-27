import subprocess
import sys
from pathlib import Path

def build_ui():
    """Build the UI using pnpm."""
    ui_dir = Path(__file__).parent.parent / "ui"
    if not ui_dir.exists():
        print("UI directory not found")
        return
    
    print("Building UI...")
    try:
        # Install dependencies
        subprocess.run(["pnpm", "install"], cwd=ui_dir, check=True)
        # Build UI
        subprocess.run(["pnpm", "run", "build"], cwd=ui_dir, check=True)
        print("UI build complete")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build UI: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("pnpm not found. Please install pnpm to build the UI")
        sys.exit(1)

if __name__ == "__main__":
    build_ui() 