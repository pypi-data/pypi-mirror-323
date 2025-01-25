from abc import ABC, abstractmethod

try:
    import pyterrier as pt
except ImportError:
    raise ImportError("PyTerrier needs to be installed to use PyTerrier transformer interfaces")

import duckdb
import numpy as np
import pandas as pd

import duckdb_selective_search.retriever as _retriever


class MinScoreTransformer(pt.Transformer):
    def __init__(self, inner: pt.Transformer, min_score: int | float):
        super().__init__()
        self.inner = inner
        self.min_score = min_score

    def transform(self, inp):
        result = self.inner.transform(inp)
        return result[result['score'] >= self.min_score]

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f'MinScore({self.inner!r} >= {self.min_score})'


class DuckDBTransformer(pt.Transformer, ABC):

    @abstractmethod
    def _transform_single(self, qid: str, query: str, query_info: pd.DataFrame) -> duckdb.DuckDBPyRelation:
        pass

    def transform(self, queries: pd.DataFrame):
        # print(getattr(self, 'resource_selection', getattr(self, 'retriever', None)))
        results = []
        for (qid, query), query_info in queries.groupby(['qid', 'query'], sort=False):
            result = self._transform_single(qid, query, query_info).fetchdf()
            if 'score' in result.columns:
                pt.model.add_ranks(result, single_query=True)
            result['qid'] = qid
            results.append(result)

        try:
            results = pd.concat(results)
        except ValueError:
            print(queries)
            print(results)
            raise

        input_cols = queries.columns[ (queries.columns == "qid") | (~queries.columns.isin(results.columns))].tolist()
        merge_cols = ["qid"]

        # Document re-ranking
        if "docno" in queries.columns and hasattr(self, 'retriever') and ("shard" not in queries.columns or not np.array_equal(queries["docno"], queries["shard"])):
            input_cols.append("docno")
            merge_cols.append("docno")

        # Shard re-ranking
        if "shard" in queries.columns and hasattr(self, 'resource_selection'):
            input_cols.extend(["docno", "shard"])
            merge_cols.extend(["docno", "shard"])

        return queries[input_cols].merge(results, on=merge_cols, how='left').fillna({'score': 0})

    def __ge__(self, min_score):
        return MinScoreTransformer(self, min_score)


class DuckDBRetriever(DuckDBTransformer):
    def __init__(self, conn: duckdb.DuckDBPyConnection, schema: str, **kwargs):
        super().__init__()
        self.retriever = _retriever.DuckDBRetriever(conn, schema, **kwargs)

    def _transform_single(self, qid: str, query: str, query_info: pd.DataFrame) -> duckdb.DuckDBPyRelation:
        print(qid, query)
        if 'shard' in query_info.columns:
            shards = sorted(query_info['shard'].tolist())
            res = self.retriever.selective_search(qid, query, shards)
        else:
            res = self.retriever.search(qid, query)
        return self.retriever.conn.query('SELECT * EXCLUDE (name), "name" AS docno FROM res')

    @property
    def num_shards(self):
        return self.retriever.num_shards

    def __str__(self):
        return str(self.retriever)

    def __repr__(self):
        return f'DuckDBRetriever({self.retriever!r})'


class AUReC(pt.Transformer):
    def __init__(self, conn: duckdb.DuckDBPyConnection, schema: str, weighted: bool = False):
        self.conn = conn
        self.schema = schema
        self.weighted = weighted

    def transform(self, run: pd.DataFrame) -> pd.DataFrame:
        cumsums = self.conn.query(
            f"""
                WITH counts AS (
                    SELECT qid, shard, COUNT(*) AS cnt
                    FROM (SELECT * REPLACE (docno AS name) FROM run)
                    JOIN {self.schema}.docs USING (name)
                    GROUP BY ALL
                ),
                pseudo_relevance_counts AS (
                    SELECT qid, shard, IFNULL(cnt, 0) AS cnt
                    FROM (
                        FROM (SELECT DISTINCT qid FROM run), (SELECT DISTINCT shard FROM {self.schema}.docs)
                    )
                    LEFT JOIN counts USING (qid, shard)
                )
                SELECT
                    qid,
                    shard,
                    SUM(cnt) OVER w_cumsum / SUM(cnt) OVER w_all AS cumsum
                FROM pseudo_relevance_counts
                WINDOW w_cumsum AS (
                    PARTITION BY qid
                    ORDER BY cnt DESC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), w_all AS (
                    PARTITION BY qid
                );
            """
        )

        if self.weighted:
            result = self.conn.query(
                f"""
                    WITH shard_sizes AS (
                        SELECT shard, COUNT(*) AS shard_size
                        FROM {self.schema}.docs
                        GROUP BY shard
                    ),
                    areas AS (
                        SELECT
                            qid,
                            shard,
                            (cumsum + lag(cumsum, 1, 0) OVER (PARTITION BY qid ORDER BY cumsum)) * shard_size AS area,
                        FROM cumsums
                        JOIN shard_sizes USING (shard)
                    )
                    SELECT
                        qid,
                        SUM(area) / (SELECT SUM(shard_size) FROM shard_sizes) / 2 AS score
                    FROM areas
                    GROUP BY qid;
                """
            )
        else:
            result = self.conn.query(
                """
                    WITH areas AS (
                        SELECT
                            qid,
                            shard,
                            (cumsum + lag(cumsum, 1, 0) OVER (PARTITION BY qid ORDER BY cumsum)) AS area,
                        FROM cumsums
                    )
                    SELECT
                        qid,
                        SUM(area) / COUNT(*) / 2 AS score
                    FROM areas
                    GROUP BY qid;
                """
            )

        return result.fetchdf()

    def __str__(self):
        if self.weighted:
            return 'wAUReC'
        else:
            return 'AUReC'
