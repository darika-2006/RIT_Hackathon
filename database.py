import os

# from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

# load_dotenv()

DATABASE_URL = (
    f"host={'localhost'} "
    f"port={'5432'} "
    f"dbname={'RIT'} "
    f"user={'postgres'} "
    f"password={'Bala@2007'}"
)

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    open=True
)