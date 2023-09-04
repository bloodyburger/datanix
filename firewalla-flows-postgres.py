#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
from hashlib import md5

URL = '<MSP_URL>/v2/flows'
HEADERS = {'Authorization':'Token <MSP TOKEN>'}
PARAMS = {'limit': 1000}
cursor = True
df_data = pd.DataFrame()

while cursor:
    print('Params used is {}'.format(PARAMS))
    r = requests.get(URL,headers = HEADERS, params=PARAMS)
    if 'next' in r.json() :
        if r.json()['next'] is not None:
            PARAMS = {'limit': 1000,'end': r.json()['next']}
        else:
            cursor = False
    else:
        cursor = False
    response = (r.json()['results'])
    df_temp = pd.json_normalize(response)
    df_data = pd.concat([df_data, df_temp])

def df_upsert(engine, data_frame, table_name, schema=None, match_columns=None):
    """
    Perform an "upsert" on a PostgreSQL table from a DataFrame.
    Constructs an INSERT … ON CONFLICT statement, uploads the DataFrame to a
    temporary table, and then executes the INSERT.
    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be upserted.
    table_name : str
        The name of the target table.
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy Engine to use.
    schema : str, optional
        The name of the schema containing the target table.
    match_columns : list of str, optional
        A list of the column name(s) on which to match. If omitted, the
        primary key columns of the target table will be used.
    """
    table_spec = ""
    if schema:
        table_spec += '"' + schema.replace('"', '""') + '".'
    table_spec += '"' + table_name.replace('"', '""') + '"'

    df_columns = list(data_frame.columns)
    if not match_columns:
        insp = sa.inspect(engine)
        match_columns = insp.get_pk_constraint(table_name, schema=schema)[
            "constrained_columns"
        ]
    columns_to_update = [
        col for col in df_columns if col not in match_columns]
    insert_col_list = ", ".join(
        [f'"{col_name}"' for col_name in df_columns])
    stmt = f"INSERT INTO {table_spec} ({insert_col_list})\n"
    stmt += f"SELECT {insert_col_list} FROM temp_table\n"
    match_col_list = ", ".join([f'"{col}"' for col in match_columns])
    stmt += f"ON CONFLICT ({match_col_list}) DO UPDATE SET\n"
    stmt += ", ".join(
        [f'"{col}" = EXCLUDED."{col}"' for col in columns_to_update]
    )

    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS temp_table")
        conn.exec_driver_sql(
            f"CREATE TEMPORARY TABLE temp_table AS SELECT * FROM {table_spec} WHERE false"
        )
        data_frame.to_sql("temp_table", conn,
                          if_exists="append", index=False)
        conn.exec_driver_sql(stmt)

CONNECTION_STRING="postgresql://postgres:yourpassword@<HOST:IP>/<DB>"
engine = sa.create_engine(CONNECTION_STRING,isolation_level="AUTOCOMMIT")

df_data['hashkey'] = df_data['ts'].astype(str) + df_data['count'].astype(str)  + df_data['device.port'].astype(str) + df_data['device.ip'].astype(str) + df_data['gid'].astype(str) + df_data['protocol'].astype(str)  + df_data['remote.ip'].astype(str) + df_data['remote.domain'].astype(str) + df_data['remote.port'].astype(str)
df_data['hashkey'] = df_data['hashkey'].apply(lambda x: md5(x.encode("utf8")).hexdigest())

df_data = df_data.drop_duplicates()
df_upsert(engine, df_data, "firewalla_flows", schema="nathass")
print("Data load completed")
