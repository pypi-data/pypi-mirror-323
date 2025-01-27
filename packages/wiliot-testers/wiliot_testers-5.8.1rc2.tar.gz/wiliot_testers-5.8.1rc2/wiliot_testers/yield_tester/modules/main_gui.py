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

import queue
import threading
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message

RED_COLOR = 'red'
BLACK_COLOR = 'black'
SET_VALUE_MORE_THAN_100 = 110
MIN_Y_FOR_PLOTS = 0
MAX_Y_FOR_PLOTS = 112
FIRST_STEP_SIZE = 10

advanced_default_values = {
    'current_min_y_value': 0,
    'current_max_y_value': 120,
    'current_size_value': 10,
    'cumulative_min_y_value': 0,
    'cumulative_max_y_value': 120,
    'cumulative_size_value': 10,
    'window_size': 1,
    'yield_type': 'Advas'}


class MainGui:
    def __init__(self, main_gui_dict):
        self.main_gui_dict = main_gui_dict
        self.sensor_vals = self.main_gui_dict['sensor_vals']
        self.logger = main_gui_dict['logger']

    def init_graphs(self, main_gui, current_plot_title):
        """
        Initialize both graphs
        @return:
        """
        # create the main figure and two subplots
        fig, (ax, axy) = plt.subplots(1, 2, figsize=(12, 7))
        fig.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15, wspace=0.2)
        # initialize the first graph
        ax.set_xlabel('Number of tags')
        ax.set_ylabel('Yield %')
        ax.set_ylim([MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS])
        ax_y_ticks = np.arange(MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS + FIRST_STEP_SIZE, FIRST_STEP_SIZE)
        ax.set_yticks(ax_y_ticks)
        ax.tick_params(axis='y', which='both', labelsize=10)
        plt.ion()
        ax.yaxis.grid(True)
        text_box = ax.text(0.18, 1.05,
                           f"{current_plot_title}: 0.00 %",
                           transform=ax.transAxes, fontweight='bold')
        if self.main_gui_dict['user_inputs'].get('min_current_line') == 'yes':
            min_current = int(self.main_gui_dict['default_user_inputs']['min_current'])
            if MIN_Y_FOR_PLOTS <= min_current <= MAX_Y_FOR_PLOTS:
                ax.axhline(y=min_current, color='black', linestyle='--')
        # initialize the second graph
        axy.set_xlabel('Number of tags')
        axy.set_ylabel('Yield %')
        axy.set_ylim([MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS])
        axy_y_ticks = np.arange(MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS + 10, FIRST_STEP_SIZE)
        axy.set_yticks(axy_y_ticks)
        axy.tick_params(axis='y', which='both', labelsize=10)
        plt.ion()
        axy.yaxis.grid(True)
        text_box1 = axy.text(0.18, 1.05, f"Cumulative Yield: 0.0 %", transform=axy.transAxes,
                             fontweight='bold')
        if self.main_gui_dict['user_inputs'].get('min_cumulative_line') == 'yes':
            min_cumulative = int(self.main_gui_dict['default_user_inputs']['min_cumulative'])
            if MIN_Y_FOR_PLOTS <= min_cumulative <= MAX_Y_FOR_PLOTS:
                axy.axhline(y=min_cumulative, color='black', linestyle='--')

        canvas_elem1 = main_gui.layout
        fig_canvas_agg1 = self.draw_figure(canvas_elem1, fig)
        return fig_canvas_agg1, ax, axy, text_box, text_box1

    def main_gui_layout(self):
        overlay_layout_dict = {
            'counting_row': [{'num_rows': {'text': '', 'widget_type': 'label', 'value': 'Number of tags:',
                                           'options': {'font': ('Arial', 26, 'bold')}}},
                             {'num_advas': {'text': '', 'widget_type': 'label', 'value': 'Number of advas:',
                                            'options': {'font': ('Arial', 26, 'bold')}}},
                             ],
            'sensor_row': [{'light_intensity_value': {'text': '', 'widget_type': 'label',
                                                      'options': {'font': ('Arial', 14, 'bold')},
                                                      'value': f'Light Intensity: {self.sensor_vals["light_intensity"]}'}},
                           {'temperature_value': {'widget_type': 'label', 'options': {'font': ('Arial', 14, 'bold')},
                                                  'value': f"Temperature: {self.main_gui_dict['temp_val']} {self.main_gui_dict['temperature_type']}"}},
                           {'humidity_value': {'widget_type': 'label',
                                               'value': f'Humidity: {self.sensor_vals["humidity"]}',
                                               'options': {'font': ('Arial', 14, 'bold')}, }
                            }, ],

            'space': {'value': '', 'widget_type': 'label'},
            'buttons_row': [
                {'advanced_settings_button': {'text': 'Advanced Settings', 'value': '', 'widget_type': 'button'}},
                {'stop_button': {'text': 'Stop', 'value': '', 'widget_type': 'button'}},
                {'pause_button': {'text': 'Pause Test', 'value': '', 'widget_type': 'button'}}]
        }

        if self.main_gui_dict['do_resolve']:
            overlay_layout_dict['counting_row'].append(
                {'num_ex_ids': {'text': '', 'widget_type': 'label', 'value': 'Number of external ids:',
                                'options': {'font': ('Arial', 26, 'bold')}}}
            )
        return overlay_layout_dict

    def sesnor_values_color_in_main_gui(self, main_gui, main_gui_params):
        """
        Finds all sensors values and shows it in the GUI.
        @param main_gui_params: Dictionary of user configs parameters.
        @return:
        """
        temperature_display = f"{self.sensor_vals['temperature']:.2f} °C"

        if main_gui_params.get('temperature_type') == "F":
            temperature_display = f"{self.sensor_vals['temperature'] * 9 / 5 + 32:.2f} °F"
        temperature_color = BLACK_COLOR if (
                main_gui_params.get('min_temperature') <= self.sensor_vals['temperature'] <=
                main_gui_params.get('max_temperature')) else RED_COLOR
        light_intensity_color = BLACK_COLOR if (
                main_gui_params.get('min_light_intensity') <= self.sensor_vals['light_intensity'] <=
                main_gui_params.get('max_light_intensity')) else RED_COLOR
        humidity_color = BLACK_COLOR if (main_gui_params.get('min_humidity') <= self.sensor_vals['humidity'] <=
                                         main_gui_params.get('max_humidity')) else RED_COLOR
        main_gui.update_widget('sensor_row_temperature_value', f'Temperature: {temperature_display}',
                               color=temperature_color)
        if 'sensor_row_light_intensity_value' in main_gui.widgets:
            main_gui.update_widget('sensor_row_light_intensity_value',
                                   f'Light Intensity: {self.sensor_vals["light_intensity"]} lux',
                                   color=light_intensity_color
                                   )
        main_gui.update_widget('sensor_row_humidity_value', f'Humidity: {self.sensor_vals["humidity"]} %',
                               color=humidity_color)

    def do_upload_thread(self, cmn, tester_type_for_upload, run_data_path, packets_data_path, env_choice,
                         result_queue, owner_id):
        try:
            is_uploaded = upload_to_cloud_api(batch_name=cmn, tester_type=tester_type_for_upload + '-test',
                                              run_data_csv_name=run_data_path, env=env_choice, is_path=True,
                                              packets_data_csv_name=packets_data_path, owner_id=owner_id)

        except Exception as ee:
            is_uploaded = False
            self.logger.error(f"do_upload_thread: Exception occurred: {ee}")
        result_queue.put(is_uploaded)

    def upload_to_cloud(self, main_gui, cmn, tester_type_for_upload, run_data_path, packets_data_path,
                        prev_owner_id=''):
        """
        All the process of uploading data to cloud.
        @return:
        """
        upload_flag = True
        env_choice = 'prod'
        yes_or_no = ['Yes', 'No']
        upload_owner_id = None
        upload_layout_dic = {'ask_to_upload': {'widget_type': 'label', 'value': 'Do you want to stop or upload?'},
                             'upload': {'text': 'Upload:', 'value': yes_or_no[0], 'widget_type': 'combobox',
                                        'options': yes_or_no},
                             'env_choice': {'text': 'Select Environment:', 'value': 'prod', 'widget_type': 'combobox',
                                            'options': ['prod', 'test']},
                             'owner_id': {'text': 'Owner Id', 'value': prev_owner_id,
                                          'widget_type': 'entry'}
                             }
        upload_layout_dic_gui = WiliotGui(params_dict=upload_layout_dic, parent=main_gui.layout,
                                          title='Upload to cloud')
        upload_layout_dic_values_out = upload_layout_dic_gui.run()

        if upload_layout_dic_values_out:
            upload_flag = upload_layout_dic_values_out['upload'] == 'Yes'
            env_choice = upload_layout_dic_values_out['env_choice']
            upload_owner_id = upload_layout_dic_values_out['owner_id']

        if upload_flag:
            result_queue = queue.Queue()
            upload_thread = threading.Thread(target=self.do_upload_thread, args=(
                cmn, tester_type_for_upload, run_data_path, packets_data_path, env_choice,
                result_queue, upload_owner_id,))
            upload_thread.start()
            upload_thread.join(timeout=5)

            if not result_queue.empty():
                is_uploaded = result_queue.get()
            else:
                is_uploaded = False
            if is_uploaded:
                self.logger.info("Successful upload")
            else:
                self.logger.info('Failed to upload the file')
                popup_message(msg="Run upload failed. Check exception error at the console"
                                  " and check Internet connection is available"
                                  " and upload logs manually", tk_frame=main_gui.layout, logger=self.logger)
            main_gui.on_close()

        else:
            self.logger.info('File was not uploaded')

    def get_adv_value(self, adv_key, adv_value, current_values, advanced_gui):
        """
        Pulls the values of advanced settings' parameters from GUI fields.
        @param adv_key: The key of the advanced setting parameter.
        @param adv_value: The value entered in the GUI field.
        @param current_values: Dictionary of the current values of advanced settings.
        @param advanced_gui: The WiliotGui instance for advanced settings.
        @return: The new value of the parameter.
        """
        if not adv_value.isdigit() and adv_value != '':
            popup_message(msg=f"A not-number character in {adv_key}", tk_frame=advanced_gui.layout, logger=self.logger)
            return None
        if adv_value != '':
            new_value = int(adv_value)  # if user wrote a value
        elif current_values[adv_key]:
            new_value = current_values[adv_key]  # if the user did not write a value and not the first submit
        else:
            new_value = int(advanced_default_values[adv_key])  # if the user did not write a value and first submit
        return new_value

    def reset_button(self, main_gui, advanced_gui, advanced_settings_inputs):
        """
        Resets all advanced settings' parameters to the default values.
        @param advanced_gui: The WiliotGui instance for advanced settings.
        @param advanced_settings_inputs: Dictionary of advanced settings' parameters.
        """
        self.logger.info("Reset values from advanced settings")
        for key in advanced_default_values:
            advanced_gui.update_widget(key, advanced_default_values[key])
            globals()[key] = advanced_default_values[key]

        advanced_settings_inputs.get('ax').set_ylim([advanced_settings_inputs.get('current_min_y_value'),
                                                     advanced_settings_inputs.get('current_max_y_value')])
        advanced_settings_inputs.get('ax').set_yticks(
            np.arange(advanced_settings_inputs.get('current_min_y_value'),
                      advanced_settings_inputs.get('current_max_y_value') + advanced_settings_inputs.get(
                          'current_size_value'),
                      advanced_settings_inputs.get('current_size_value')))

        advanced_settings_inputs.get('axy').set_ylim([advanced_settings_inputs.get('cumulative_min_y_value'),
                                                      advanced_settings_inputs.get('cumulative_max_y_value')])
        advanced_settings_inputs.get('axy').set_yticks(
            np.arange(advanced_settings_inputs.get('cumulative_min_y_value'),
                      advanced_settings_inputs.get('cumulative_max_y_value') + advanced_settings_inputs.get(
                          'cumulative_size_value'),
                      advanced_settings_inputs.get('cumulative_size_value')))
        main_gui.window_size = 1
        return 'Advas'

    @staticmethod
    def advanced_gui_layout(yield_type):
        advanced_layout_dict = {
            'current_min_y_value': {'text': 'Current" min y:', 'value': '', 'widget_type': 'entry'},
            'current_max_y_value': {'text': '"Current" max y:', 'value': '', 'widget_type': 'entry'},
            'current_size_value': {'text': '"Current" step:', 'value': '', 'widget_type': 'entry'},
            'cumulative_min_y_value': {'text': '"Cumulative" min y:', 'value': '', 'widget_type': 'entry'},
            'cumulative_max_y_value': {'text': '"Cumulative" max y', 'value': '', 'widget_type': 'entry'},
            'cumulative_size_value': {'text': '"Cumulative" step:', 'value': '', 'widget_type': 'entry'},
            'window_size': {'text': 'Window size:', 'value': '', 'widget_type': 'entry'},
            'yield_type': {'text': 'Yield type', 'value': yield_type, 'widget_type': 'combobox',
                           'options': ['Advas', 'External Ids']},
            'reset_button': {'text': 'Reset', 'value': '', 'widget_type': 'button'},
        }
        return advanced_layout_dict

    @staticmethod
    def current_adv_settings_graphs(advanced_settings_inputs, current_values):
        advanced_settings_inputs.get('ax').set_ylim(
            [current_values['current_min_y_value'], current_values['current_max_y_value']])
        advanced_settings_inputs.get('ax').set_yticks(np.arange(current_values['current_min_y_value'],
                                                                current_values['current_max_y_value'] +
                                                                current_values[
                                                                    'current_size_value'],
                                                                current_values['current_size_value']))

        advanced_settings_inputs.get('axy').set_ylim(
            [current_values['cumulative_min_y_value'], current_values['cumulative_max_y_value']])
        advanced_settings_inputs.get('axy').set_yticks(np.arange(current_values['cumulative_min_y_value'],
                                                                 current_values['cumulative_max_y_value'] +
                                                                 current_values[
                                                                     'cumulative_size_value'],
                                                                 current_values['cumulative_size_value']))

    @staticmethod
    def get_current_plot_title(yield_type, window_size):
        """
        Write the yield type with window size for the current yield graph
        @return:
        """
        yield_type = 'Advas Yield' if yield_type == 'Advas' else 'External Ids Yield'

        return f'{yield_type} of last {window_size} matrices'

    @staticmethod
    def draw_figure(canvas, figure):
        """
        Embeds a Matplotlib figure in a Canvas Element
        @param canvas: Canvas we want to draw on.
        @param figure: Figure we want to show.
        @return:
        """
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().grid(row=3, column=0, sticky="nsew", columnspan=120)
        figure_canvas_agg.get_tk_widget().configure(width=520, height=500)
        return figure_canvas_agg
