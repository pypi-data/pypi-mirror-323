import hashlib
from pathlib import Path
import pickle
from typing import Protocol
import duckdb


class DuckDBConnectionProtocol(Protocol):
    @property
    def conn(self) -> duckdb.DuckDBPyConnection: ...

    @property
    def schema(self) -> str: ...


class CacheMixin(DuckDBConnectionProtocol):
    def query(self, query: str, params: dict | None = None) -> duckdb.DuckDBPyRelation:
        query = self._clean_query(query)

        cache_file = self._get_cache_file(query)

        if not cache_file.exists():
            result = self.conn.query(query, params=params)
            if (cache_size := getattr(self, 'cache_size', None)) is not None:
                result = result.limit(cache_size)
            self.conn.execute(f"COPY result TO '{cache_file}';")

        return self.conn.query(f"FROM '{cache_file}';")

    def _get_cache_file(self, query: str, params: dict | None = None) -> Path:
        query_key = hashlib.md5(query.encode()).hexdigest()
        params_key = hashlib.md5(pickle.dumps(tuple(sorted(params.items())) if params is not None else None)).hexdigest()

        cache_dir = Path('.cache') / self.schema / query_key

        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)
            with open(cache_dir / 'query.sql', 'w') as f:
                f.write(query)

        return cache_dir / f'{params_key}.parquet'

    def _clean_query(self, query: str) -> list[str]:
        return '\n'.join([
            stripped_line
            for line in query.splitlines()
            if (stripped_line := line.strip())
        ])
