"""This module contains the API routes for managing datasets."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from .api.status import HTTP_STATUS_NOT_FOUND

app_router = APIRouter()

# Get the current project root directory
project_root = Path(__file__).resolve().parent.parent.parent

webapp_dir = project_root / "dist-purple-view-app"

# Check if the directory exists and raise an error if it doesn't
if not webapp_dir.exists():
    raise RuntimeError(
        f"Directory '{webapp_dir}' does not exist in '{project_root}'"
    )

# Ensure the path is absolute
webapp_dir = webapp_dir.resolve()


@app_router.get("/", include_in_schema=False)
async def serve_index_file():
    """Serve the index.html file for the webapp."""
    index_file = webapp_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Index file not found"
        )
    return FileResponse(index_file)


@app_router.get("/{path:path}", include_in_schema=False)
async def serve_static_files(path: str):
    """Serve static files from the webapp directory."""
    file_path = webapp_dir / path

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="File not found"
        )
    return FileResponse(file_path)
