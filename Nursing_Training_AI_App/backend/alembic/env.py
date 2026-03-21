import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import ALL models so Alembic sees them
from core.database import Base
from models.user import User, UserProgress, UserSession
from models.training import Question, UserAnswer, TrainingSession, LearningPath, UserLearningPath

# NEW models (Phase 2)
from models.nursing import Speciality, Band, QuestionCategory, Trust, TrustQuestion, InterviewSession, InterviewAnswer

target_metadata = Base.metadata

# Get DATABASE_URL from environment
def get_url():
    return os.getenv("DATABASE_URL", "postgresql://nursing_user:nursing_password@localhost:5432/nursing_training_ai")

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
