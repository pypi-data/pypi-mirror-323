from pyodbc import Cursor, Connection, Row, connect
import logging
import functools
import datetime
import decimal

# Setting up a logger for database operations
database_command_logger = logging.getLogger('SQL Database')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

data_type_map = {
    int: 'INTEGER',               # INTEGER in SQL for Python int
    float: 'REAL',                # REAL in SQL for Python float
    str: 'NVARCHAR(255)',         # TEXT in SQL for Python str. VARCHAR or NVARCHAR can be used in other SQL databases
    bool: 'BOOLEAN',              # BOOLEAN in SQL for Python bool (SQLite stores this as INTEGER 0 or 1)
    bytes: 'BLOB',                # BLOB in SQL for Python bytes
    datetime.date: 'DATE',        # DATE in SQL for Python datetime.date
    datetime.datetime: 'DATETIME',# DATETIME in SQL for Python datetime.datetime
    datetime.time: 'TIME',        # TIME in SQL for Python datetime.time
    decimal.Decimal: 'NUMERIC',   # NUMERIC in SQL for Python decimal.Decimal (useful for precise fixed-point arithmetic)
    list: 'TEXT',                 # Serialized list (e.g., JSON) stored as TEXT in SQL
    dict: 'TEXT',                 # Serialized dictionary (e.g., JSON) stored as TEXT in SQL
    None: 'NULL',                 # NULL in SQL for Python None
}
class Database:

    def __init__(self, server:str = None, database:str = None, **kwargs):
        """Initializes a new Database object with connection details.

        This class sets up the configuration for a database connection. It allows for different
        authentication methods and can be customized further with additional keyword arguments.

        Args:
            username (str, optional): The username for database login. It's required if the login method is not 'windows_auth'.
            password (str, optional): The password for database login. It's required if the login method is not 'windows_auth'.
            server (str, optional): The server address of the database.
            database (str, optional): The name of the specific database to connect to.
            **kwargs: Additional keyword arguments for more customization.
        """
        self.username:str = kwargs.get('username')
        self.password:str = kwargs.get('password')
        self.server:str = server
        self.database:str = database

        if self.username and self.password:
            self.connection:Connection = self.login_sql_server_authentication(self.server, self.database, self.username, self.password)

        else:
            self.connection:Connection = self.login_windows_authentication(self.server, self.database)

    def __str__(self) -> str:
        return self.server+'-'+self.database

    def __db_operation(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            connection: Connection = self.connection
            cursor = None
            try:
                cursor = connection.cursor()
                result = func(self, cursor, *args, **kwargs)
                connection.commit()
                return result
            except Exception as e:
                print(f'An error occurred: {e}')
                connection.rollback()
                return None
            finally:
                if cursor:
                    cursor.close()
        return wrapper

    def login_windows_authentication(self, server: str, database: str) -> Connection:
        """
        Establishes a connection to a SQL Server database using provided credentials.

        :param server: The address of the SQL Server database (IP or hostname).
        :param database: The name of the database to connect to.

        :return: A pyodbc Connection object if the connection is successful, None otherwise.

        """
        connection = ('DRIVER={SQL Server};'
                f'Trusted_Connection=Yes;'
                f'SERVER={server};'
                f'DATABASE={database};')
        try:
            connection = connect(connection, timeout = 120)
            database_command_logger.info('Connection Successful')
            return connection
        except Exception as e:
            database_command_logger.error(f'{e}')
            return None
            
    def login_sql_server_authentication(self, server: str, database: str, username: str, password: str) -> Connection:
        """
        Establishes a connection to a SQL Server database using provided credentials.

        :param server: The address of the SQL Server database (IP or hostname).
        :param database: The name of the database to connect to.
        :param username: The username for database authentication.
        :param password: The password for database authentication.

        :return: A pyodbc Connection object if the connection is successful, None otherwise.

        """
        connection = ('DRIVER={SQL Server};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}')
        try:
            connection = connect(connection, timeout = 120)
            database_command_logger.info('Connection Successful')
            return connection
        except Exception as e:
            database_command_logger.critical(f'{e}')
            return None
        
    # @__db_operation
    # def create_table(self, cursor:Cursor, table_name:str, column_definitions:dict[str:type], primary_key:list = None):
    #     try:
    #         data_types = '('
    #         for column_name, data_type in column_definitions.items():
    #             data_types += f'{column_name} {data_type_map.get(data_type)}, '
    #         if primary_key:
    #             primary_key_str = 'PRIMARY KEY ('
    #             for key in primary_key:
    #                 primary_key_str += f'{key}, '
    #             primary_key_str = primary_key_str[0:-2] + ')'
    #             data_types += primary_key_str + ')'
    #         else:
    #             data_types = data_types[0:-2] + ')'
    #         statement = f'CREATE TABLE {table_name} {data_types}'
    #         cursor.execute(statement)
    #         logging.debug(f'SUCCESS: Table Created. {statement}')
    #         self.connection.commit()
    #         return True
    #     except Exception as e:
    #         logging.critical(f'FAILURE: Table Not Created. {statement}')
    #         logging.debug(e, exc_info=True)
    #         return False
    
    # @__db_operation
    # def drop_table(self, cursor:Cursor, table_name:str):
    #     try:
    #         statement = f'DROP TABLE IF EXISTS {table_name}'
    #         cursor.execute(statement)
    #         logging.debug(f'SUCCESS: Table Dropped. {statement}')
    #         self.connection.commit()
    #         return True
    #     except Exception as e:
    #         logging.critical(f'FAILURE: Table Not Dropped. {statement}')
    #         logging.debug(e, exc_info=True)
    #         return False
    
    @__db_operation
    def select(
        self,
        cursor: Cursor,
        table_name: str,
        distinct: bool = False,
        cols: str = '*',
        alias: str = None,
        join_type: str = None,
        join_table: str = None,
        join_alias: str = None,
        on: str = None,
        where: str = None,
        group_by: str = None,
        with_rollup: bool = False,
        having: str = None,
        order_by: str = None,
        order_asc_desc: str = None,
        nulls_first_last: str = None,
        limit: int = None,
        offset: int = None,
        set_operation: str = None,
        another_query: str = None,
        **kwargs
    ):
        try:
            statement = ''
            def quote_columns(column_str):
                if column_str == '*':
                    return column_str
                return ', '.join(f'[{col.strip()}]' for col in column_str)                 
            query_parts = ['SELECT']
            if distinct:
                query_parts.append('DISTINCT')

            query_parts.append(f'{quote_columns(cols)} FROM {table_name}')

            if alias:
                query_parts.append(f'AS {alias}')

            if join_type and join_table and on:
                join_alias_part = f' AS {join_alias}' if join_alias else ''
                query_parts.append(f'{join_type} {join_table}{join_alias_part} ON {on}')

            if where:
                query_parts.append(f'WHERE {where}')

            if group_by:
                group_by_part = f'GROUP BY {group_by}'
                if with_rollup:
                    group_by_part += ' WITH ROLLUP'
                query_parts.append(group_by_part)

            if having:
                query_parts.append(f'HAVING {having}')

            if order_by:
                order_by_part = f'ORDER BY {order_by}'
                if order_asc_desc:
                    order_by_part += f' {order_asc_desc}'
                if nulls_first_last:
                    order_by_part += f' {nulls_first_last}'
                query_parts.append(order_by_part)

            if limit is not None:
                query_parts.append(f'LIMIT {limit}')

            if offset is not None:
                query_parts.append(f'OFFSET {offset}')

            if set_operation and another_query:
                query_parts.append(f'{set_operation} ({another_query})')

            statement = ' '.join(query_parts)
            cursor.execute(statement)
            logging.debug(f'SUCCESS: {statement}')
            results = cursor.fetchall()
            try:
                # If the result is a column with multiple rows
                if len(results[0]) == 1:
                    results = [row[0] for row in results]
                    # If the result is a a single value
                    if len(results) == 1:
                        result = results[0]
                    return result
                else:
                    return results
            except:
                return results
            
        except Exception as e:
            logging.critical(f'FAILURE: {statement}')
            logging.debug(e, exc_info=True)

    @__db_operation
    def insert(self, cursor:Cursor, table_name:str, columns:list[str]=None, values:list=None, dict_data:dict=None):
        if dict_data:
            columns = list(dict_data.keys())
            values = list(dict_data.values())
        try:
            placeholders = ', '.join(['?' for _ in columns])
            statement = f'INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})'
            cursor.execute(statement, values)
            logging.debug(f'SUCCESS: {statement}')
            self.connection.commit()
            return True
        except Exception as e:
            logging.critical(f'FAILURE: {statement}')
            logging.debug(e, exc_info=True)
            return False

    @__db_operation
    def statement(self, cursor:Cursor, statement:str):
        # To pass params to the statement, give the function a tuple. The statement will use the param tuple arguements in order. They replace the question marks in the statement, in order.
        try:
            cursor.execute(statement)
            logging.debug(f'SUCCESS: {statement}')
            result = cursor.fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            logging.critical(f'FAILURE: {statement}')
            logging.debug(e, exc_info=True)
            return False
        
    @__db_operation
    def get_definition(self, cursor:Cursor, table_name:str, schema_name:str='dbo'):
        columns = cursor.columns(table=table_name, schema=schema_name)
        columns_raw_dict = {}
        for column in columns:
            columns_raw_dict[column.column_name] = {
                "TABLE_CAT": column.table_cat,
                "TABLE_SCHEM": column.table_schem,
                "TABLE_NAME": column.table_name,
                "COLUMN_NAME": column.column_name,
                "DATA_TYPE": column.data_type,
                "TYPE_NAME": column.type_name,
                "COLUMN_SIZE": column.column_size,
                "BUFFER_LENGTH": column.buffer_length,
                "DECIMAL_DIGITS": column.decimal_digits,
                "NUM_PREC_RADIX": column.num_prec_radix,
                "NULLABLE": column.nullable,
                "REMARKS": column.remarks,
                "COLUMN_DEF": column.column_def,
                "SQL_DATA_TYPE": column.sql_data_type,
                "SQL_DATETIME_SUB": column.sql_datetime_sub,
                "CHAR_OCTET_LENGTH": column.char_octet_length,
                "ORDINAL_POSITION": column.ordinal_position,
                "IS_NULLABLE": column.is_nullable,
            }

        return columns_raw_dict