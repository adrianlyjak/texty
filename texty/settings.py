from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model_large: str = "openai/gpt-4o"
    llm_model_small: str = "openai/gpt-3.5-turbo"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    # if true, send a json_schema param, for llama.cpp for typed json responses
    llama_cpp_json_schema: Optional[bool] = None
    # if true, use json mode instead of a tool call
    openai_json_mode: Optional[bool] = None
    openai_tool_mode: Optional[bool] = None


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        


settings = Settings()
