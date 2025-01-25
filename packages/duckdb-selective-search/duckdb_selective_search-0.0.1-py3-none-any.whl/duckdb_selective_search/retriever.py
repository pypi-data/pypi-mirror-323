from functools import cached_property

import duckdb

from duckdb_selective_search.cache import CacheMixin



class DuckDBRetriever(CacheMixin):
    def __init__(self, conn: duckdb.DuckDBPyConnection, schema: str, num_results: int = 1000, **search_params):
        self.conn = conn
        self.schema = schema
        self.num_results = num_results

        self.search_params = search_params

    @property
    def _search_query(self):
        return f"""
            FROM {self.schema}.score_documents($query{self._param_list})
            ORDER BY score DESC;
        """

    @property
    def _topk_per_shard_query(self):
        return f"""
            FROM {self.schema}.score_documents($query{self._param_list})
            QUALIFY row_number() OVER (PARTITION BY shard ORDER BY score DESC) <= {self.num_results}
            ORDER BY score DESC;
        """

    @property
    def _param_list(self):
        return ''.join(f', {key} := {repr(value)}' for key, value in self.search_params.items())

    def search(self, qid: str, query: str) -> duckdb.DuckDBPyRelation:
        return self.query(self._search_query, params={'query': query})

    def topk_per_shard(self, qid: str, query: str) -> duckdb.DuckDBPyRelation:
        return self.query(self._topk_per_shard_query, params={'query': query})

    def selective_search(self, qid: str, query: str, shards: list[int]) -> duckdb.DuckDBPyRelation:
        all_results = self.topk_per_shard(qid, query)

        return self.conn.query(
            """
            FROM all_results
            WHERE shard IN $shards
            ORDER BY score DESC;
            """,
            params={'shards': shards}
        ).limit(self.num_results)

    def cost_in_postings(self, qid: str, query: str, shards: list[int] = None, per_shard: bool = False) -> int:
        if shards is None and not per_shard:
            res = self.query(
                f"""
                SELECT SUM(df)
                FROM {self.schema}.dict
                WHERE termid IN (SELECT termid FROM {self.schema}.get_termids($query));
                """,
                params={'query': query}
            )
        else:
            costs_per_shard = self.query(
                f"""
                SELECT shard, SUM(df) AS cost_in_postings
                FROM {self.schema}.shard_representations
                WHERE termid IN (SELECT termid FROM {self.schema}.get_termids($query))
                GROUP BY shard;
                """,
                params={'query': query}
            )

            if shards is None:
                filtered_shards = costs_per_shard
            else:
                filtered_shards = self.conn.query("FROM costs_per_shard WHERE shard in $shards", params={'shards': shards})

            if per_shard:
                return filtered_shards.fetchdf()

            res = self.conn.query("SELECT SUM(cost_in_postings) FROM filtered_shards;")

        x = res.fetchone()[0]

        return x

    @cached_property
    def num_shards(self) -> int:
        return self.conn.query(f'SELECT COUNT(DISTINCT shard) FROM {self.schema}.docs;').fetchone()[0]

    def __repr__(self):
        return f'{self.__class__.__name__}({self.schema}{self._param_list})'
