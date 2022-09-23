def add_row(cursor, table_name, col_name, col_type):
    table_info = cursor.execute("PRAGMA TABLE_INFO({})".format(table_name)).fetchall()
    table_cols = list(map( lambda x: x[1], table_info))

    if not(col_name in table_cols):
        cursor.execute("alter table {} add column '{}' '{}'".format(table_name, col_name, col_type))


def update_value(conn,table_name, col_value_dict, row_value_dict):

    sql_partial_update="UPDATE '{}'".format(table_name)
    sql_partial_set = "SET "
    sql_partial_where="WHERE "

    for col in sorted(col_value_dict)[:-1]:
        sql_partial_set= sql_partial_set+"{} = '{}',\n".format(col, col_value_dict[col])    
    sql_partial_set= sql_partial_set+"{} = '{}'".format(sorted(col_value_dict)[-1], col_value_dict[sorted(col_value_dict)[-1]])
    
    for row in row_value_dict:
        sql_partial_where = sql_partial_where+ "{} = '{}'".format(row, row_value_dict[row] )
    
    sql_update_string = "\n".join([sql_partial_update, sql_partial_set, sql_partial_where])

    try:
        c = conn.cursor()
        c.execute(sql_update_string)
        conn.commit()
    except:
        print("An exception occurred")
    

def insert_row(conn, table_name,  col_name_list, data): 
    cursor = conn.cursor()
    
    assert len(col_name_list) == len(data)

    col_number = len(col_name_list)
    value_string = "("
    for col in range(col_number-1):
        value_string = value_string + "?," 
    value_string= value_string + "?)"

    sql_insert_string = ''' INSERT INTO '{}'{}
            VALUES{} '''.format(table_name, tuple(col_name_list), value_string)            
    
    cursor.execute(sql_insert_string, tuple(data))
    conn.commit()