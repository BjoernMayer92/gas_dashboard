create_company_table_query ="""
CREATE TABLE IF NOT EXISTS company (
    eic TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    url TEXT NOT NULL,
    type TEXT NOT NULL,
    country TEXT NOT NULL,
    image TEXT NOT NULL
)
"""

insert_company_query = """ 
INSERT INTO company (eic, name, short_name, url, type, country, image)
        values (?, ?, ?, ? ,? ,?,?)
"""

create_facility_table_query ="""
CREATE TABLE IF NOT EXISTS facilities (
    eic TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    country TEXT NOT NULL,
    company_eic TEXT NOT NULL,
    FOREIGN KEY (company_eic)
       REFERENCES company (company_eic) 
)
"""

insert_facility_query = """ 
INSERT INTO facilities (eic, name, type, country, company_eic)
        values (?, ?, ?, ?, ? )
"""

insert_location_query = """ 
UPDATE facilities
SET lat = ? ,
    lon = ? ,
    google_location_name = ?
WHERE eic = ?
"""


create_timeseries_table_query="""
            CREATE TABLE IF NOT EXISTS 'Data' (
                gasDayStart DATE,
                gasInStorage FLOAT,
                injection FLOAT,
                withdrawal FLOAT,
                workingGasVolume FLOAT,
                injectionCapacity FLOAT,
                withdrawalCapacity FLOAT,
                status TEXT,
                trend FLOAT,
                full FLOAT,
                facility_eic TEXT,
                PRIMARY KEY (facility_eic, gasDayStart),
                FOREIGN KEY (facility_eic)
                    REFERENCES company (facility_eic) 
            )
            """

insert_timeseries_query = """ 
        INSERT INTO 'Data' (gasDayStart, gasInStorage, injection, withdrawal, workingGasVolume, injectionCapacity, withdrawalCapacity, status, trend, full, facility_eic)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

def add_cols(cursor, table_name, col_dict):
    table_info = cursor.execute("PRAGMA TABLE_INFO({})".format(table_name)).fetchall()
    table_cols = list(map( lambda x: x[1], table_info))

    for col_name, col_type in col_dict.items():
        if not(col_name in table_cols):
            cursor.execute("alter table {} add column '{}' '{}'".format(table_name, col_name, col_type))
