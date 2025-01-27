"""
Copyright (c) 2016- 2024, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import datetime
import os
import sys
import time
from queue import Queue
import matplotlib
import pandas as pd
from functools import partial
import threading
import numpy as np

from wiliot_api.utils.get_version import get_version
from wiliot_core.packet_data.packet_list import PacketList
from wiliot_testers.tester_utils import dict_to_csv
from wiliot_testers.yield_tester.modules.first_gui import open_session, preparing_layout, inlays
from wiliot_testers.yield_tester.modules.adva_process import AdvaProcess, user_inputs, default_user_inputs
from wiliot_core.utils.utils import set_logger
from wiliot_testers.yield_tester.modules.main_gui import MainGui, MAX_Y_FOR_PLOTS, MIN_Y_FOR_PLOTS, FIRST_STEP_SIZE, \
    popup_message, WiliotGui
from wiliot_testers.yield_tester.utils.resolve_utils import ENV_RESOLVE, YieldTagStatus
from wiliot_tools.resolver_tool.resolve_packets import ResolvePackets

today = datetime.date.today()
formatted_today = today.strftime("%Y%m%d")  # without -
formatted_date = today.strftime("%Y-%m-%d")
current_time = datetime.datetime.now()
cur_time_formatted = current_time.strftime("%H%M%S")  # without :
time_formatted = current_time.strftime("%H:%M:%S")
TIME_BETWEEN_MATRICES = 0.5
RSSI_THRESHOLD = int(user_inputs.get('rssi_threshold', '0') or '0')
TESTER_TYPE = 'assembly_yield_tester'
matplotlib.use('TkAgg')


class MainWindow:
    """
    The main class the runs the GUI and supervise the multi-threading process of fraction's calculation and GUI viewing
    """

    def __init__(self):
        self.main_gui_instance = None
        self.first_gui_vals = None
        self.last_processed_index = 0
        self.current_values = None
        self.main_gui = None
        self.test_started = True
        self.logger = None
        self.adva_process = None
        self.adva_process_thread = None
        self.resolver_thread = None
        self.resolve_path = ''
        self.external_ids = []
        self.resolver = None
        self.resolve_q = Queue(maxsize=10000)
        self.folder_path = None
        self.run_data_path = None
        self.run_data_dict = None
        self.stop = threading.Event()
        self.tester_type_for_upload = 'yield'
        self.cmn = ''
        self.packets_data_path = None
        self.advas_before_tags = set()
        self.fig_canvas_agg1 = None
        self.yield_type = None
        self.machine_type = 'assembly_yield_tester'
        self.yield_df = pd.DataFrame(columns=['matrix_num', 'matrix_advas', 'matrix_external_ids', 'trigger_time'])

    ###############  BEFORE RUN FUNCTIONS ###############

    def setup_logger_and_paths(self):
        """
        Sets logger and paths for the run
        @return:
        """
        self.cmn = self.get_cmn(formatted_today, cur_time_formatted)
        logger_path, self.logger = set_logger(app_name=self.machine_type, common_run_name=self.cmn,
                                              folder_name=self.get_folder_name())
        self.folder_path = os.path.dirname(logger_path)
        self.run_data_dict, self.run_data_path = self.init_run_data(cmn=self.cmn, folder_path=self.folder_path,
                                                                    inlay=self.first_gui_vals['selected'],
                                                                    received_channel=
                                                                    inlays[self.first_gui_vals['selected']][
                                                                        'received_channel'])
        self.packets_data_path = os.path.join(self.folder_path, f"{self.cmn}@packets_data.csv")

    def init_run_data(self, cmn, folder_path, inlay, received_channel):
        """
        Initialize run data csv file.
        @return:
        """
        py_wiliot_version = get_version()
        run_data_path = os.path.join(folder_path, cmn + '@run_data.csv')
        start_time = datetime.datetime.now()
        run_start_time = start_time.strftime("%H:%M:%S")
        run_data_dict = {
            'common_run_name': cmn, 'tester_station_name': self.first_gui_vals.get('tester_station_name', ''),
            'operator': self.first_gui_vals.get('operator', ''), 'received_channel': received_channel,
            'run_start_time': formatted_date + ' ' + run_start_time, 'run_end_time': '',
            'wafer_lot': self.first_gui_vals.get('wafer_lot', ''),
            'wafer_number': self.first_gui_vals.get('wafer_number', ''),
            'assembled reel': self.first_gui_vals.get('assembled_reel', ''),
            'lane_ids': self.first_gui_vals.get('lane_ids', ''),
            'window_size': self.first_gui_vals.get('window_size', ''), 'upload_date': '',
            'gw_energy_pattern': self.first_gui_vals.get('gw_energy_pattern', ''),
            'comments': self.first_gui_vals.get('comments', ''), 'inlay': inlay, 'total_run_tested': 0,
            'total_run_responding_tags': 0,
            'conversion_type': self.first_gui_vals.get('conversion_type', ''),
            'surface': self.first_gui_vals.get('surface', ''),
            'matrix_tags': str(self.first_gui_vals.get('matrix_size', '')), 'py_wiliot_version': py_wiliot_version,
            'number_of_columns': self.first_gui_vals.get('thermodes_col', ''),
            'number_of_lanes': self.first_gui_vals.get('rows_number', ''),
            'gw_time_profile': self.first_gui_vals.get('gw_time_profile', '')
        }

        return run_data_dict, run_data_path

    def first_gui_setup(self):
        """
        Does all the work of the first gui.
        @return:
        """
        previous_input, inlay_info_dict = preparing_layout()
        layout, cols_or_rows = self.open_session_layout(previous_input=previous_input, inlay_info=inlay_info_dict)
        self.first_gui_vals = open_session(open_session_layout=layout, cols_or_rows=cols_or_rows)
        return self.first_gui_vals

    def get_cmn(self, day_str, time_str):
        """
        Creates the common run name of the files we want to save.
        @param day_str: Date of the day
        @param time_str: time stamp
        @return: common run name
        """
        return '{wafer_lot}.{wafer_number}_{day}_{time}'.format(wafer_lot=self.first_gui_vals['wafer_lot'],
                                                                wafer_number=self.first_gui_vals['wafer_number'],
                                                                day=day_str, time=time_str)

    def get_folder_name(self):
        return '{}.{}'.format(self.first_gui_vals['wafer_lot'], self.first_gui_vals['wafer_number'])

    @staticmethod
    def open_session_layout(previous_input, inlay_info):
        """
        Returns GUI as dictionary for wiliotGUI
        @param previous_input: Dictionary of default values.
        @param inlay_info: Info about Inlay we take from data_inlay/data_inlay_eng
        @return: GUI as dictionary for wiliotGUI
        """
        cols_or_rows = 'thermodes_col'
        open_session_layout = {
            'wafer_lot': {'text': 'Wafer Lot:', 'value': previous_input['wafer_lot'], 'widget_type': 'entry'},
            'wafer_num': {'text': 'Wafer Number:', 'value': previous_input['wafer_num'], 'widget_type': 'entry'},
            'thermodes_col': {'text': 'Number of Columns:', 'value': previous_input['thermodes_col'],
                              'widget_type': 'entry'},
            'matrix_tags': {'text': '', 'widget_type': 'label',
                            'value': f'Matrix tags: {str(inlay_info["default_matrix_tags"])}'},
            'inlay_dict': [
                {'inlay': {'text': 'Inlay:', 'value': previous_input['inlay_dict_inlay'], 'widget_type': 'combobox',
                           'options': list(inlays.keys())}},
                {'inlay_info': {'widget_type': 'label', 'value': inlay_info['inlay_info']}},
            ],
            'tester_station_name': {'text': 'Tester Station:', 'value': previous_input['tester_station_name'],
                                    'widget_type': 'entry'},
            'comments': {'text': 'Comments:', 'value': previous_input['comments'], 'widget_type': 'entry'},
            'operator': {'text': 'Operator:', 'value': previous_input['operator'], 'widget_type': 'entry'},
            'conversion_type': {'text': 'Conversion:', 'value': previous_input['conversion_type'],
                                'widget_type': 'combobox', 'options': inlay_info["conv_opts"]},
            'surface': {'text': 'Surface:', 'value': previous_input['surface'], 'widget_type': 'combobox',
                        'options': inlay_info["surfaces"]},
            'window_size': {'text': 'Window Size for Analysis:', 'value': previous_input['window_size'],
                            'widget_type': 'entry'},
            'do_resolve': {'text': 'Get External Id from Cloud', 'value': previous_input['do_resolve']},
            'owner_id': {'text': 'Owner Id for Cloud Connection', 'value': previous_input['owner_id']},

        }

        return open_session_layout, cols_or_rows

    ###############  RUNNING CLASS FUNCTIONS ###############

    def init_processes(self, inlay_select, time_between_matrices=TIME_BETWEEN_MATRICES, rssi_th=RSSI_THRESHOLD):
        """
        Initializing the two main instances and threads in order to start working
        @param inlay_select: Inlay type we are running
        @param time_between_matrices: Time between two triggers in seconds
        @param rssi_th: RSSI threshold we want to filter according to it.
        @return:
        """
        try:
            adva_process_inputs = {'inlay_type': inlay_select, 'listener_path': self.folder_path,
                                   'time_between_matrices': time_between_matrices, 'rssi_th': rssi_th, 'cmn': self.cmn}
            self.adva_process = AdvaProcess(stop_event=self.stop, logger=self.logger,
                                            adva_process_inputs=adva_process_inputs)

            self.adva_process_thread = threading.Thread(target=self.adva_process.run, args=())
            self.init_resolver(owner_id=self.first_gui_vals['owner_id'], logger_name=self.logger.name,
                               tag_status_class=YieldTagStatus, gui_type='ttk')
        except Exception as e:
            self.logger.warning(f"{e}")
            popup_message(msg='GW is not connected. Please connect it.', logger=self.logger)
            raise Exception(f'GW is not connected {e}')

        if self.first_gui_vals['do_resolve']:
            self.yield_type = 'External Ids'
        else:
            self.yield_type = 'Advas'

    def start_processes(self):
        """
        Starting the work of the both threads
        @return:
        """
        self.adva_process_thread.start()
        if self.resolver_thread is not None:
            self.resolver_thread.start()

    def run(self):
        """
        Viewing the window and checking if the process stops
        @return:
        """
        self.first_gui_setup()
        self.setup_logger_and_paths()
        self.init_processes(self.first_gui_vals['selected'])
        time.sleep(0.5)
        self.init_resolver_data()
        self.start_processes()
        gui = self.overlay_window()
        return gui

    def stop_yield(self):
        """
        All the work when the application is stopped (User interaction or Error).
        @return:
        """
        self.stop.set()
        final_tags = 1 if self.get_number_of_tested() == 0 else self.get_number_of_tested()
        total_ex_ids = 0 if self.yield_df.empty else self.yield_df['matrix_external_ids'].sum()
        total_advas = 0 if self.yield_df.empty else self.yield_df['matrix_advas'].sum()

        self.logger.info(
            'Final Adva Yield: %s, Final External Ids Yield: %s, Final Tags: %05d, Final Advas: %05d,'
            ' Final External Ids: %05d', total_advas / final_tags, total_ex_ids / final_tags, final_tags, total_advas,
            total_ex_ids)
        self.logger.info(f"User quit from application")

        is_uploaded = self.main_gui_instance.upload_to_cloud(main_gui=self.main_gui, cmn=self.cmn,
                                                             tester_type_for_upload=self.tester_type_for_upload,
                                                             run_data_path=self.run_data_path,
                                                             packets_data_path=self.packets_data_path,
                                                             prev_owner_id=self.first_gui_vals['owner_id'])
        end_time = datetime.datetime.now()
        run_end_time = end_time.strftime("%H:%M:%S")
        if is_uploaded:
            upload_date = run_end_time
        else:
            upload_date = ''
        tags_num = self.get_number_of_tested()
        result = float(100 * (total_advas / tags_num)) if tags_num != 0 else float('nan')
        if self.adva_process_thread.is_alive():
            self.adva_process_thread.join(timeout=5)
        self.update_run_data_file(formatted_date + ' ' + run_end_time, tags_num, total_advas, result, upload_date)
        self.update_packet_data()
        time.sleep(1)
        sys.exit()

    ###############  RESOLVE FUNCTIONS ###############

    def init_resolver(self, owner_id, logger_name, tag_status_class, gui_type='ttk'):
        """
        Initializes and sets up the ResolvePackets instance and its thread.
        """
        self.resolver = ResolvePackets(
            tags_in_test=[],
            owner_id=owner_id,
            env=ENV_RESOLVE,
            resolve_q=self.resolve_q,
            set_tags_status_df=self.updated_resolved_tags,
            stop_event_trig=self.stop,
            logger_name=logger_name,
            gui_type=gui_type,
            tag_status=tag_status_class
        )

    def updated_resolved_tags(self, tag_status):
        """
        Updating resolve data.
        """
        tag_status = {k: v[0] for k, v in tag_status.items()}
        new_ex_id = tag_status['external_id']
        matrix_num = tag_status['matrix_num']
        self.logger.info(f'update resolved tags: {new_ex_id}')
        if new_ex_id not in self.external_ids:
            self.external_ids.append(new_ex_id)
            self.yield_df.loc[self.yield_df['matrix_num'] == matrix_num, 'matrix_external_ids'] += 1

        dict_to_csv(dict_in=tag_status, path=self.resolve_path, append=True)

    def init_resolver_data(self):
        if not self.first_gui_vals['do_resolve']:
            return

        self.resolve_path = os.path.join(self.folder_path, self.cmn + '@resolve_data.csv')
        dict_to_csv({'adv_address': [], 'resolve_status': [], 'external_id': []},
                    self.resolve_path, only_titles=True)

    def add_to_resolve_queue(self, packet_in):
        """
        Adds resolve data to the queue while running.
        """
        adva = packet_in.get_adva()
        marix_num = packet_in.custom_data['matrix_tags_location']
        if self.resolve_q.full():
            self.logger.warning(f'Resolve queue is full. Discard the following adva: {adva}')
            return
        self.resolve_q.put({'tag': adva, 'payload': packet_in.get_payload(), 'matrix_num': marix_num}, )

    ###############  UPDATES FUNCTIONS ###############

    def update_packet_data(self):
        """
        Updates the run_data CSV file while running the program
        @return:
        """
        cur_packets_or_triggers_q = self.adva_process.get_packet_of_unq_tags()
        n_elements = cur_packets_or_triggers_q.qsize()

        # Collecting Packets from the queue and putting them into a TagCollection
        new_packet_list = PacketList()
        for _ in range(n_elements):
            cur_p_or_t_dict = cur_packets_or_triggers_q.get()
            if 'trigger' in cur_p_or_t_dict.keys():  # a trigger was caught
                #  creating a new row in the dataframe
                new_row = {'matrix_num': cur_p_or_t_dict['trigger']['trigger_num'], 'matrix_advas': 0,
                           'matrix_external_ids': 0,
                           'trigger_time': cur_p_or_t_dict['trigger']['trigger_time']}

                if self.yield_df.empty:
                    self.yield_df = pd.DataFrame([new_row])
                else:
                    self.yield_df = pd.concat([self.yield_df, pd.DataFrame([new_row])], ignore_index=True)

            else:  # a packet caught
                if not self.yield_df.empty:
                    self.yield_df.loc[
                        self.yield_df['matrix_num'] == cur_p_or_t_dict['packet'].custom_data['matrix_tags_location'],
                        'matrix_advas'] += 1

                    if self.first_gui_vals['do_resolve']:
                        self.add_to_resolve_queue(cur_p_or_t_dict['packet'])
                        if not self.resolve_q.empty():
                            self.resolver.get_external_id_and_update()  # TODO need to do it on the adva_process
                    new_packet_list.append(cur_p_or_t_dict['packet'])

        packet_list_df = new_packet_list.get_df()
        if not packet_list_df.empty:
            if not os.path.exists(self.packets_data_path):
                packet_list_df.to_csv(self.packets_data_path, mode='w', header=True, index=False)
            else:
                packet_list_df.to_csv(self.packets_data_path, mode='a', header=False, index=False)

    def update_run_data_file(self, run_end_time, tags_num, advas, result, upload_date=''):

        """
        Updates the run_data CSV file while running the program
        @param run_end_time: Last time stamp of the update
        @param tags_num: Number of tested tags
        @param advas: Number of seen advas
        @param result: Yield fraction
        @param upload_date: Upload date
        @return:
        """
        self.run_data_dict['gw_version'] = self.adva_process.gw_instance.get_gw_version()[0]
        self.run_data_dict['tester_type'] = self.tester_type_for_upload
        self.run_data_dict['run_end_time'] = run_end_time
        self.run_data_dict['upload_date'] = upload_date
        self.run_data_dict['total_run_tested'] = tags_num
        self.run_data_dict['total_run_responding_tags'] = advas
        self.run_data_dict['yield'] = result
        if self.first_gui_vals['do_resolve'] and not self.yield_df.empty:
            self.run_data_dict['total_run_external_ids'] = self.yield_df['matrix_external_ids'].sum()
            self.run_data_dict['yield_external_ids'] = 100 * (
                    self.run_data_dict['total_run_external_ids'] / tags_num) if tags_num else 0
        dict_to_csv(dict_in=self.run_data_dict, path=self.run_data_path)

    def update_cumulative_graph(self, cumulative_graph_update_args):
        """
        Updates the cumulative graph
        @return:
        """
        all_data = self.yield_df
        x_values = all_data['matrix_num'] * self.first_gui_vals['matrix_size']
        needed_col = 'matrix_advas' if self.yield_type == 'Advas' else 'matrix_external_ids'
        cumulative_sum = all_data[needed_col].cumsum()
        y_values = cumulative_sum / (all_data['matrix_num'] * self.first_gui_vals['matrix_size']) * 100
        cumulative_graph_update_args.get('axy').clear()
        cumulative_graph_update_args.get('axy').set_ylim(
            [self.current_values['cumulative_min_y_value'], self.current_values['cumulative_max_y_value']])
        axy_y_ticks = np.arange(self.current_values['cumulative_min_y_value'],
                                self.current_values['cumulative_max_y_value'] + 10,
                                self.current_values['cumulative_size_value'])
        cumulative_graph_update_args.get('axy').set_yticks(axy_y_ticks)
        cumulative_graph_update_args.get('axy').yaxis.grid(True)
        if self.main_gui_instance.main_gui_dict['user_inputs'].get('min_cumulative_line') == 'yes':
            min_cumulative = int(self.main_gui_instance.main_gui_dict['default_user_inputs']['min_cumulative'])
            if self.current_values['cumulative_min_y_value'] <= min_cumulative <= self.current_values[
                'cumulative_max_y_value']:
                cumulative_graph_update_args.get('axy').axhline(y=min_cumulative, color='black', linestyle='--')
        cumulative_graph_update_args.get('axy').plot(x_values, y_values, color='blue', marker='o', linestyle='-', )
        yield_type_str = 'Advas' if self.yield_type == 'Advas' else 'External Ids'
        if len(all_data) > 0:
            cumulative_title = f"{yield_type_str} Cumulative Yield: {y_values.iloc[-1]:.2f}%"
            cumulative_graph_update_args.get('axy').text(0.18, 1.05, cumulative_title,
                                                         transform=cumulative_graph_update_args.get('axy').transAxes,
                                                         fontweight='bold')
        self.fig_canvas_agg1.draw()

    def update_current_graph(self, args):
        """
        Updates the current graph with data points averaged over chunks of window size.
        """
        window_size = int(self.first_gui_vals['window_size'])
        max_index = len(self.yield_df) - 1
        if self.last_processed_index >= max_index or max_index == 0:
            return  # No new data to process

        all_data = self.yield_df.iloc[:max_index + 1]
        needed_col = 'matrix_advas' if self.yield_type == 'Advas' else 'matrix_external_ids'

        matrix_size = self.first_gui_vals['matrix_size']
        x_values = (all_data['matrix_num'] * matrix_size * window_size)

        num_full_windows = len(all_data) // window_size
        if num_full_windows == 0:
            return  # Not enough data to process

        complete_data = all_data.iloc[:num_full_windows * window_size]
        grouped = complete_data[needed_col].groupby(complete_data.index // window_size)
        y_values = (grouped.sum() / (window_size * matrix_size)) * 100

        args['ax'].clear()
        args['ax'].set_ylim([self.current_values['current_min_y_value'], self.current_values['current_max_y_value']])
        axy_y_ticks = np.arange(self.current_values['current_min_y_value'],
                                self.current_values['current_max_y_value'] + 10,
                                self.current_values['current_size_value'])
        args['ax'].set_yticks(axy_y_ticks)
        args['ax'].yaxis.grid(True)
        if self.main_gui_instance.main_gui_dict['user_inputs'].get('min_current_line') == 'yes':
            min_current = int(self.main_gui_instance.main_gui_dict['default_user_inputs']['min_current'])
            if self.current_values['current_min_y_value'] <= min_current <= self.current_values['current_max_y_value']:
                args['ax'].axhline(y=min_current, color='black', linestyle='--')

        args['ax'].plot(x_values.iloc[:len(y_values)], y_values, color='blue', marker='o', linestyle='-')

        if not y_values.empty:
            current_plot_title = f"{self.main_gui_instance.get_current_plot_title(yield_type=self.yield_type, window_size=self.first_gui_vals['window_size'])}: {y_values.iloc[-1]:.2f} %"
            args['ax'].text(0.18, 1.05, current_plot_title, transform=args['ax'].transAxes, fontweight='bold')

        self.last_processed_index = max_index
        self.update_params_for_current_graph(all_data)

    def update_gui(self, args):
        """
        Updates all main GUI details.
        @param args: Dictionary containing all the required arguments for GUI updates.
        """
        self.update_packet_data()
        if self.last_processed_index < len(self.yield_df):
            self.update_current_graph(args)

        cumulative_graph_update_args = {'axy': args['axy'], 'text_box1': args['text_box1']}

        self.update_cumulative_graph(cumulative_graph_update_args)

        new_num_rows = self.get_number_of_tested()
        new_num_advas = 0 if self.yield_df.empty else self.yield_df['matrix_advas'].sum()

        args['gui_instance'].update_widget('counting_row_num_rows', f"Number of tags: {new_num_rows}")
        args['gui_instance'].update_widget('counting_row_num_advas', f"Number of advas: {new_num_advas}")
        if self.first_gui_vals['do_resolve']:
            args['gui_instance'].update_widget('counting_row_num_ex_ids',
                                               f"Number of external ids: {self.yield_df['matrix_external_ids'].sum()}")

        self.main_gui_instance.sesnor_values_color_in_main_gui(main_gui=self.main_gui,
                                                               main_gui_params=args['main_gui_params'])

        end_time = datetime.datetime.now()
        run_end_time = end_time.strftime("%H:%M:%S")
        advas = 0 if self.yield_df.empty else self.yield_df['matrix_advas'].sum()
        tags_num = self.get_number_of_tested()
        result = float(100 * (advas / tags_num)) if tags_num != 0 else float('nan')
        self.update_run_data_file(formatted_date + ' ' + run_end_time, tags_num, advas, result)

        # Correct canvas drawing
        self.fig_canvas_agg1.draw()

        if self.adva_process.get_gw_error_connection():
            self.stop_yield()

    def update_params_for_current_graph(self, all_data):
        """
        Updates the run parameters of the current yield graph.
        @param all_data: DataFrame containing all necessary data.
        """
        sensor_vals = self.adva_process.read_and_return_sensor_values()

        all_advas = 0 if self.yield_df.empty else self.yield_df['matrix_advas'].sum()
        all_external_ids = 0 if self.yield_df.empty else self.yield_df['matrix_external_ids'].sum()
        matrix_num = all_data['matrix_num'].iloc[-1]
        latest_adva = all_data['matrix_advas'].iloc[-1]
        latest_ex_ids = all_data['matrix_external_ids'].iloc[-1]

        adva_yield_result_formatted = "%.5f" % self.get_yield_result(all_advas)
        adva_latest_yield_formatted = "{:.5f}".format(float(latest_adva / self.first_gui_vals['matrix_size']) * 100)
        ex_yield_result_formatted = "%.5f" % self.get_yield_result(all_external_ids)
        ex_latest_yield_formatted = "{:.5f}".format(float(latest_ex_ids / self.first_gui_vals['matrix_size']) * 100)
        all_tested = matrix_num * self.first_gui_vals['matrix_size']

        self.logger.info(
            'Matrix Number: %05d, Cumulative Advas Yield: %s, Cumulative External Ids Yield: %s, Cumulative Tags: %05d,'
            ' Cumulative Advas: %05d, Cumulative External Ids: %05d, '
            'Latest Advas Yield: %s, Latest External Ids Yield: %s, Latest Tags: %05d, Latest Advas: %05d,'
            ' Latest External Ids: %05d, Humidity: %05.1f, Temperature: %05.1f, Light Intensity: %05.1f',
            matrix_num, adva_yield_result_formatted, ex_yield_result_formatted, all_tested, all_advas,
            all_external_ids, adva_latest_yield_formatted, ex_latest_yield_formatted,
            self.first_gui_vals['matrix_size'], latest_adva,
            latest_ex_ids, float(sensor_vals.get('temperature', 0.0)), float(sensor_vals.get('humidity', 0.0)),
            float(sensor_vals.get('light_intensity', 0.0))
        )

    ###############  MAIN GUI FUNCTIONS ###############

    @staticmethod
    def init_main_gui_params():
        main_gui_params = dict()
        for key in default_user_inputs.keys():
            if key not in (
                    'pin_number', 'temperature_type', 'min_current_line', 'min_cumulative_line', 'rssi_threshold'):
                main_gui_params[key] = float(user_inputs.get(key, default_user_inputs[key]))
            else:
                main_gui_params[key] = user_inputs.get(key, default_user_inputs[key])
        return main_gui_params

    def create_main_gui(self, sensor_vals, main_gui_params, temp_val, temperature_type):
        main_gui_dict = {'user_inputs': user_inputs, 'sensor_vals': sensor_vals, 'temperature_type': temperature_type,
                         'temp_val': temp_val, 'do_resolve': self.first_gui_vals['do_resolve'],
                         'default_user_inputs': default_user_inputs, 'logger': self.logger}
        self.main_gui_instance = MainGui(main_gui_dict)
        overlay_layout_dict = self.main_gui_instance.main_gui_layout()
        return overlay_layout_dict

    def handling_advanced_settings_window(self, advanced_settings_inputs):
        """
        Do all the work that is related to the advanced settings
        @param advanced_settings_inputs: A dictionary of advanced settings' parameters.
        @return:
        """
        self.logger.info('Advanced settings was pressed')
        advanced_layout_dict = self.main_gui_instance.advanced_gui_layout(self.yield_type)
        advanced_gui = WiliotGui(params_dict=advanced_layout_dict, exit_sys_upon_cancel=False,
                                 parent=self.main_gui.layout, title='Advanced Settings')
        advanced_gui.set_button_command(
            'reset_button',
            lambda: self.main_gui_instance.reset_button(main_gui=self.main_gui, advanced_gui=advanced_gui,
                                                        advanced_settings_inputs=advanced_settings_inputs))
        user_out = advanced_gui.run()

        if not self.current_values:
            self.current_values = {
                'current_min_y_value': advanced_settings_inputs.get('current_min_y_value'),
                'current_max_y_value': advanced_settings_inputs.get('current_max_y_value'),
                'current_size_value': advanced_settings_inputs.get('current_size_value'),
                'cumulative_min_y_value': advanced_settings_inputs.get('cumulative_min_y_value'),
                'cumulative_max_y_value': advanced_settings_inputs.get('cumulative_max_y_value'),
                'cumulative_size_value': advanced_settings_inputs.get('cumulative_size_value'),
                'window_size': advanced_settings_inputs.get('window_size', 1),
                'yield_type': 'Advas',
            }

        if user_out:
            self.main_gui.layout.attributes('-alpha', 1.0)
            for adv_key, adv_value in user_out.items():
                if adv_value and adv_key != 'window_size' and adv_key != 'yield_type':
                    new_value = self.main_gui_instance.get_adv_value(adv_key=adv_key, adv_value=adv_value,
                                                                     current_values=self.current_values,
                                                                     advanced_gui=advanced_gui)
                else:
                    if adv_key == 'yield_type':
                        new_value = adv_value
                        self.current_values[adv_key] = new_value
                        if self.yield_type != new_value:
                            for line in advanced_settings_inputs.get('ax').get_lines():
                                line.remove()
                            for line in advanced_settings_inputs.get('axy').get_lines():
                                line.remove()
                            self.yield_type = new_value
                    else:
                        new_value = int(
                            self.main_gui_instance.get_adv_value(adv_key=adv_key, adv_value=adv_value,
                                                                 current_values=self.current_values,
                                                                 advanced_gui=advanced_gui))
                        self.first_gui_vals['window_size'] = new_value
                        self.main_gui.window_size = new_value
                self.current_values[adv_key] = new_value
                self.logger.info(f"{adv_key} changed to {new_value}")
            self.main_gui_instance.current_adv_settings_graphs(advanced_settings_inputs=advanced_settings_inputs,
                                                               current_values=self.current_values)
            self.fig_canvas_agg1.draw()

    def overlay_window(self):
        """
        Main GUI window.
        @return:
        """
        # Taking values from user_input JSON file
        main_gui_params = self.init_main_gui_params()
        # Creating the main window
        sensor_vals = self.adva_process.read_and_return_sensor_values()
        temp_val = sensor_vals['temperature'] if (main_gui_params['temperature_type'] ==
                                                  "C") else sensor_vals['temperature'] * 9 / 5 + 32
        overlay_layout_dict = self.create_main_gui(sensor_vals=sensor_vals, main_gui_params=main_gui_params,
                                                   temp_val=temp_val,
                                                   temperature_type=main_gui_params['temperature_type'])

        # Setting up GUI
        self.main_gui = WiliotGui(params_dict=overlay_layout_dict, full_screen=True, do_button_config=False,
                                  title='Yield Tester')

        # Initializing graphs
        current_plot_title = self.main_gui_instance.get_current_plot_title(yield_type=self.yield_type,
                                                                           window_size=self.first_gui_vals[
                                                                               'window_size'])
        self.fig_canvas_agg1, ax, axy, text_box, text_box1 = \
            self.main_gui_instance.init_graphs(main_gui=self.main_gui, current_plot_title=current_plot_title)
        advanced_settings_inputs = {'ax': ax, 'current_min_y_value': MIN_Y_FOR_PLOTS,
                                    'window_size': self.first_gui_vals['window_size'],
                                    'current_max_y_value': MAX_Y_FOR_PLOTS, 'cumulative_min_y_value': MIN_Y_FOR_PLOTS,
                                    'text_box': text_box, 'current_size_value': FIRST_STEP_SIZE, 'axy': axy,
                                    'cumulative_max_y_value': MAX_Y_FOR_PLOTS, 'cumulative_size_value': FIRST_STEP_SIZE,
                                    }
        self.current_values = advanced_settings_inputs

        advanced_settings_callback = partial(self.handling_advanced_settings_window, advanced_settings_inputs)

        self.main_gui.set_button_command('buttons_row_advanced_settings_button', advanced_settings_callback)
        self.main_gui.set_button_command('buttons_row_stop_button', self.stop_yield)
        self.main_gui.set_button_command('buttons_row_pause_button', self.pause_and_start_button)

        # initialize num_advas and num_rows
        num_rows, num_advas = 0, 0
        self.main_gui.update_widget('counting_row_num_rows', f"Number of tags: {num_rows}")
        self.main_gui.update_widget('counting_row_num_advas', f"Number of advas: {num_advas}")
        if self.first_gui_vals['do_resolve'] and not self.yield_df.empty:
            self.main_gui.update_widget('counting_row_num_ex_ids',
                                        f"Number of external ids: {0 if self.yield_df.empty else self.yield_df['matrix_external_ids'].sum()}")

        update_gui_args = {'gui_instance': self.main_gui, 'text_box': text_box, 'ax': ax, 'axy': axy,
                           'text_box1': text_box1, 'prev_tests': 0, 'prev_val': 0, 'prev_tests1': 0, 'prev_val1': 0,
                           'num_rows': 0, 'num_advas': 0, 'result': float('nan'),
                           'main_gui_params': main_gui_params}
        # Setting up recurrent GUI updates
        self.main_gui.add_recurrent_function(500, lambda: self.update_gui(update_gui_args))
        return self.main_gui

    def pause_and_start_button(self):
        """
        Does the work when the user click on Pause/Start test.
        @return:
        """
        self.test_started = not self.test_started
        self.adva_process.set_stopped_by_user(not self.test_started)
        if self.test_started:
            self.logger.info('Test was started by user')
            self.main_gui.update_widget('buttons_row_pause_button', 'Pause Test')

        else:
            self.logger.info('Test was paused by user')
            self.main_gui.update_widget('buttons_row_pause_button', 'Start Test')

    def get_yield_result(self, advas_or_external):
        """
        Calculates the yield fraction for a given advas_or_external.
        @param advas_or_external: The collection (e.g., seen_advas or external_ids) to calculate yield for.
        @return: Yield fraction for the collection.
        """
        result = 0
        tags_num = self.yield_df['matrix_num'].iloc[-1] * self.first_gui_vals['matrix_size']
        if tags_num > 0:
            result = (advas_or_external / tags_num) * 100
        return result

    def get_number_of_tested(self):
        """
        Return number of tested tags.
        @return: number of tested tags.
        """
        tags_num = 0
        if not self.yield_df.empty:
            tags_num = self.yield_df['matrix_num'].iloc[-1] * int(self.first_gui_vals['thermodes_col']) * int(
                self.first_gui_vals['rows_number'])
        return tags_num


if __name__ == '__main__':
    m = MainWindow()
    gui = m.run()
    gui.run()
