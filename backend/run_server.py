"""
PyInstaller entry point for KKRPA backend server.
This file is used as the main script when packaging with PyInstaller.
"""
import sys
import os
import multiprocessing

# Fix for PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    base_dir = os.path.dirname(sys.executable)
    # Add the app directory to path
    sys.path.insert(0, base_dir)
    os.chdir(base_dir)

    # Ensure data directory exists
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)


def main():
    """Start the uvicorn server."""
    import uvicorn
    from app.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        # No reload in production
        reload=False,
    )


if __name__ == "__main__":
    # Required for Windows multiprocessing in frozen mode
    multiprocessing.freeze_support()
    main()
