import sqlite3
import csv
import time
import datetime
import subprocess

# package_statuses:
# 0 = checked in/on-hand
# 1 = checked out/given to resident
# 2 = checked in, missing
# 3 = entered in error

#GLOBAL VARIABLES
db_name = 'package-log.db'
tb_create = """CREATE TABLE package_log(check_in_time DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')), check_out_time TIMESTAMP, delivered_by TEXT, apartment TEXT, barcode_scan TEXT, package_status INT)"""

sqlite_connection = sqlite3.connect(db_name)
cursor = sqlite_connection.cursor()

status_dict = {
    0: "Checked In",
    1: "Checked Out",
    2: "Missing",
    3: "Mistake"
}
##################################
def error_logging(message):
    with open("error.log", "a") as file:
        file.write(f"\n{datetime.datetime.now()} {message}")

def time_string():
    return str(int(time.time()))

def today_date_string():
    string_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    return string_date

def db_connect():
    global sqlite_connection
    global cursor
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
    try:
        if 'package_count' in package_dict:
            for i in range(int(package_dict['package_count'])):
                if package_dict['barcode_scan'].startswith('MANUAL'):
                    package_dict['barcode_scan'] = 'MANUAL' + str(time.time())
                cursor.execute(sql_insert, package_dict)
                time.sleep(.01)
        else:
            cursor.execute(sql_insert, package_dict)
        sqlite_connection.commit()
        return True
    except Exception as exception_message:
        error_logging(repr(exception_message))
        return False

def check_out_barcode(barcode):
    update_cursor = sqlite_connection.cursor()
    update_cursor.execute("SELECT * FROM package_log WHERE check_out_time IS NULL AND barcode_scan=? ", (barcode,))
    update_cursor.execute('''UPDATE package_log SET check_out_time = CURRENT_TIMESTAMP, package_status = 1 WHERE check_out_time IS NULL AND barcode_scan=?''', (barcode,))
    sqlite_connection.commit()
    return True

def check_out_manual(package_info):
    try:
        check_out_cursor = sqlite_connection.cursor()
        sql_expression = f"UPDATE package_log SET check_out_time = CURRENT_TIMESTAMP, package_status = 1 WHERE check_out_time IS NULL AND barcode_scan IS '{package_info[2]}'; "

        check_out_cursor.execute(sql_expression)
        sqlite_connection.commit()
        return True

    except Exception as exception_message:
        error_logging(repr(exception_message))
        return False

def mark_as_error(package_info, status_update):
    try:
        check_out_cursor = sqlite_connection.cursor()
        sql_expression = f"UPDATE package_log SET check_out_time = CURRENT_TIMESTAMP, package_status = {status_update} WHERE check_out_time IS NULL AND barcode_scan IS '{package_info[2]}'; "

        check_out_cursor.execute(sql_expression)
        sqlite_connection.commit()
        return True

    except Exception as exception_message:
        error_logging(repr(exception_message))
        return False


def db_search_on_hand(search_dict):
    sql_search_expression = f"SELECT * FROM package_log WHERE apartment = '{search_dict['apartment'].upper()}' AND package_status = 0 ORDER BY check_in_time; "
    if search_dict['apartment'].upper() == '':
        sql_search_expression = "SELECT * FROM package_log WHERE package_status = 0 ORDER BY apartment, check_in_time; "
    search_cursor = sqlite_connection.cursor()
    search_cursor.execute(sql_search_expression)
    #output_temp_file(search_cursor)
    results_list = []
    for row in search_cursor:
        formatted_row = [row[0], row[3], row[4], row[2]]
        results_list.append(formatted_row)
    return results_list

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

    sql_report_expression = sql_report_expression[:-4] + 'ORDER BY apartment'

    # if report_dict['check_in_time_start'] == '' and
    if not any(report_dict.values()):
        sql_report_expression = "SELECT * FROM package_log ORDER BY apartment; "
    report_cursor.execute(sql_report_expression)
    results_list = []
    for row in report_cursor:
        formatted_row = [row[3], row[0], row[1], row[2], status_dict[row[5]]]
        results_list.append(formatted_row)
    return results_list


def count_received_by_apartment_date_range(count_dict):
    if count_dict['apartment'] == '':
        sql_count_expression = f'''SELECT apartment
        , COUNT(*) AS Total
        , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
        , COUNT(package_status) FILTER (WHERE package_status = 1) AS Delivered
        , COUNT(package_status) FILTER (WHERE package_status = 2) AS Missing
        , COUNT(package_status) FILTER (WHERE package_status = 3) AS Mistake
        FROM package_log WHERE date(check_in_time) BETWEEN '{count_dict['check_in_time_start']}' AND '{count_dict['check_in_time_end']}' GROUP BY apartment ORDER BY apartment; '''
    else:
        sql_count_expression = f'''SELECT apartment
        , COUNT(*) AS Total
        , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
        , COUNT(package_status) FILTER (WHERE package_status = 1) AS Delivered
        , COUNT(package_status) FILTER (WHERE package_status = 2) AS Missing
        , COUNT(package_status) FILTER (WHERE package_status = 3) AS Mistake
        FROM package_log WHERE apartment IS '{count_dict['apartment']}' AND date(check_in_time) BETWEEN '{count_dict['check_in_time_start']}' AND '{count_dict['check_in_time_end']}' GROUP BY apartment ORDER BY apartment; '''
    function_cursor = sqlite_connection.cursor()
    function_cursor.execute(sql_count_expression)
    results_list = []

    for row in function_cursor:
        formatted_row = [row[0], row[2], row[3], row[4], row[5], row[1]]
        results_list.append(formatted_row)
    return results_list


def all_onhand_count(count_all_status):
    if count_all_status:
        sql_count_expression = f'''SELECT apartment
            , COUNT(*) AS Total
            , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
            , COUNT(package_status) FILTER (WHERE package_status = 1) AS Delivered
            , COUNT(package_status) FILTER (WHERE package_status = 2) AS Missing
            , COUNT(package_status) FILTER (WHERE package_status = 3) AS Mistake
            FROM package_log GROUP BY apartment ORDER BY apartment; '''
    else:
        sql_count_expression = f'''SELECT apartment
            , COUNT(*) AS Total
            , COUNT(package_status) FILTER (WHERE package_status = 0) AS Onhand
            FROM package_log GROUP BY apartment ORDER BY apartment; '''

    function_cursor = sqlite_connection.cursor()
    function_cursor.execute(sql_count_expression)
    #apt onhand delivered missing total
    results_list = []
    for row in function_cursor:
        if count_all_status:
            formatted_row = [row[0], row[2], row[3], row[4], row[5], row[1]]
        else:
            formatted_row = [row[0], row[2], '', '', '', row[1]]
        results_list.append(formatted_row)
    return results_list


def save_report(headers, data, file_name):
    start_file_name = f'"{file_name}"'
    with open(file_name, 'w', newline='') as out_csv_file:
        csv_out = csv.writer(out_csv_file)
        csv_out.writerow(headers)
        for row in data:
            csv_out.writerow(row)
    subprocess.Popen(start_file_name, shell=True)
