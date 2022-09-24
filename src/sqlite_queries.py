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