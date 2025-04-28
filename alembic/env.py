from __future__ import with_statement
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.declarative import declarative_base
from logging.config import fileConfig

# Импортируем свои модели, чтобы Alembic знал о них
from models import Base

# Получаем метаданные моделей
target_metadata = Base.metadata

# Оставь этот код без изменений, это стандартный код для Alembic
config = context.config
fileConfig(config.config_file_name)

# Создаем подключение к базе данных
engine = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)

# Создаем сессию
with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()
