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

    print(
        """
        Function built to supply help about whats in this package. Please see individual
        functions for more detailed information on parameters and purpose

        Function list
        ---------
        start_engine()
        query_redshift()
        gsheets_start()
        """
    )

def start_engine(user_creds):
    """
    The purpose of this function is to get a redshift connection using credentials, usually stored in
    a creds file.

    This connection is built using the redshift_connector package

    Params
    ------
    user_creds : credentials, dict

    Output
    ------
    conn: active connection to redshift

    """
    conn = redshift_connector.connect(
    host=user_creds['host'],
    port=user_creds['port'],
    database=user_creds['db'],
    user=user_creds['usr'],
    password=user_creds['pwd']
    )

    return conn.cursor()

def query_redshift(query):
    """
    The purpose of this function is to query redshift, and return a pandas dataframe.
    This function is utilizing start_engine() to generate its connection, and is grabbing
    credentials from a local creds file.

    Params
    ------
    query : actual query to be used, str

    Output
    ------
    result: pandas dataframe based on query

    """
    connector = start_engine(creds.redshift_user)
    connector.execute(query)
    result: pandas.DataFrame = connector.fetch_dataframe()
    return result

def gsheets_start():
    """
    The purpose of this function is to load credentials and authorize gspread. The creds are grabbed 
    directly from a local creds file.

    Output
    ------
    active connection to gspread 

    """
    return gspread.service_account_from_dict(creds.gspread_creds)