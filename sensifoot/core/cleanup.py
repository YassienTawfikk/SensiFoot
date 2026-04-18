import os
import shutil

def perform_cleanup(project_root: str):
    """
    Recursively scans the project_root directory and forcibly deletes any
    `__pycache__` or `.idea` folders to ensure a clean state upon automation exit.
    """
    targets_to_remove = {'__pycache__', '.idea'}

    print(f"\n[Cleanup Automation] Initiating teardown in {project_root}...")

    for root, dirs, files in os.walk(project_root, topdown=False):
        for directory in dirs:
            if directory in targets_to_remove:
                target_path = os.path.join(root, directory)
                try:
                    shutil.rmtree(target_path, ignore_errors=True)
                    print(f"  -> Destroyed: {target_path}")
                except Exception as e:
                    print(f"  -> Failed to destroy {target_path}: {e}")

    print("[Cleanup Automation] Teardown complete.\n")
