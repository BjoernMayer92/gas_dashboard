import sys
import os
import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path

root_dir = Path.cwd().parents[1]
conf_dir = os.path.join(root_dir,"config")


sys.path.append(str(conf_dir))

import config

extraction_keyword_list = config.AGSI_EXTRACTION_KEYWORD_LIST
extraction_keyword_type = config.AGSI_EXTRACTION_KEYWORD_TYPE
extraction_keyword_type_sql = config.AGSI_EXTRACTION_KEYWORD_TYPE_SQL

metadata_keyword_list = config.AGSI_METADATA_KEYWORD_LIST
metadata_keyword_type = config.AGSI_METADATA_KEYWORD_TYPE

api_string = config.AGSI_API_STRING
sys.path.append(str(config.SRC_DIR))

import agsi_api as agsi
import sqlite_functions

sql_database_file = config.SQL_DATABASE_FILE
conn = sqlite3.connect(sql_database_file)



if __name__ == '__main__':
    conn_cursor = conn.cursor()
    conn_cursor.execute('SELECT RowID FROM eic_listing') 
    row_id_list = conn_cursor.fetchall()


    # Add new columns in listing table
    for metadata_keyword in metadata_keyword_list:
        sqlite_functions.add_row(conn_cursor,
        table_name="eic_listing",
        col_name="metadata_"+metadata_keyword,
        col_type=metadata_keyword_type[metadata_keyword])


    # Add data to new columns
    for row_id in row_id_list:
        facility_entry = conn_cursor.execute('SELECT name,country, company, facility, query_string FROM eic_listing WHERE RowID={}'.format(row_id[0])).fetchall()
        name, country, company, facility, query_string = facility_entry[0]

        #Make initial request       
        initial_request_data = agsi.request_query_as_json(query_string)
        number_of_pages = initial_request_data["last_page"]
        metadata_dict = {}
        initial_request_data_first_entry = initial_request_data["data"][0]

        # Add metadate to eic_listing
        col_value_dict={}
        for metadata_keyword in metadata_keyword_list:
            metadata_value = initial_request_data_first_entry[metadata_keyword]
            col_value_dict["metadata_"+metadata_keyword]= metadata_value

        row_value_dict = {"name":name}
        
        conn_data_cursor = conn.cursor()
        table_name ="eic_listing"

        sql_string = sqlite_functions.update_value(conn, table_name,col_value_dict, row_value_dict )
        
        # Add Tables

        table_name = "_".join([country, company, facility])
        print(table_name)
        
        sql_create_table_string = "CREATE TABLE IF NOT EXISTS '{}' ( \n".format(table_name)
        
        for extraction_keyword in sorted(extraction_keyword_list)[:-1]:
            sql_create_table_string = sql_create_table_string + "{} {}, \n".format( extraction_keyword, extraction_keyword_type_sql[extraction_keyword])

        extraction_keyword =    sorted(extraction_keyword_list)[-1]     
        sql_create_table_string = sql_create_table_string + "{} {})".format( extraction_keyword, extraction_keyword_type_sql[extraction_keyword])

        c = conn.cursor()
        c.execute(sql_create_table_string)
        conn.commit()

        # Fill Tables
        agsi.curl_data_from_query_in_db(conn, query_string, table_name, extraction_keyword_list, extraction_keyword_type)

