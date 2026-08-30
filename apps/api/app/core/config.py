import os

# Since Pydantic V2 does not include BaseSettings by default (it was moved to pydantic-settings), 
# we can declare a standard class or install pydantic-settings. 
# We listed pydantic to be V2, so to keep things simple we will parse settings cleanly using a robust class.

class Settings:
    PROJECT_NAME: str = "AI Codebase Investigator"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Server configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/codebase_investigator"
    )
    
    # AI Config
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    
    # GitHub Integration
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    
    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY)

settings = Settings()
