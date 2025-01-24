
import os
import pyodbc, struct
from azure import identity

class AzureDbApi:
    # TODO: A lot of hard-code here, need to be refactored
    def __init__(self) -> None:

        self.connection = None
        self.create_connection()

    
    def create_connection(self):
        try:
            credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)

            token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")

            token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

            SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h

            conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:igoarserver.database.windows.net;DATABASE=igoarservices;', attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})

            self.connection = conn

        except Exception as e:
            print(f"Failed to connect to Azure DB: {e}")
            return
    
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
