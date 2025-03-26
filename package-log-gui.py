import FreeSimpleGUI as sg
import packagelog
import os

carriers_dict = {0: 'Amazon',
                 1: 'Fedex',
                 2: 'US Postal',
                 3: 'DHL',
                 4: 'UPS',
                 5: 'Other',
                 6: ''
                 }

def main_menu():
    packagelog.db_connect()

    layout = [[sg.Button('Manual Check In'), sg.Button('Manual Check Out'), sg.Button('On Hand Search'), sg.Button('Manual Reports'), sg.Button('Counts by Check in Date'), sg.Button('All Counts'), sg.Button('Mark As Mistake or Missing'), sg.Exit() ]]
    window = sg.Window('Package Log Main Menu', layout, use_ttk_buttons=True, resizable=True).Finalize()
    window.Maximize()
    while True:                             # The Event Loop
        event, values = window.read()
        # if event == 'Check In':
        #     check_in_gui()
        # if event == 'Check Out':
        #     check_out_gui()
        if event == 'Manual Check In':
            manual_check_in_gui()
        if event == 'Manual Check Out':
            manual_check_out_gui()
        if event == 'On Hand Search':
            on_hand_search_gui()
        if event == 'Manual Reports':
            manual_reports_gui()
        if event == 'Counts by Check in Date':
            counts_by_apartment_date_range_gui()
        if event == 'All Counts':
            count_all_gui()
        if event == 'Mark As Mistake or Missing':
            mark_as_error_gui()
        if event == sg.WIN_CLOSED or event == 'Exit':
            packagelog.db_close()
            break
    window.close()

def error_message(message):
    error_font_settings = ('arial', 25, 'bold')
    layout=[[sg.Text(text=f"{message}", background_color='pink', text_color='black', font=error_font_settings)],
            [sg.Button("OK")]]
    sg.Window(title="Error", layout=layout, use_ttk_buttons=True, modal=True, keep_on_top=True, disable_close=True,background_color='pink').read(close=True)

def manual_check_in_gui():
    layout = [[sg.Text('Manual Check In')],
              [sg.Text('Carrier')],
              [sg.Radio('Amazon', 'group 1')],
              [sg.Radio('FedEx', 'group 1')],
              [sg.Radio('US Postal', 'group 1')],
              [sg.Radio('DHL', 'group 1')],
              [sg.Radio('UPS', 'group 1')],
              [sg.Radio('Other', 'group 1', default=True),],
              [sg.Text('Apartment Number'), sg.Input(key='apartment', focus=True)],
              [sg.Text('Number of Packages'), sg.Input(key='package_count', default_text='1')],
              [sg.Button('Check In', bind_return_key = True), sg.Exit()]]

    window = sg.Window('Package Check In', layout, use_ttk_buttons=True, modal=True).Finalize()
    window['apartment'].set_focus()

    while True:                             # The Event Loop
        event, values = window.read()

        if event == 'Check In':
            carrier_value = ''
            for key in values:
                if values[key] == True:
                    carrier_value = carriers_dict[key]
            values['barcode'] = 'MANUAL'
            if values['apartment'] != '' and carrier_value != '':
                package_info = dict(apartment = values['apartment'].upper(), delivered_by = carrier_value, barcode_scan = values['barcode'], package_status = 0, package_count=values['package_count'])

                if packagelog.check_in(package_info):
                    if int(values['package_count']) == 1:
                        sg.popup_quick_message(f"{values['package_count']} package added for apartment {package_info['apartment']}", background_color = "white", text_color = 'black')
                    else:
                        sg.popup_quick_message(
                            f"{values['package_count']} packages added for apartment {package_info['apartment']}",
                            background_color="white", text_color='black')
                    window['apartment'].update(value='')
                    window['package_count'].update(value=1)
                    window['apartment'].set_focus()

                else:
                    error_message("Error: Package Not Saved. Please verify information and try again.")
            else:
                sg.popup('Please enter information in all fields and try again')

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def manual_check_out_gui():
    data = []
    headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
    layout = [[sg.Text('Manual Check Out')],
              [sg.Button('Select All'), sg.Button('Load list', bind_return_key = True), sg.Text('Apartment'), sg.Input(key='apartment')],
              [sg.Table(values=data, headings=headings, def_col_width=30, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Button('Manual Check Out')]
              ]
    window = sg.Window('Manual Check Out', layout, use_ttk_buttons=True, modal=True).Finalize()
    window['apartment'].set_focus()

    while True:                             # The Event Loop
        event, values = window.read()
        if event == 'Load list':
            if values['apartment'] != '':
                data = packagelog.db_search_on_hand(values)
                window['-TABLE-'].update(values=data)
        if event == 'Select All':
            selected_rows = []
            for i in range(len(data)):
                selected_rows.append(i)
            if selected_rows != []:
                window['-TABLE-'].update(select_rows=selected_rows)

        if event == 'Manual Check Out':
            row_count = 0
            error_count = 0
            for row in values['-TABLE-']:
                if not packagelog.check_out_manual(data[row]):
                    error_message(f"Package {data[row]} did not check out correctly. Please try again and report to IT if the error persists.")
                    error_count += 1
                row_count += 1
            package_plural = 'packages'
            checked_out_count = row_count - error_count
            if checked_out_count == 1:
                package_plural = 'package'
            sg.popup_quick_message(f"{checked_out_count} {package_plural} checked out for apartment {data[0][1]}",
                                   background_color="white", text_color='black')
            data = packagelog.db_search_on_hand(values)
            window['-TABLE-'].update(values=data)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()


def mark_as_error_gui():
    data = []
    headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
    layout = [[sg.Text('Mark As Mistake')],
              [sg.Button('Load list', bind_return_key = True), sg.Text('Apartment'), sg.Input(key='apartment')],
              [sg.Table(values=data, headings=headings, def_col_width=30, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Button('Mark As Mistake'), sg.Button('Mark As Missing')]
              ]
    window = sg.Window('Mark As Mistake', layout, use_ttk_buttons=True, modal=True).Finalize()
    window['apartment'].set_focus()

    while True:                             # The Event Loop
        event, values = window.read()
        if event == 'Load list':
            data = packagelog.db_search_on_hand(values)
            window['-TABLE-'].update(values=data)
        print(event)
        if event == 'Mark As Mistake' or event == 'Mark As Missing':
            row_count = 0
            error_count = 0
            if event == 'Mark As Missing':
                status_change = 2
            else:
                status_change = 3
            for row in values['-TABLE-']:
                if not packagelog.mark_as_error(package_info=data[row], status_update=status_change):
                    error_message(f"Package {data[row]} status not updated. Please try again and report to IT if the error persists.")
                    error_count += 1
                row_count += 1
            package_plural = 'packages'
            checked_out_count = row_count - error_count
            if checked_out_count == 1:
                package_plural = 'package'
            sg.popup_quick_message(f"{checked_out_count} {package_plural} marked {packagelog.status_dict[status_change]} for apartment {data[0][1]}",
                                   background_color="white", text_color='black')
            data = packagelog.db_search_on_hand(values)
            window['-TABLE-'].update(values=data)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()

def on_hand_search_gui():
    data = []
    #total = 0
    headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
    layout = [[sg.Text('Search by apartment')],
              [sg.Button('Load list', bind_return_key = True), sg.Text('Apartment'), sg.Input(key='apartment')],
              [sg.Table(values=data, headings=headings, def_col_width=30, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Text('Total'), sg.Text('0', key='total_value')]
              ]
    window = sg.Window('Search', layout, use_ttk_buttons=True, modal=True).Finalize()
    window['apartment'].set_focus()

    while True:                             # The Event Loop
        event, values = window.read()
        if event == 'Load list':
            data = packagelog.db_search_on_hand(values)
            window['-TABLE-'].update(values=data)
            window['total_value'].update(value=len(data))
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()

def manual_reports_gui():
    combo_dict_conversion = {'Checked In': 0,
                             'Checked Out': 1,
                             'Missing': 2,
                             'Mistake': 3,
                             'All': ''}
    data = []
    headings = ['Apartment', 'Check In Time', 'Check Out Time', 'Carrier', 'Status']
    layout = [[sg.Text('Manual Reports')],
              [sg.Text('Carrier')],
              [sg.Radio('Amazon', 'group 1')],
              [sg.Radio('FedEx', 'group 1')],
              [sg.Radio('US Postal', 'group 1')],
              [sg.Radio('DHL', 'group 1')],
              [sg.Radio('UPS', 'group 1')],
              [sg.Radio('Other', 'group 1')],
              [sg.Radio('All', 'group 1', default=True)],
              [sg.Text('Apartment Number'), sg.Input(key='apartment')],
              [sg.Text('Barcode'), sg.Input(key='barcode_scan')],
              [sg.CalendarButton(button_text='Check In Date Start', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_start')],
              [sg.CalendarButton(button_text='Check In Date End', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_end')],
              [sg.CalendarButton(button_text='Check Out Date Start', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_out_time_start')],
              [sg.CalendarButton(button_text='Check Out Date End', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_out_time_end')],
              [sg.Text('Package Status'), sg.Combo(['Checked In', 'Checked Out', 'Missing', 'Mistake', 'All'], default_value='All', readonly=True,
                        key='status')],
              [sg.Button('Load list', bind_return_key = True)],
              [sg.Table(values=data, headings=headings, def_col_width = 20, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        justification="left",
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Text('Total'), sg.Text('0', key='total_value')],
              [sg.Button('Save Report'), sg.Exit()]]


    window = sg.Window('Manual Reports', layout, use_ttk_buttons=True, modal=True)

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Save Report':
            save_file_name = sg.popup_get_file(message="Choose where to save report",
                                          default_path=f'Report {packagelog.time_string()}',
                                          no_window=True,
                                          save_as = True,
                                          file_types = (('*.csv',"ALL Files"),),
                                          initial_folder=os.path.expanduser('~/Documents/'),
                                          default_extension='.csv'
                                          )

            if save_file_name is not None and save_file_name != '':
                packagelog.save_report(headers=headings, data=data, file_name=save_file_name)
                sg.popup_quick_message("File Saved", background_color = "white", text_color = 'black')

        if event == 'Load list':
            carrier_value = ''
            for key in values:
                if values[key] == True:
                    carrier_value = carriers_dict[key]
            package_info = dict(check_in_time_start=values['check_in_time_start'],
                                check_in_time_end=values['check_in_time_end'],
                                check_out_time_start=values['check_out_time_start'],
                                check_out_time_end=values['check_out_time_end'],
                                apartment=values['apartment'].upper(),
                                delivered_by=carrier_value,
                                barcode_scan=values['barcode_scan'],
                                package_status=combo_dict_conversion[values['status']])
            data = packagelog.db_manual_report(package_info)
            window['-TABLE-'].update(values=data)
            window['total_value'].update(value=len(data))
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def counts_by_apartment_date_range_gui():
    counts_header = ['Apartment', 'Onhand', 'Delivered', 'Missing', 'Mistake', 'Total']
    data = []
    layout = [[sg.Text('Counts by apartment, leave apartment blank to view all')],
              [sg.CalendarButton(button_text='Check In Date Start', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_start', default_text=packagelog.today_date_string())],
              [sg.CalendarButton(button_text='Check In Date End', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_end', default_text=packagelog.today_date_string())],
              [sg.Text('Apartment Number'), sg.Input(key='apartment')],
              [sg.Button('Load List', bind_return_key = True)],
              [sg.Table(values=data, headings=counts_header, def_col_width=30, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        justification="left",
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Button('Save Report'), sg.Exit()]
              ]

    window = sg.Window('Counts by Check in Date', layout, use_ttk_buttons=True, modal=True).Finalize()
    window['apartment'].set_focus()

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Load List':
            if values['check_in_time_start'] == '' or values['check_in_time_end'] == '':
                sg.popup('Please choose date range')
            else:
                package_info = dict(check_in_time_start=values['check_in_time_start'],
                                    check_in_time_end=values['check_in_time_end'],
                                    apartment=values['apartment'].upper())
                data = packagelog.count_received_by_apartment_date_range(package_info)
                window['-TABLE-'].update(values=data)

        if event == 'Save Report':
            save_file_name = sg.popup_get_file(message="Choose where to save report",
                                          default_path=f'Report {packagelog.time_string()}',
                                          no_window=True,
                                          save_as = True,
                                          file_types = (('*.csv',"ALL Files"),),
                                          initial_folder=os.path.expanduser('~/Documents/'),
                                          default_extension='.csv'
                                          )
            write_file_headers = counts_header
            write_file_headers.extend([f"Start {values['check_in_time_start']}", f"End {values['check_in_time_end']}"])

            if save_file_name is not None and save_file_name != '':
                packagelog.save_report(headers=write_file_headers, data=data, file_name=save_file_name)
                sg.popup_quick_message("File Saved", background_color = "white", text_color = 'black')
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()

def count_all_gui():
    counts_header = ['Apartment', 'Onhand', 'Delivered', 'Missing', 'Mistake', 'Total']
    data = []
    layout = [[sg.Text("Shows current counts of all records")],
              [sg.Button('Load Onhand Counts'), sg.Button('Load All Counts')],
              [sg.Table(values=data, headings=counts_header, def_col_width=30, max_col_width=50, background_color='darkblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        justification="left",
                        num_rows=20,
                        key='-TABLE-')],
              [sg.Button('Save Report'), sg.Exit()]
              ]

    window = sg.Window('Counts by Package Status', layout, use_ttk_buttons=True, modal=True)

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Load Onhand Counts':
            data = packagelog.all_onhand_count(count_all_status=False)
            window['-TABLE-'].update(values=data)

        if event == 'Load All Counts':
            data = packagelog.all_onhand_count(count_all_status=True)
            window['-TABLE-'].update(values=data)

        if event == 'Load Missing Counts':
            pass

        if event == 'Load Delivered Counts':
            pass

        if event == 'Save Report':
            save_file_name = sg.popup_get_file(message="Choose where to save report",
                                          default_path=f'Report {packagelog.time_string()}',
                                          no_window=True,
                                          save_as = True,
                                          file_types = (('*.csv',"ALL Files"),),
                                          initial_folder=os.path.expanduser('~/Documents/'),
                                          default_extension='.csv'
                                          )
            write_file_headers = counts_header

            if save_file_name is not None and save_file_name != '':
                packagelog.save_report(headers=write_file_headers, data=data, file_name=save_file_name)
                sg.popup_quick_message("File Saved", background_color = "white", text_color = 'black')
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()



def check_in_gui():
    layout = [[sg.Text('Package Check In')],
              [sg.Text('Carrier')],
              [sg.Radio('Amazon', 'group 1')],
              [sg.Radio('FedEx', 'group 1')],
              [sg.Radio('US Postal', 'group 1')],
              [sg.Radio('DHL', 'group 1')],
              [sg.Radio('UPS', 'group 1')],
              [sg.Radio('Other', 'group 1'),],
              [sg.Text('Apartment Number'), sg.Input(key='apartment')],
              [sg.Text('Barcode'), sg.Input(key='barcode', do_not_clear=False)],
              [sg.Button('Check In', bind_return_key = True), sg.Exit()]]

    window = sg.Window('Package Check In', layout, use_ttk_buttons=True, modal=True)

    while True:                             # The Event Loop
        event, values = window.read()

        if event == 'Check In':
            carrier_value = ''
            for key in values:
                if values[key] == True:
                    carrier_value = carriers_dict[key]

            if values['apartment'] != '' and carrier_value != '' and values['barcode'] != '':
                package_info = dict(apartment = values['apartment'], delivered_by = carrier_value, barcode_scan = values['barcode'], package_status = 0)
                if packagelog.check_in(package_info):
                    sg.popup_quick_message(f"Packaged added for apartment {package_info['apartment']}", background_color = "white", text_color = 'black')
            else:
                sg.popup('Please enter information in all fields and try again')

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def check_out_gui():
    layout = [[sg.Text('Package Check Out')],
              [sg.Text('Barcode'), sg.Input(key='barcode')],
              [sg.Button('Check Out'), sg.Exit()]]

    window = sg.Window('Package Check Out', layout, use_ttk_buttons=True, modal=True)


    while True:                             # The Event Loop
        event, values = window.read()
        if event == 'Check Out':
            packagelog.check_out_barcode(values['barcode'])
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()


main_menu()