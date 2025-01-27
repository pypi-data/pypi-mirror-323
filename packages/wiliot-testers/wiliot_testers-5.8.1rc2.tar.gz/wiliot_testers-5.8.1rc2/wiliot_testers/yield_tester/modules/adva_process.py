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

import importlib
import os
import json
import time
import datetime
from queue import Queue
from collections import deque

from wiliot_testers.yield_tester.configs.inlay_data import all_inlays
from wiliot_testers.yield_tester.simulation.yield_simulation_utils import get_simulated_gw_port, AUTO_PACKET, \
    AUTO_TRIGGERS, TIME_BETWEEN_AUTO_TRIGGERS
from wiliot_core import CommandDetails, WiliotGateway, ActionType, DataType
from wiliot_core import Packet
from wiliot_tools.test_equipment.test_equipment import YoctoSensor

script_dir = os.path.dirname(__file__)
json_file_path = os.path.join(script_dir, '../configs', 'user_inputs.json')
default_user_inputs = {
    "min_cumulative": "60",
    "min_cumulative_line": "yes",
    "min_current": "20",
    "min_current_line": "yes",
    "max_temperature": "40",
    "min_temperature": "10",
    "temperature_type": "C",
    "min_humidity": "20",
    "max_humidity": "90",
    "min_light_intensity": "0",
    "max_light_intensity": "1500",
    "red_line_cumulative": "85",
    "red_line_current": "50",
    "pin_number": "004",
    "rssi_threshold": ""
}
try:
    with open(json_file_path) as f:
        user_inputs = json.load(f)
    for key, value in default_user_inputs.items():
        if key not in user_inputs:
            user_inputs[key] = value
    with open(json_file_path, 'w') as f:
        json.dump(user_inputs, f, indent=4)
except Exception as e:
    user_inputs = default_user_inputs
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    with open(json_file_path, 'w') as f:
        json.dump(user_inputs, f, indent=4)

SECONDS_WITHOUT_PACKETS = 60
SECONDS_FOR_GW_ERROR_AFTER_NO_PACKETS = 120
MAX_SUB1G_POWER = 29
MAX_BLE_POWER = 22
VALUE_WHEN_NO_SENSOR = -10000

inlay_data_eng_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs', 'inlay_data_eng.py')
if os.path.exists(inlay_data_eng_path):
    inlay_data = getattr(importlib.import_module('wiliot_testers.yield_tester.configs.inlay_data_eng'), 'all_inlays',
                         {})
    inlays = inlay_data if inlay_data else all_inlays
else:
    inlays = all_inlays


class AdvaProcess(object):
    """
    Counting the number of unique advas
    """

    def __init__(self, stop_event, logger, adva_process_inputs):

        self.unq_packets_new_triggers = Queue()
        self.sensor_vals = {}
        self.main_sensor = None
        self.seen_advas = set()
        self.adva_process_inputs = adva_process_inputs
        self.advas_before_tags = set()
        self.stopped_by_user = False
        self.take_care_of_pausing = False
        self.gw_error_connection = False
        self.print_neg_advas = True
        self.second_without_packets = False  # This is only used to print no packets after one minute
        self.gw_instance = None
        self.logger = logger
        self.all_tags = Queue()
        self.stop = stop_event
        self.gw_start_time = datetime.datetime.now()
        self.trigger_time_queue = deque(maxlen=10)
        self.last_change_time = 0
        self.number_of_sensor_triggers = 0
        self.needed_time_between_matrices = TIME_BETWEEN_AUTO_TRIGGERS if AUTO_TRIGGERS else self.adva_process_inputs[
            'time_between_matrices']
        self.init_gw(self.adva_process_inputs['listener_path'])
        self.gw_reset_config()
        time.sleep(1)
        self.setup_sensors()

    def init_gw(self, listener_path=None):

        try:
            if self.gw_instance is None:
                gw_port = get_simulated_gw_port() if AUTO_PACKET else None
                self.gw_instance = WiliotGateway(auto_connect=True,
                                                 logger_name=self.logger.name,
                                                 log_dir_for_multi_processes=listener_path,
                                                 port=gw_port,
                                                 np_max_packet_in_buffer_before_error=10)

            else:
                # reconnect
                is_connected = self.gw_instance.is_connected()
                if is_connected:
                    self.gw_instance.close_port()
                self.gw_instance.open_port(self.gw_instance.port, self.gw_instance.baud)

            is_connected = self.gw_instance.is_connected()
            if is_connected:
                self.gw_instance.start_continuous_listener()
            else:
                self.logger.warning("Couldn't connect to GW in main thread")
                raise Exception(f"Couldn't connect to GW in main thread")

        except Exception as ee:
            raise Exception(f"Couldn't connect to GW in main thread, error: {ee}")

    def set_stopped_by_user(self, stopped):
        self.stopped_by_user = stopped
        self.take_care_of_pausing = True

    def calculate_ttfp_with_queue(self, packet_time):
        """
        Calculates ttfp (time to first packet) for each packet within the run.
        @param packet_time: The time we recieve the packet.
        @return:
        """
        while self.trigger_time_queue:
            try:
                trigger_time, matrix_cnt = self.trigger_time_queue[0]
                if len(self.trigger_time_queue) > 1:
                    trigger_time_next, _ = self.trigger_time_queue[1]
                else:
                    trigger_time_next = float('inf')
                # [matrix_x, time_x] <= p_time <= [matrix_y, time_y] --> p from matrix x
                if trigger_time <= packet_time <= trigger_time_next:
                    return trigger_time, matrix_cnt, packet_time - trigger_time
                elif packet_time < trigger_time:  # got packet before trigger
                    return float('nan'), matrix_cnt - 1, float('nan')
                else:  # packet_time > trigger_time_next
                    # Remove the processed trigger time
                    self.trigger_time_queue.popleft()

            except Exception as e:
                self.logger.warning(f'Could not calculate tag matrix TTFP due to {e}')
                break
        return float('nan'), None, float('nan')

    def gw_reset_config(self, start_gw_app=False):
        """
        Configs the gateway
        """
        if self.gw_instance.connected:
            self.gw_instance.reset_gw()
            self.gw_instance.reset_listener()
            time.sleep(2)
            if not self.gw_instance.is_gw_alive():
                self.logger.warning('gw_reset_and_config: gw did not respond')
                raise Exception('gw_reset_and_config: gw did not respond after rest')

            gw_config = inlays.get(self.adva_process_inputs['inlay_type'])

            cmds = {CommandDetails.scan_ch: gw_config['received_channel'],
                    CommandDetails.time_profile: gw_config['time_profile_val'],
                    CommandDetails.set_energizing_pattern: gw_config['energy_pattern_val'],
                    CommandDetails.set_sub_1_ghz_power: [MAX_SUB1G_POWER],
                    CommandDetails.set_scan_radio: self.gw_instance.get_cmd_symbol_params(
                        freq_str=gw_config['symbol_val']),
                    CommandDetails.set_rssi_th: self.adva_process_inputs['rssi_th'],
                    }
            output_power_cmds = self.gw_instance.get_cmds_for_abs_output_power(abs_output_power=MAX_BLE_POWER)
            cmds = {**cmds, **output_power_cmds}
            self.gw_instance.set_configuration(cmds=cmds, start_gw_app=start_gw_app, read_max_time=1)
            if not AUTO_TRIGGERS:
                pin_num = user_inputs.get('pin_number')
                cmd = '!cmd_gpio CONTROL_IN P%s 0' % pin_num.zfill(3)
                self.gw_instance.write(cmd, must_get_ack=True)
        else:
            raise Exception('Could NOT connect to GW')

    def raising_trigger_number(self):
        self.number_of_sensor_triggers += 1
        self.logger.info(f'Got a Trigger.  Number of Triggers {self.number_of_sensor_triggers}')

    def read_and_return_sensor_values(self):
        if self.main_sensor:
            self.sensor_vals = {'light_intensity': self.main_sensor.get_light(),
                                'humidity': self.main_sensor.get_humidity(),
                                'temperature': self.main_sensor.get_temperature()}
        return self.sensor_vals

    def setup_sensors(self):
        try:
            self.main_sensor = YoctoSensor(self.logger)
        except Exception as ee:
            self.main_sensor = None
            self.logger.info(f'No sensor is connected ({ee})')
        if self.main_sensor:
            self.sensor_vals = {'light_intensity': self.main_sensor.get_light(),
                                'humidity': self.main_sensor.get_humidity(),
                                'temperature': self.main_sensor.get_temperature()}
        else:
            self.sensor_vals = {'light_intensity': VALUE_WHEN_NO_SENSOR,
                                'humidity': VALUE_WHEN_NO_SENSOR,
                                'temperature': VALUE_WHEN_NO_SENSOR}

    def create_packet_process(self):
        """
        Does the process of adding a new Packet to our collection
        """
        if not self.all_tags.empty():
            n_elements = self.all_tags.qsize()
            # Collecting Packets from the queue and putting them into a TagCollection
            for _ in range(n_elements):
                for p in self.all_tags.get():
                    trigger_time, matrix_cnt, tag_matrix_ttfp = self.calculate_ttfp_with_queue(p['time'])
                    cur_p = Packet(p['raw'], time_from_start=p['time'],
                                   inlay_type=self.adva_process_inputs['inlay_type'],
                                   custom_data={'common_run_name': self.adva_process_inputs['cmn'],
                                                'matrix_tags_location': matrix_cnt,
                                                'matrix_timestamp': trigger_time, 'tag_matrix_ttfp': tag_matrix_ttfp,
                                                'environment_light_intensity': self.sensor_vals['light_intensity'],
                                                'environment_humidity': self.sensor_vals['humidity'],
                                                'environment_temperature': self.sensor_vals['temperature']})

                    tag_id = cur_p.get_adva()

                    if self.number_of_sensor_triggers == 0:
                        self.advas_before_tags.add(tag_id)
                    else:
                        if self.print_neg_advas:
                            self.logger.info('neglected advas:  %05d', len(self.advas_before_tags))
                            self.print_neg_advas = False

                    if tag_id not in self.seen_advas and tag_id not in self.advas_before_tags:
                        self.seen_advas.add(tag_id)
                        self.logger.info(f"New adva {tag_id}")
                        self.unq_packets_new_triggers.put({'packet': cur_p})

    def get_packet_of_unq_tags(self):
        return self.unq_packets_new_triggers

    def check_new_trigger(self, gw_rsps):  # for loop for the signals (not one signal)
        if AUTO_TRIGGERS:
            self.last_change_time = (datetime.datetime.now() - self.gw_start_time).total_seconds()  # a float
            self.raising_trigger_number()
            self.trigger_time_queue.append([self.last_change_time, self.number_of_sensor_triggers])
            self.unq_packets_new_triggers.put({'trigger': {'trigger_time': self.last_change_time,
                                                           'trigger_num': self.number_of_sensor_triggers}})
        else:
            for gw_rsp in gw_rsps:
                if gw_rsp is not None and 'Detected High-to-Low peak' in gw_rsp['raw'] and not self.stopped_by_user:
                    self.last_change_time = gw_rsp['time']  # a float
                    self.raising_trigger_number()
                    self.trigger_time_queue.append([self.last_change_time, self.number_of_sensor_triggers])
                    self.unq_packets_new_triggers.put({'trigger': {'trigger_time': self.last_change_time,
                                                                   'trigger_num': self.number_of_sensor_triggers}})

    def run(self):
        """
        Receives available data then counts and returns the number of unique advas.
        """
        self.gw_instance.set_configuration(start_gw_app=True)
        self.gw_instance.reset_start_time()
        self.gw_start_time = datetime.datetime.now()
        got_new_adva = False
        no_data_start_time = None  # Time when we first detect no data available

        while not self.stop.is_set():
            time.sleep(0)
            current_time_of_data = (datetime.datetime.now() - self.gw_start_time).total_seconds()
            time_condition_met = current_time_of_data - self.last_change_time >= self.needed_time_between_matrices

            gw_rsps = self.gw_instance.get_gw_signals()

            if not self.stopped_by_user and self.take_care_of_pausing:
                self.gw_reset_config(start_gw_app=True)
                self.take_care_of_pausing = False
            elif self.stopped_by_user and self.take_care_of_pausing:
                self.gw_instance.reset_gw()
                self.take_care_of_pausing = False

            if self.gw_instance.is_data_available() and not self.stopped_by_user:
                raw_packets_in = self.gw_instance.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                              data_type=DataType.RAW,
                                                              tag_inlay=self.adva_process_inputs['inlay_type'])
                if not self.all_tags.full():
                    self.all_tags.put(raw_packets_in)
                else:
                    self.logger.warning(f"Queue is full.. Packet: {raw_packets_in}")
                got_new_adva = True
                no_data_start_time = None
                self.create_packet_process()

            if time_condition_met:
                self.check_new_trigger(gw_rsps=gw_rsps)

            if not (self.gw_instance.is_data_available() and not self.stopped_by_user):
                no_data_start_time, got_new_adva = self.no_advas_checks(no_data_start_time, got_new_adva)

        self.gw_instance.reset_gw()
        self.gw_instance.exit_gw_api()

    def no_advas_checks(self, no_data_start_time, got_new_adva):
        """
        Does all the work when GW does not receive packets
        """
        if not self.stopped_by_user:
            if no_data_start_time is None:
                no_data_start_time = time.time()
            if time.time() - no_data_start_time >= SECONDS_WITHOUT_PACKETS:
                got_new_adva = False
                if not self.second_without_packets:
                    self.logger.warning("One minute without packets..")
                    self.second_without_packets = True
                time.sleep(5)
                if not self.gw_instance.is_connected():
                    self.reconnect()
            if time.time() - no_data_start_time >= SECONDS_FOR_GW_ERROR_AFTER_NO_PACKETS:
                self.gw_error_connection = True
            if self.gw_instance.get_read_error_status():
                self.logger.warning("Reading error.. Listener did recovery flow.")
            time.sleep(0.050 if not got_new_adva else 0)
        else:
            no_data_start_time = None
        return no_data_start_time, got_new_adva

    def get_gw_error_connection(self):
        """
        Gets the error variable to discover if GW has an error
        """
        return self.gw_error_connection

    def reconnect(self):
        """
        Tries to reconnect GW when a problem occurred
        """
        self.logger.info('Trying to reconnect to GW')
        try:
            self.init_gw()
            self.gw_reset_config(start_gw_app=True)
        except Exception as e:
            self.gw_error_connection = True
            self.logger.warning(f"Couldn't reconnect GW, due to: {e}")
