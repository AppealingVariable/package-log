import sqlite3
import csv
import time
import os
import subprocess
import random

# package_statuses:
# 0 = checked in/on-hand
# 1 = checked out/given to resident
# 2 = checked in, missing

#GLOBAL VARIABLES
db_name = 'package-log.db'
tb_create = """CREATE TABLE package_log(check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP, check_out_time TIMESTAMP, delivered_by TEXT, apartment TEXT, barcode_scan TEXT, package_status INT)"""

sqlite_connection = sqlite3.connect(db_name)
cursor = sqlite_connection.cursor()


##################################


def db_connect():
    global sqlite_connection
    global cursor
    # sqlite_connection = sqlite3.connect(db_name)
    # cursor = sqlite_connection.cursor()
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='package_log';""")
    if cursor.fetchone() is not None:
        pass
    else:
        create_table()

def db_close():
    sqlite_connection.close()

def create_table():
    try:
        cursor.execute(tb_create)

    except sqlite3.OperationalError:
        pass


def check_in(package_dict):
    sql_insert = '''INSERT INTO package_log (delivered_by, apartment, barcode_scan, package_status) VALUES (:delivered_by, :apartment, :barcode_scan, :package_status)'''
    cursor.execute(sql_insert, package_dict)
    sqlite_connection.commit()

def check_out(barcode):
    update_cursor = sqlite_connection.cursor()
    update_cursor.execute("SELECT * FROM package_log WHERE check_out_time IS NULL AND barcode_scan=? ", (barcode,))

    update_cursor.execute('''UPDATE package_log SET check_out_time = CURRENT_TIMESTAMP, package_status = 1 WHERE check_out_time IS NULL AND barcode_scan=?''', (barcode,))
    update_cursor.execute("SELECT * FROM package_log WHERE barcode_scan=? ", (barcode,))

    sqlite_connection.commit()

def db_search(search_dict):         #check_in_time, check_out_time, delivered_by, apartment, barcode_scan, package_status:
    sql_search_expression = "SELECT * FROM package_log WHERE "
    search_cursor = sqlite_connection.cursor()

    #generate sql query
    for key in search_dict:
        if search_dict[key] != '':
            if key == "check_in_time" or key == "check_out_time":
                #format dates for query
                sql_search_expression+= 'date(' + key + ") = '" + str(search_dict[key]) + "' AND "
            else:
                sql_search_expression+= key + " = '" + str(search_dict[key]) + "' AND "

    # sql_search_expression = sql_search_expression[:-4]
    search_cursor.execute(sql_search_expression[:-4])
    output_temp_file(search_cursor)


def db_manual_report(report_dict):
    sql_report_expression = "SELECT * FROM package_log WHERE "
    report_cursor = sqlite_connection.cursor()

    # generate sql query
    for key in report_dict:
        if report_dict[key] != '':
            if key == "check_in_time_start" or key == "check_out_time_start":
                # format dates for query
                end_key = key[:-6] + '_end'
                sql_report_expression += 'date(' + key[:-6] + ") BETWEEN '" + str(report_dict[key]) + "' AND '" + str(report_dict[end_key]) + "' AND "
            elif key == "check_in_time_end" or key == "check_out_time_end":
                pass
            else:
                sql_report_expression += key + " = '" + str(report_dict[key]) + "' AND "

    sql_report_expression = sql_report_expression[:-4] + 'GROUP BY apartment'
    report_cursor.execute(sql_report_expression)

    output_temp_file(report_cursor)


def count_received_by_apartment_date_range(count_dict):
    sql_count_expression = f'''SELECT apartment
    , COUNT(*) AS Total
    , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
    , COUNT(package_status) FILTER (WHERE package_status = 1) AS Delivered
    , COUNT(package_status) FILTER (WHERE package_status = 2) AS Missing
    FROM package_log WHERE date(check_in_time) BETWEEN '{count_dict['check_in_time_start']}' AND '{count_dict['check_in_time_end']}' GROUP BY apartment ORDER BY apartment; '''
    function_cursor = sqlite_connection.cursor()
    function_cursor.execute(sql_count_expression)
    output_temp_file(function_cursor)



def all_onhand_count():
    sql_count_expression = f'''SELECT apartment
    , COUNT(*) AS Total
    , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
    FROM package_log GROUP BY apartment ORDER BY apartment; '''
    function_cursor = sqlite_connection.cursor()
    function_cursor.execute(sql_count_expression)
    output_temp_file(function_cursor)

def output_temp_file(function_cursor):
    temp_file_name = 'temp/' + str(int(time.time())) + '.csv'
    search_file_path = os.path.abspath(temp_file_name)
    with open(temp_file_name, 'w', newline='') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
        csv_out.writerow(d[0] for d in function_cursor.description)
        for row in function_cursor:
            csv_out.writerow(row)

    # os.system(search_file_path)
    subprocess.Popen("start " + search_file_path, shell=True)


def make_test_entries():
    carriers_dict = {0: 'Amazon',
                     1: 'Fedex',
                     2: 'US Postal',
                     3: 'DHL',
                     4: 'UPS',
                     5: 'Other'
                     }
    for i in range(10000):
        package_info = dict(apartment=random.randint(1,3000), delivered_by=carriers_dict[random.randint(0,5)], barcode_scan=i,
                            package_status=random.randint(0,2))
        check_in(package_info)
