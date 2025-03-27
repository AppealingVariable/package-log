import FreeSimpleGUI as sg
import packagelog
import os
import PackageLogTabs

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
    tab2_layout = [[sg.T('This is inside tab 2')],
                   [sg.In(key='in')]]
    check_in_obj = PackageLogTabs.CheckIn()
    check_out_obj = PackageLogTabs.CheckOut()
    onhand_search_obj = PackageLogTabs.OnHandSearch()
    counts_by_date_obj = PackageLogTabs.CountsByDate()
    mark_mistake_obj = PackageLogTabs.MarkMistakeMissing()
    layout = [[sg.TabGroup(layout=[[sg.Tab(title=check_in_obj.tab_title, layout=check_in_obj.layout, key=check_in_obj.tab_key)],
                                   [sg.Tab(title=check_out_obj.tab_title, layout=check_out_obj.layout, key=check_out_obj.tab_key)],
                                   [sg.Tab(title=onhand_search_obj.tab_title, layout=onhand_search_obj.layout, key=onhand_search_obj.tab_key)],
                                   [sg.Tab(title=counts_by_date_obj.tab_title, layout=counts_by_date_obj.layout, key=counts_by_date_obj.tab_key)],
                                   [sg.Tab(title=mark_mistake_obj.tab_title, layout=mark_mistake_obj.layout, key=mark_mistake_obj.tab_key)]],
                           key="tab",
                           enable_events=True)],
          [sg.Button('Read')]]

    #layout = [[sg.Button('Manual Check In'), sg.Button('Manual Check Out'), sg.Button('On Hand Search'), sg.Button('Manual Reports'), sg.Button('Counts by Check in Date'), sg.Button('All Counts'), sg.Button('Mark As Mistake or Missing'), sg.Exit() ]]
    window = sg.Window('Package Log Main Menu', layout, use_ttk_buttons=True, resizable=True).Finalize()
    window.Maximize()
    #set_return_bind_tab(window, current_tab + 'return_bind')

    current_return_bind = window['tab'].find_currently_active_tab_key() + 'return_bind'
    #current_focus = window['tab'].find_currently_active_tab_key().focus
    window.write_event_value('tab', check_in_obj.tab_key)
    #print(current_focus)
    while True:                             # The Event Loop
        event, values = window.read()
        print(event, values)
        #change tab event
        if event == 'tab':
            current_return_bind = bind_return_set_focus(window, current_return_bind, window['tab'].find_currently_active_tab_key())

        #matches all events for check in
        if event.startswith(check_in_obj.tab_key):
            check_in_obj.check_in_gui(window=window, event=event, filtered_values=PackageLogTabs.filter_read_dict(values))

        # matches all events for check out
        if event.startswith(check_out_obj.tab_key):
            check_out_obj.check_out_gui(window=window, event=event, filtered_values=PackageLogTabs.filter_read_dict(values))

        # matches all events for onhand search
        if event.startswith(onhand_search_obj.tab_key):
            onhand_search_obj.on_hand_search_gui(window=window, event=event, filtered_values=PackageLogTabs.filter_read_dict(values))

        # matches all events for counts by date
        if event.startswith(counts_by_date_obj.tab_key):
            counts_by_date_obj.counts_by_date_gui(window=window, event=event, filtered_values=PackageLogTabs.filter_read_dict(values))

        # matches all events for mark mistake or missing
        if event.startswith(mark_mistake_obj.tab_key):
            mark_mistake_obj.mark_as_error_gui(window=window, event=event, filtered_values=PackageLogTabs.filter_read_dict(values))

        if event == 'Manual Reports':
            manual_reports_gui()

        if event == 'All Counts':
            count_all_gui()
        if event == 'Mark As Mistake or Missing':
            mark_as_error_gui()
        if event == sg.WIN_CLOSED or event == 'Exit':
            packagelog.db_close()
            break
    window.close()


def bind_return_set_focus(window, current_return_bind, tab_bind):
    window[current_return_bind].unbind("<Return>")
    window.bind("<Return>", tab_bind + 'return_bind')
    window[tab_bind + 'return_bind'].bind("<Return>", '')
    window[tab_bind + 'apartment'].set_focus()
    return tab_bind + 'return_bind'



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



# def check_in_gui():
#     layout = [[sg.Text('Package Check In')],
#               [sg.Text('Carrier')],
#               [sg.Radio('Amazon', 'group 1')],
#               [sg.Radio('FedEx', 'group 1')],
#               [sg.Radio('US Postal', 'group 1')],
#               [sg.Radio('DHL', 'group 1')],
#               [sg.Radio('UPS', 'group 1')],
#               [sg.Radio('Other', 'group 1'),],
#               [sg.Text('Apartment Number'), sg.Input(key='apartment')],
#               [sg.Text('Barcode'), sg.Input(key='barcode', do_not_clear=False)],
#               [sg.Button('Check In', bind_return_key = True), sg.Exit()]]
#
#     window = sg.Window('Package Check In', layout, use_ttk_buttons=True, modal=True)
#
#     while True:                             # The Event Loop
#         event, values = window.read()
#
#         if event == 'Check In':
#             carrier_value = ''
#             for key in values:
#                 if values[key] == True:
#                     carrier_value = carriers_dict[key]
#
#             if values['apartment'] != '' and carrier_value != '' and values['barcode'] != '':
#                 package_info = dict(apartment = values['apartment'], delivered_by = carrier_value, barcode_scan = values['barcode'], package_status = 0)
#                 if packagelog.check_in(package_info):
#                     sg.popup_quick_message(f"Packaged added for apartment {package_info['apartment']}", background_color = "white", text_color = 'black')
#             else:
#                 sg.popup('Please enter information in all fields and try again')
#
#         if event == sg.WIN_CLOSED or event == 'Exit':
#             break
#
#     window.close()

# def check_out_gui():
#     layout = [[sg.Text('Package Check Out')],
#               [sg.Text('Barcode'), sg.Input(key='barcode')],
#               [sg.Button('Check Out'), sg.Exit()]]
#
#     window = sg.Window('Package Check Out', layout, use_ttk_buttons=True, modal=True)
#
#
#     while True:                             # The Event Loop
#         event, values = window.read()
#         if event == 'Check Out':
#             packagelog.check_out_barcode(values['barcode'])
#         if event == sg.WIN_CLOSED or event == 'Exit':
#             break
#
#     window.close()


main_menu()