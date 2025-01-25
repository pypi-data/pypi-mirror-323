import redshift_connector
import pandas
from . import creds
import gspread

def get_help():
    """
    Function built to supply help about whats in this package. Please see individual
    functions for more detailed information on parameters and purpose

    Function list
    ---------
    start_engine()
    query_redshift()
    gsheets_start()

    """

def start_engine(user_creds):
    conn = redshift_connector.connect(
    host=user_creds['host'],
    port=user_creds['port'],
    database=user_creds['db'],
    user=user_creds['usr'],
    password=user_creds['pwd']
    )

    #outdated non-functioning sqlalchemy/psycopg2 code
    #db_url = "postgresql://{usr}:{pwd}@{host}:{port}/{db}".format(**user_creds)
    #return create_engine(db_url)

    return conn.cursor()

def query_redshift(query):
    connector = start_engine(creds.redshift_user)
    connector.execute(query)
    result: pandas.DataFrame = connector.fetch_dataframe()
    return result

def gsheets_start():
    return gspread.service_account_from_dict(creds.gspread_creds)