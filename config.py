import os


class Config:
    NUM_QUESTIONS = 300
    SEED = 42
    OUTPUT_DIR = "outputs"
    REPORT_DIR = "report"

    # Model API configurations
    MODELS = {
        "gemini": {
            "api_key_env": "GEMINI_API_KEY",
            "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "enabled": True,
        },
        "groq": {
            "api_key_env": "GROQ_API_KEY",
            "api_url": "https://api.groq.com/openai/v1/chat/completions",
            "enabled": True,
        },
    }

    @staticmethod
    def get_api_key(model_name: str) -> str:
        info = Config.MODELS[model_name]
        key_env = info.get("api_key_env")
        if key_env is None:
            return ""
        return os.environ.get(key_env, "")
