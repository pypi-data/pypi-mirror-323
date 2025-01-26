"""Non-editable system constants for AI Kit."""


# ! Main config
class CoreConfig:
    ROOT_DIR = ".ai-kit"
    INDEX_DIR = "files"  # Directory for indexed content
    INDEX_CACHE_DIR = "index"  # Directory for index cache files
    SUPPORTED_FILE_EXTENSIONS = [".txt", ".md"]

# ! LLM Config
class LiteLLMConfig:
    """Model configurations that can be customized by users."""

    # Default models
    DEFAULT_CHAT_MODEL = "gpt-4o"
    DEFAULT_REASONING_MODEL = "o1"
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

    # Supported models - add or remove based on your needs
    SUPPORTED_CHAT_MODELS = ["gpt-4o", "llama-3.1-8B-instruct"]
    SUPPORTED_REASONING_MODELS = ["o1-mini", "o1", "r1"]
    SUPPORTED_EMBEDDING_MODELS = ["text-embedding-3-small", "text-embedding-3-large"]

    # Model mappings (optional)
    MODEL_MAPPINGS = {
        "r1": "deepseek-reasoner",
        "llama-3.1-8B-instruct": "together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    }

    # Required API keys for different providers (optional)
    REQUIRED_API_KEYS = {
        "o1-mini": "OPENAI_API_KEY",
        "o1": "OPENAI_API_KEY",
        "gpt-4o": "OPENAI_API_KEY",
        "r1": "DEEPSEEK_API_KEY",
        "llama-3.1-8B-instruct": "TOGETHER_API_KEY",
    }

    # Model dimension mappings for embeddings
    MODEL_DIMENSIONS = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}

    @staticmethod
    def api_keys():
        return set(LiteLLMConfig.REQUIRED_API_KEYS.values())

    @staticmethod
    def to_string():
        return f"""
        DEFAULT_CHAT_MODEL: {LiteLLMConfig.DEFAULT_CHAT_MODEL}
        DEFAULT_REASONING_MODEL: {LiteLLMConfig.DEFAULT_REASONING_MODEL}
        DEFAULT_EMBEDDING_MODEL: {LiteLLMConfig.DEFAULT_EMBEDDING_MODEL}
        
        SUPPORTED_CHAT_MODELS: {LiteLLMConfig.SUPPORTED_CHAT_MODELS}
        SUPPORTED_REASONING_MODELS: {LiteLLMConfig.SUPPORTED_REASONING_MODELS}
        SUPPORTED_EMBEDDING_MODELS: {LiteLLMConfig.SUPPORTED_EMBEDDING_MODELS}
        
        MODEL_MAPPINGS: {LiteLLMConfig.MODEL_MAPPINGS}
        REQUIRED_API_KEYS: {LiteLLMConfig.REQUIRED_API_KEYS}
        MODEL_DIMENSIONS: {LiteLLMConfig.MODEL_DIMENSIONS}
        """
