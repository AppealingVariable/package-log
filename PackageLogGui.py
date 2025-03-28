import FreeSimpleGUI as sg
import packagelog
import PackageLogTabs




def main_menu():
    packagelog.db_connect()
    tab2_layout = [[sg.T('This is inside tab 2')],
                   [sg.In(key='in')]]
    check_in_obj = PackageLogTabs.CheckIn()
    check_out_obj = PackageLogTabs.CheckOut()
    onhand_search_obj = PackageLogTabs.OnHandSearch()
    counts_by_date_obj = PackageLogTabs.CountsByDate()
    mark_mistake_obj = PackageLogTabs.MarkMistakeMissing()
    man_reports_obj = PackageLogTabs.ManualReports()
    count_all_obj = PackageLogTabs.AllCounts()

    layout = [[sg.TabGroup(layout=[[sg.Tab(title=check_in_obj.tab_title, layout=check_in_obj.layout, key=check_in_obj.tab_key)],
                                   [sg.Tab(title=check_out_obj.tab_title, layout=check_out_obj.layout, key=check_out_obj.tab_key)],
                                   [sg.Tab(title=onhand_search_obj.tab_title, layout=onhand_search_obj.layout, key=onhand_search_obj.tab_key)],
                                   [sg.Tab(title=counts_by_date_obj.tab_title, layout=counts_by_date_obj.layout, key=counts_by_date_obj.tab_key)],
                                   [sg.Tab(title=count_all_obj.tab_title, layout=count_all_obj.layout, key=count_all_obj.tab_key)],
                                   [sg.Tab(title=man_reports_obj.tab_title, layout=man_reports_obj.layout, key=man_reports_obj.tab_key)],
                                   [sg.Tab(title=mark_mistake_obj.tab_title, layout=mark_mistake_obj.layout, key=mark_mistake_obj.tab_key)]],
                           key="tab",
                           enable_events=True)]]

    window = sg.Window('Package Log Main Menu', layout, use_ttk_buttons=True, resizable=True).Finalize()

    current_return_bind = window['tab'].find_currently_active_tab_key() + 'return_bind'
    window.write_event_value('tab', check_in_obj.tab_key)

    while True:                             # The Event Loop
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            packagelog.db_close()
            break

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

        # matches all events for manual reports
        if event.startswith(man_reports_obj.tab_key):
            man_reports_obj.manual_reports_gui(window=window, event=event,
                                               filtered_values=PackageLogTabs.filter_read_dict(values))

        # matches all events for counts tab
        if event.startswith(count_all_obj.tab_key):
            count_all_obj.count_all_gui(window=window, event=event,
                                               filtered_values=PackageLogTabs.filter_read_dict(values))

    window.close()


def bind_return_set_focus(window, current_return_bind, tab_bind):
    window[current_return_bind].unbind("<Return>")
    window.bind("<Return>", tab_bind + 'return_bind')
    window[tab_bind + 'return_bind'].bind("<Return>", '')
    window[tab_bind + 'apartment'].set_focus()
    return tab_bind + 'return_bind'








main_menu()