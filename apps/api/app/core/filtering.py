import re

BLACKLIST_DIRS = {
    "node_modules", "dist", "build", ".next", "out", "coverage", ".git", ".idea", ".vscode", "venv", ".venv", "__pycache__"
}

BLACKLIST_FILES = {
    ".env", ".gitignore", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Pipfile.lock", "poetry.lock"
}

BLACKLIST_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", # Images
    ".mp3", ".mp4", ".wav", ".avi", ".mov", # Media
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", # Documents
    ".zip", ".tar", ".gz", ".rar", # Archives
    ".exe", ".dll", ".so", ".dylib", ".class", ".jar", ".pyc", # Binaries
    ".pem", ".key", ".cert", ".crt", # Secrets/certs
    ".sqlite", ".db", ".sqlite3" # local DBs
}

def is_file_allowed(file_path: str) -> bool:
    """
    Validates whether a specific file should be ingested from the repository.
    
    Args:
        file_path (str): The relative path of the file in the repository (e.g., "src/main.py")
        
    Returns:
        bool: True if the file should be indexed, False otherwise.
    """
    parts = file_path.split("/")
    
    # Check if file is inside a blacklisted directory
    for part in parts[:-1]:
        if part in BLACKLIST_DIRS:
            return False
            
    filename = parts[-1]
    
    # Check for specific blacklisted filenames
    if filename in BLACKLIST_FILES:
        return False
        
    # Check for wildcards like .env.* or secret prefixes
    if filename.startswith(".env"):
        return False
        
    # Extract extension and check
    dot_index = filename.rfind(".")
    if dot_index != -1 and dot_index != 0:
        ext = filename[dot_index:].lower()
        if ext in BLACKLIST_EXTENSIONS:
            return False
            
    return True
