import pandas as pd
from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String, Float)

server = "localhost"
db = "test"
userid = "postgres"
pwd = "password"
port = 5432

try:
    engine = create_engine(f'postgresql://{userid}:{pwd}@{server}:{port}/{db}')
    meta_data = MetaData(engine)
    Sample_ic = Table("Sample_ic", meta_data,
                      Column("sample_id", String(15), primary_key = True),
                      Column("bridge_ic", Float),
                      Column("bridge_width", Float),
                      Column("full_width_ic", Float))
    Sample_pfm = Table("Sample_pfm", meta_data,
                       Column("sample_id", String(15), primary_key = True),
                       Column("average", Float))
    meta_data.create_all(engine)




    with pd.ExcelFile('Master file pfm.xlsx') as xlsr:
        df = pd.read_excel(xlsr)
        df.to_sql(name="Sample_pfm", con=engine, if_exists='append', index=False)

    with pd.ExcelFile('Master file IC.xlsx') as xlsrR:
        df = pd.read_excel(xlsrR)
        df.to_sql(name="Sample_ic", con=engine, if_exists='append', index=False)
except Exception as error:
    print(str(error))