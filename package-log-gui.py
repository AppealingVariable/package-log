import FreeSimpleGUI as sg
import packagelog

carriers_dict = {0: 'Amazon',
                 1: 'Fedex',
                 2: 'US Postal',
                 3: 'DHL',
                 4: 'UPS',
                 5: 'Other'
                 }

def main_menu():
    packagelog.db_connect()

    layout = [[sg.Button('Check In'), sg.Button('Check Out'), sg.Button('Search'), sg.Button('Manual Reports'), sg.Button('Counts by Apartment'), sg.Button('All Onhand Counts'),sg.Exit() ]]
    window = sg.Window('Package Log Main Menu', layout, use_ttk_buttons=True, resizable=True).Finalize()
    window.Maximize()
    while True:                             # The Event Loop
        event, values = window.read()
        if event == 'Check In':
            check_in_gui()
        if event == 'Check Out':
            check_out_gui()
        if event == 'Search':
            search_gui()
        if event == 'Manual Reports':
            manual_reports_gui()
        if event == 'Counts by Apartment':
            counts_by_apartment_date_range_gui()
        if event == 'All Onhand Counts':
            packagelog.all_onhand_count()
        if event == sg.WIN_CLOSED or event == 'Exit':
            packagelog.db_close()
            break

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
              [sg.Text('Barcode'), sg.Input(key='barcode')],
              [sg.Button('Check In'), sg.Exit()]]

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
                packagelog.check_in(package_info)
            else:
                pass

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
            packagelog.check_out(values['barcode'])
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def search_gui():
    combo_dict_conversion = {'Checked In': 0,
                             'Checked Out': 1,
                             'Missing': 2,
                             'All': ''}
    layout = [[sg.Text('Package Search')],
              [sg.Text('Carrier')],
              [sg.Radio('Amazon', 'group 1')],
              [sg.Radio('FedEx', 'group 1')],
              [sg.Radio('US Postal', 'group 1')],
              [sg.Radio('DHL', 'group 1')],
              [sg.Radio('UPS', 'group 1')],
              [sg.Radio('Other', 'group 1'),],
              [sg.Text('Apartment Number'), sg.Input(key='apartment')],
              [sg.Text('Barcode'), sg.Input(key='barcode_scan')],
              [sg.CalendarButton(button_text='Check In Date',format = "%Y-%m-%d", key='date_dummy'),sg.Input(key='check_in_time')],
              [sg.CalendarButton(button_text='Check Out Date', format="%Y-%m-%d", key='date_dummy'), sg.Input(key='check_out_time')],
              [sg.Combo(['Checked In', 'Checked Out', 'Missing', 'All'], default_value='All', readonly=True, key='status')],
              [sg.Button('Search'), sg.Exit()]]

    window = sg.Window('Package Search', layout, use_ttk_buttons=True, modal=True)

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Search':
            carrier_value = ''
            for key in values:
                if values[key] == True:
                    carrier_value = carriers_dict[key]
            package_info = dict(check_in_time= values['check_in_time'], check_out_time= values['check_out_time'], apartment = values['apartment'], delivered_by = carrier_value, barcode_scan = values['barcode_scan'], package_status = combo_dict_conversion[values['status']])
            packagelog.db_search(package_info)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()


def manual_reports_gui():
    combo_dict_conversion = {'Checked In': 0,
                             'Checked Out': 1,
                             'Missing': 2,
                             'All': ''}
    layout = [[sg.Text('Manual Reports')],
              [sg.Text('Carrier')],
              [sg.Radio('Amazon', 'group 1')],
              [sg.Radio('FedEx', 'group 1')],
              [sg.Radio('US Postal', 'group 1')],
              [sg.Radio('DHL', 'group 1')],
              [sg.Radio('UPS', 'group 1')],
              [sg.Radio('Other', 'group 1'), ],
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
              [sg.Combo(['Checked In', 'Checked Out', 'Missing', 'All'], default_value='All', readonly=True,
                        key='status')],
              [sg.Button('Generate Report'), sg.Exit()]]

    window = sg.Window('Manual Reports', layout, use_ttk_buttons=True, modal=True)

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Generate Report':
            carrier_value = ''
            for key in values:
                if values[key] == True:
                    carrier_value = carriers_dict[key]
            package_info = dict(check_in_time_start=values['check_in_time_start'],
                                check_in_time_end=values['check_in_time_end'],
                                check_out_time_start=values['check_out_time_start'],
                                check_out_time_end=values['check_out_time_end'],
                                apartment=values['apartment'],
                                delivered_by=carrier_value,
                                barcode_scan=values['barcode_scan'],
                                package_status=combo_dict_conversion[values['status']])
            packagelog.db_manual_report(package_info)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def counts_by_apartment_date_range_gui():

    layout = [[sg.Text('Manual Reports')],
              [sg.CalendarButton(button_text='Check In Date Start', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_start')],
              [sg.CalendarButton(button_text='Check In Date End', format="%Y-%m-%d", key='date_dummy'),
               sg.Input(key='check_in_time_end')],
              [sg.Button('Generate Report'), sg.Exit()]]

    window = sg.Window('Package Check Out', layout, use_ttk_buttons=True, modal=True)

    while True:  # The Event Loop
        event, values = window.read()

        if event == 'Generate Report':
            package_info = dict(check_in_time_start=values['check_in_time_start'],
                                check_in_time_end=values['check_in_time_end'])
            packagelog.count_received_by_apartment_date_range(package_info)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()


main_menu()