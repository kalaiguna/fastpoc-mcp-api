"""
Entry point for running the FastAPI REST API server.
Configuration via environment variables:
    - PORT: Server port (default: 8081)
    - HOST: Server host (default: 0.0.0.0)
"""
import os
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get configuration from environment variables
    port = int(os.getenv("PORT", 8081))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "true").lower() in ("true", "1", "yes")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app.api:app", host=host, port=port, reload=reload)
