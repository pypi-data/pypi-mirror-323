import duckdb


def get_conn(db_file: str, memory_limit: str = None, threads: int = None) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(db_file)

    if memory_limit is not None:
        conn.execute(f"SET memory_limit = '{memory_limit}';")
    if threads is not None:
        conn.execute(f"SET threads = {threads};")

    return conn
