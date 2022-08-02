import pandas as pd
from sqlalchemy import (create_engine, MetaData, Table, column, Integer, String)

server = "localhost"
db = "Project"
userid = "postgres"
pwd = "password"
port = 5432

try:
    engine = create_engine(f'postgresql://{userid}:{pwd}@{server}:{port}/{db}')
    metadata = MetaData(engine)



    with pd.ExcelFile('Master file pfm.xlsx') as xlsr:
        df = pd.read_excel(xlsr)
        df.to_sql(name="sample_pfm", con=engine, if_exists='append', index=False)

    with pd.ExcelFile('Master file IC.xlsx') as xlsrR:
        df = pd.read_excel(xlsrR)
        df.to_sql(name="sample_IC", con=engine, if_exists='append', index=False)
except Exception as error:
    print(str(error))