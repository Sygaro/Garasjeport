from utils.logging.unified_logger import get_logger
import subprocess

def get_git_version():
    try:
        result = subprocess.check_output(["git", "describe", "--tags", "--always"], stderr=subprocess.DEVNULL)
        return result.decode("utf-8").strip()
    except Exception:
        return "ukjent"
