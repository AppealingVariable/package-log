import FreeSimpleGUI as sg
import packagelog
import os

def return_carrier_value(values):
    pass

def get_tab_name():
    pass

def error_message(message):
    error_font_settings = ('arial', 25, 'bold')
    layout=[[sg.Text(text=f"{message}", background_color='pink', text_color='black', font=error_font_settings)],
            [sg.Button("OK")]]
    sg.Window(title="Error", layout=layout, use_ttk_buttons=True, modal=True, keep_on_top=True, disable_close=True,background_color='pink').read(close=True)

def filter_read_dict(values):
    input_values = values
    tab = input_values.pop('tab')
    filtered_dict = {str(key).removeprefix(tab): val for key, val in input_values.items()
                     if str(key).startswith(tab)}
    return filtered_dict

class CheckIn:
    def __init__(self):
        self.tab_key = 'check_in_tab'
        self.tab_title = 'Check In'
        self.focus = self.tab_key + 'apartment'
        self.return_bind = self.tab_key + 'return_bind'
        self.layout = [[sg.Text('Check In')],
                   [sg.Text('Carrier')],
                   [sg.Radio(text='Amazon', group_id=self.tab_key + 'radio', key=self.tab_key + 'Amazon')],
                   [sg.Radio(text='FedEx', group_id=self.tab_key + 'radio', key=self.tab_key + 'FedEx')],
                   [sg.Radio(text='US Postal', group_id=self.tab_key + 'radio', key=self.tab_key + 'US Postal')],
                   [sg.Radio(text='DHL', group_id=self.tab_key + 'radio', key=self.tab_key + 'DHL')],
                   [sg.Radio(text='UPS', group_id=self.tab_key + 'radio', key=self.tab_key + 'UPS')],
                   [sg.Radio(text='Other', group_id=self.tab_key + 'radio', key=self.tab_key + 'Other', default=True), ],
                   [sg.Text('Apartment Number'), sg.Input(key=self.tab_key + 'apartment', focus=True)],
                   [sg.Text('Number of Packages'), sg.Input(key=self.tab_key + 'package_count', default_text='1')],
                   [sg.Button(button_text='Check In', key=self.tab_key + 'return_bind'), sg.Exit()]]



    def check_in_gui(self, window, event, filtered_values):

        window[self.tab_key + 'apartment'].set_focus()

        if event == self.tab_key + 'return_bind': #check in
            carrier_value = ''
            for key in filtered_values:
                if filtered_values[key] == True:
                    carrier_value = key
                    print(carrier_value)
            filtered_values['barcode'] = 'MANUAL'
            if filtered_values['apartment'] != '' and carrier_value != '':
                package_info = dict(apartment=filtered_values['apartment'].upper(), delivered_by=carrier_value,
                                    barcode_scan=filtered_values['barcode'], package_status=0,
                                    package_count=filtered_values['package_count'])

                if packagelog.check_in(package_info):
                    if int(filtered_values['package_count']) == 1:
                        sg.popup_quick_message(
                            f"{filtered_values['package_count']} package added for apartment {package_info['apartment']}",
                            background_color="white", text_color='black')
                    else:
                        sg.popup_quick_message(
                            f"{filtered_values['package_count']} packages added for apartment {package_info['apartment']}",
                            background_color="white", text_color='black')
                    window[self.tab_key + 'apartment'].update(value='')
                    window[self.tab_key + 'package_count'].update(value=1)
                    window[self.tab_key + 'apartment'].set_focus()

                else:
                    error_message("Error: Package Not Saved. Please verify information and try again.")
            else:
                sg.popup('Please enter information in all fields and try again')

class CheckOut:
    def __init__(self):
        self.tab_key = 'check_out_tab'
        self.tab_title = 'Check Out'
        self.data = []
        self.headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
        self.layout = [[sg.Text('Check Out')],
                       [sg.Button(button_text='Select All', key=self.tab_key + 'Select All'),
                        sg.Button(button_text='Load list', key=self.tab_key + 'return_bind'),
                        sg.Text('Apartment'), sg.Input(key=self.tab_key +'apartment')],
                       [sg.Table(values=self.data,
                                 headings=self.headings,
                                 def_col_width=30,
                                 max_col_width=50,
                                 background_color='darkblue',
                                 auto_size_columns=False,
                                 display_row_numbers=False,
                                 num_rows=20,
                                 key=self.tab_key + 'table')],
                  [sg.Button(button_text='Check Out', key=self.tab_key + 'Check Out')]
                  ]


    def check_out_gui(self, window, event, filtered_values):

        #window[self.tab_key + 'apartment'].set_focus()

        if event == self.tab_key + 'return_bind':       #load list
            if filtered_values['apartment'] != '':
                self.data = packagelog.db_search_on_hand(filtered_values)
                window[self.tab_key + 'table'].update(values=self.data)
        if event == self.tab_key + 'Select All':
            selected_rows = []
            for i in range(len(self.data)):
                selected_rows.append(i)
            if selected_rows != []:
                window[self.tab_key + 'table'].update(select_rows=selected_rows)

        if event == self.tab_key + 'Check Out':
            row_count = 0
            error_count = 0
            if filtered_values['table'] != []:
                for row in filtered_values['table']:
                    if not packagelog.check_out_manual(self.data[row]):
                        error_message(
                            f"Package {self.data[row]} did not check out correctly. Please try again and report to IT if the error persists.")
                        error_count += 1
                    row_count += 1
                package_plural = 'packages'
                checked_out_count = row_count - error_count
                if checked_out_count == 1:
                    package_plural = 'package'
                sg.popup_quick_message(f"{checked_out_count} {package_plural} checked out for apartment {self.data[0][1]}",
                                       background_color="white", text_color='black')
                self.data = packagelog.db_search_on_hand(filtered_values)
                window[self.tab_key + 'table'].update(values=self.data)


class OnHandSearch:
    def __init__(self):
        self.tab_key = 'on_hand_search'
        self.tab_title = 'On Hand Search'
        self.data = []
        self.headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
        self.layout = [[sg.Text('Search by apartment')],
                  [sg.Button(button_text='Load list', key=self.tab_key + 'return_bind'), sg.Text('Apartment'), sg.Input(key=self.tab_key +'apartment')],
                  [sg.Table(values=self.data, headings=self.headings, def_col_width=30, max_col_width=50,
                            background_color='darkblue',
                            auto_size_columns=False,
                            display_row_numbers=False,
                            num_rows=20,
                            key=self.tab_key + 'table')],
                  [sg.Text('Total'), sg.Text('0', key=self.tab_key + 'total_value')]
                  ]

    def on_hand_search_gui(self, window, event, filtered_values):

        if event == self.tab_key + 'return_bind':
            self.data = packagelog.db_search_on_hand(filtered_values)
            window[self.tab_key + 'table'].update(values=self.data)
            window[self.tab_key + 'total_value'].update(value=len(self.data))



class CountsByDate:
    def __init__(self):
        self.tab_key = 'counts_by_date'
        self.tab_title = 'Counts by Date'
        self.data = []
        self.headings = ['Apartment', 'Onhand', 'Delivered', 'Missing', 'Mistake', 'Total']
        self.layout = [[sg.Text('Counts by apartment, leave apartment blank to view all')],
                  [sg.CalendarButton(button_text='Check In Date Start', format="%Y-%m-%d", key='date_dummy'),
                   sg.Input(key=self.tab_key + 'check_in_time_start', default_text=packagelog.today_date_string())],
                  [sg.CalendarButton(button_text='Check In Date End', format="%Y-%m-%d", key='date_dummy'),
                   sg.Input(key=self.tab_key + 'check_in_time_end', default_text=packagelog.today_date_string())],
                  [sg.Text('Apartment Number'), sg.Input(key=self.tab_key + 'apartment')],
                  [sg.Button(button_text='Load List', key=self.tab_key + 'return_bind', bind_return_key=True)],
                  [sg.Table(values=self.data, headings=self.headings, def_col_width=30, max_col_width=50,
                            background_color='darkblue',
                            auto_size_columns=False,
                            display_row_numbers=False,
                            justification="left",
                            num_rows=20,
                            key=self.tab_key + 'table')],
                  [sg.Button(button_text='Save Report', key=self.tab_key + 'Save Report')]
                  ]

    def counts_by_date_gui(self, window, event, filtered_values):
        if event == self.tab_key + 'return_bind':
            if filtered_values['check_in_time_start'] == '' or filtered_values['check_in_time_end'] == '':
                sg.popup('Please choose date range')
            else:
                package_info = dict(check_in_time_start=filtered_values['check_in_time_start'],
                                    check_in_time_end=filtered_values['check_in_time_end'],
                                    apartment=filtered_values['apartment'].upper())
                self.data = packagelog.count_received_by_apartment_date_range(package_info)
                window[self.tab_key + 'table'].update(values=self.data)

        if event == self.tab_key + 'Save Report':
            write_file_headers = self.headings[:]
            write_file_headers.extend(
                [f"Start {filtered_values['check_in_time_start']}", f"End {filtered_values['check_in_time_end']}"])

            save_file_name = sg.popup_get_file(message="Choose where to save report",
                                               default_path=f'Report {packagelog.time_string()}',
                                               no_window=True,
                                               save_as=True,
                                               file_types=(('*.csv', "ALL Files"),),
                                               initial_folder=os.path.expanduser('~/Documents/'),
                                               default_extension='.csv'
                                               )

            if save_file_name is not None and save_file_name != '':
                packagelog.save_report(headers=write_file_headers, data=self.data, file_name=save_file_name)
                sg.popup_quick_message("File Saved", background_color="white", text_color='black')

class MarkMistakeMissing:
    def __init__(self):
        self.tab_key = 'mistake_missing'
        self.tab_title = 'Mark As Mistake'
        self.data = []
        self.headings = ['Check in time', 'Apartment', 'Barcode', 'Carrier']
        self.layout = [[sg.Text('Mark As Mistake')],
                  [sg.Button(button_text='Load list', key=self.tab_key + 'return_bind', bind_return_key=True), sg.Text('Apartment'), sg.Input(key=self.tab_key + 'apartment')],
                  [sg.Table(values=self.data, headings=self.headings, def_col_width=30, max_col_width=50,
                            background_color='darkblue',
                            auto_size_columns=False,
                            display_row_numbers=False,
                            num_rows=20,
                            key=self.tab_key + 'table')],
                  [sg.Button(button_text='Mark As Mistake', key=self.tab_key + 'Mark As Mistake'), sg.Button(button_text='Mark As Missing', key=self.tab_key + 'Mark As Missing')]
                  ]

    def mark_as_error_gui(self, window, event, filtered_values):
        if event == self.tab_key + 'return_bind':
            data = packagelog.db_search_on_hand(filtered_values)
            window[self.tab_key + 'table'].update(values=data)
        if event == self.tab_key + 'Mark As Mistake' or event == self.tab_key + 'Mark As Missing':
            row_count = 0
            error_count = 0
            if event == 'Mark As Missing':
                status_change = 2
            else:
                status_change = 3
            print(len(filtered_values['table']))
            for row in filtered_values['table']:
                print(row)
                if not packagelog.mark_as_error(package_info=self.data[row], status_update=status_change):
                    error_message(
                        f"Package {self.data[row]} status not updated. Please try again and report to IT if the error persists.")
                    error_count += 1
                row_count += 1
            package_plural = 'packages'
            checked_out_count = row_count - error_count
            if checked_out_count == 1:
                package_plural = 'package'
            sg.popup_quick_message(
                f"{checked_out_count} {package_plural} marked {packagelog.status_dict[status_change]} for apartment {data[0][1]}",
                background_color="white", text_color='black')
            data = packagelog.db_search_on_hand(filtered_values)
            window['-TABLE-'].update(values=data)


