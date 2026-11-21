from pathlib import Path
from datetime import datetime, timezone
PROJECT_ROOT = Path(__file__).resolve().parent.parent
def initialize_project():
    """Initialize the AI intelligence pipeline."""
    print("=" * 50)
    print("AI INTELLIGENCE DATA PIPELINE")
    print("=" * 50)
    print(f"Project directory: {PROJECT_ROOT}")
    print(f"Startup time: {datetime.now(timezone.utc).isoformat()}")
    required_directories = [
        "data",
        "logs",
        "tests",
    ]
    for directory in required_directories:
        path = PROJECT_ROOT / directory
        path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Directory ready: {directory}")
    print("\nProject initialization completed successfully!")
if __name__ == "__main__":
    initialize_project()