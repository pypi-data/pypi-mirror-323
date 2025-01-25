import duckdb
import pyarrow as pa

from ._util import _get_if_file


def sql(s, **dfs):
    db = Database(**dfs)
    out = db.sql(s)

    return out


class Database:
    def __init__(self, **dfs):
        con = duckdb.connect(
            database = ':memory:',
            config = {'enable_external_access': False},
        )

        for tbl_name, df in dfs.items():
            df = pa.Table.from_pandas(df)
            con.register(tbl_name, df)

        self._con = con

    def __repr__(self):
        tables = _yield_table_lines(self)
        tables = [
            f'\n    {t}'
            for t in tables
        ]
        tables = ''.join(tables)
        tables = tables or ' None'

        out = 'pdx2.Database:' + tables

        return out

    def sql(self, s):
        s = _get_if_file(s)
        out = self._con.execute(s).df()
        return out


def _yield_table_lines(db):
    df = db.sql('show all tables')

    for _, tbl in df.iterrows():
        name = tbl['name']
        columns = list(tbl['column_names'])
        n = db.sql(f'select count() from {name}').asitem()

        yield f'{name}: {n} x {columns}'
