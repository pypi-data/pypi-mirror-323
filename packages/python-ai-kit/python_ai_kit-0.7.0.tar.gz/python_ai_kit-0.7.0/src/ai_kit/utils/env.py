from dotenv import load_dotenv
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_environment(root_dir: str):
    """Load environment variables from .env files."""
    # Try loading from user's home directory first
    home_env = Path.home() / '.env'
    if home_env.exists():
        load_dotenv(home_env)
    
    # Then load from current directory, allowing it to override home settings
    local_env = Path('.env')
    if local_env.exists():
        load_dotenv(local_env, override=True)
    
    # Finally load from root directory if it exists
    ai_env = Path(root_dir) / '.env'
    if ai_env.exists():
        load_dotenv(ai_env, override=True)

    logger.debug("Environment variables loaded successfully")

    return True