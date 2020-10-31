import os
import re
import sys
import json
import socket
import psutil
import hashlib
import getpass
import logging
import subprocess
from time import sleep
from win32gui import *
from win32api import *
from pynput import mouse
from win32process import *
from pynput import keyboard
from datetime import datetime, timedelta
from pc_tracker.settings import save_config
from pc_tracker import logsys

# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes


def set_event_id():
    return hashlib.sha3_256(datetime.now().__str__().encode()).hexdigest()


class Options:
    # how much seconds must pass before the user is considered that he is in idle
    # default is 5min or 300s
    idle_lenght = 1

    # how many seconds must pass that windows data may be considered valuable logging
    time_spend_lenght = 0

    # GDPR - if some of data you consider to be private or don't want specific data in dataset add them here
    # private_data = ['login_user', ]
    private_data = []


class WindowStats:
    def __init__(self):
        # window tracker
        self.event_id = set_event_id()
        self.window_title = None
        self.pid = None
        self.application_name = None

        # host info data
        self.login_user = getpass.getuser()
        self.host_name = None
        self.host_local_ip = None
        self.update_host_data()

        # variables for tracking time spent
        self.time_spend = 0
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.idle_periods = dict()
        self.idle_total_time = 0
        self.active_time = 0

        if self.pid is None:
            self.window_title, self.pid, self.application_name = self.load_win_info()

    def update_host_data(self):
        self.host_name = socket.gethostname()
        self.host_local_ip = socket.gethostbyname(self.host_name)

    def load_win_info(self):
        try:
            window_title = GetWindowText(GetForegroundWindow())
            _, pid = GetWindowThreadProcessId(GetForegroundWindow())
            application_name = psutil.Process(pid).name()
        except psutil.NoSuchProcess:
            return None, None, None
        return window_title, pid, application_name


class MouseStats:
    def __init__(self):
        self.loc = GetCursorPos()
        self.mouse_move = False
        self.movement_detected = datetime.now()
        self.mouse_timer = 0
        self.event_listener = mouse.Listener(on_scroll=self.on_scroll, on_click=self.on_click)
        self.event_listener.start()

        self.scroll_direction = None
        self.scroll_start = datetime.now()
        self.scroll_end = datetime.now()
        self.scroll_position = None
        self.scroll_timeout = 1

        self.click_pos= None
        self.click_start = datetime.now()
        self.click_timeout = 1

    def mouse_active(self):
        self.mouse_move = True
        self.movement_detected = datetime.now()
        self.mouse_idle_time = 0

    def on_scroll(self, x, y, dx, dy):
        self.scroll_direction = 'down' if dy < 0 else 'up'
        if self.scroll_position != (x, y):
            self.scroll_position = (x, y)
            self.scroll_start = datetime.now()

    def on_click(self, x, y, button, pressed):
        button_pos = (x, y)
        button_name = button._name_
        if self.click_pos != button_pos:
            self.mouse_active()
            self.click_start = datetime.now()
            self.click_pos = button_pos

    def mouse_position(self):
        try:
            loc = GetCursorPos()
            if loc != self.loc:
                self.mouse_active()
                self.loc = loc
            else:
                self.mouse_move = False
                self.mouse_idle_time = (datetime.now()-self.movement_detected).total_seconds()
        except BaseException:
            return

    def mouse_events(self):
        # checking mouse movement
        self.mouse_position()

        # checking scrolling
        scroll_time_passed = (datetime.now() - self.scroll_start).total_seconds()
        if scroll_time_passed > self.scroll_timeout and self.scroll_direction is not None:
            self.scroll_direction = None
            self.scroll_position = None
            self.mouse_active()


class KeyboardStats:
    def __init__(self):
        self.keyboard_timer= 0
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_listener.start()
        self.press_detected = datetime.now()
        self.key_pressed = False

    def on_press(self, key):
        self.key_pressed = True
        self.press_detected = datetime.now()

    def on_release(self, key):
        self.key_pressed = False

    def keyboard_events(self):
        self.keyboard_idle_time = (datetime.now() - self.press_detected).total_seconds()


class GatherData(WindowStats, MouseStats, KeyboardStats, Options):
    def __init__(self, local=0):
        self.local = local
        self.locked_status = False
        self.current_data = dict()

        # inherits variables for current window data
        WindowStats.__init__(self)
        # inherits variables for mouse data
        MouseStats.__init__(self)
        # inherits variables for keyboard data
        KeyboardStats.__init__(self)

        # container that saves previous window data
        self.win_previous = WindowStats()

        self.idle_periods = dict()
        self.idle_data = dict()
        self.idle_start_time = None
        self.active_time = 0

        self.history_log = self.history_log_path()
        self.history_logger = logsys.history_logger_simple(self.history_log)

    def reset_idle(self):
        self.idle_periods = dict()
        self.idle_data = dict()
        self.idle_start_time = None

    def windows_handle(self):
        window_title, pid, application_name = self.load_win_info()
        if window_title is None and application_name is None:
            return

        if window_title != self.window_title:
            self.end_time = datetime.now()
            self.time_spend = (self.end_time-self.start_time).total_seconds()
            self.active_time = self.time_spend-self.idle_total_time
            [self.win_previous.__setattr__(k,v) for k,v
             in self.__dict__.items() if k in self.win_previous.__dict__.keys() and
             k not in self.private_data]
            window_previous_activity = self.win_previous.__dict__

            # save status only if time spent on window is longer then specified in Options
            if self.time_spend > self.time_spend_lenght:
                # from here we save data we gathered
                print(f"{window_previous_activity}")
                if self.local == 1:
                    event_id = window_previous_activity.get('event_id')
                    self.history_logger.info(event_id, window_previous_activity)

                # TODO: saving data remotely with logging module
                # TODO: saving data over HTTP request to server and saving data in db

            # loading values for current window
            self.window_title, self.pid, self.application_name = self.load_win_info()
            self.start_time = datetime.now()
            self.reset_idle()
            self.update_host_data()
            self.event_id = set_event_id()
            self.idle_total_time = 0
            self.active_time = 0

    def check_lock_screen(self):
        process_name = b'LogonUI.exe'
        get_tasklist = 'TASKLIST'
        tasklist = subprocess.check_output(get_tasklist)
        proc_data = [row for row in tasklist.split(b'\n') if row.startswith(process_name)]
        if proc_data and self.locked_status is False:
            self.locked_status = True
            self.windows_handle()
            self.locked_status = True
        else:
            self.locked_status = False

    def history_log_path(self, create=False):
        current_date = datetime.now().date()
        with open(save_config, 'r') as f:
            save_path = f.read()
            host_folder = os.path.join(save_path, self.host_local_ip)
        user_folder = os.path.join(host_folder, self.login_user)
        daily_folder = os.path.join(user_folder, user_folder, current_date.strftime("%Y%m%d"))
        if create is True:
            folders = [host_folder, user_folder, daily_folder]
            for folder in folders:
                for i in range(3):
                    if os.path.exists(folder) is False:
                        os.mkdir(folder)
                    else:
                        break
                    sleep(0.2)
        return os.path.join(daily_folder, 'history')


    def events_tracker(self):
        lock_switch = False
        folder_check_date = (datetime.now()-timedelta(days=1)).date()

        while True:
            if self.local == 1:
                # check folder existence
                current_date = datetime.now().date()
                if folder_check_date != current_date:
                    self.history_log = self.history_log_path(create=True)
                    folder_check_date = current_date

            self.check_lock_screen()
            if lock_switch is True and self.locked_status is False:
                self.login_user = getpass.getuser()
                lock_switch = False

            if self.locked_status is False:
                try:
                    self.windows_handle()
                    self.mouse_events()
                    self.keyboard_events()

                    if self.mouse_move is False and self.key_pressed is False and not self.idle_data :
                        self.idle_start_time = datetime.now()
                        self.idle_data.update({'start_idle': datetime.now()})

                    if (self.mouse_move is True or self.key_pressed is True) and self.idle_data and self.idle_start_time is not None:
                        idle_length = (datetime.now() - self.idle_start_time).total_seconds()
                        if idle_length > self.idle_lenght:
                            self.idle_total_time += idle_length
                            self.idle_data.update({'end_idle': datetime.now(), 'total_idle': int(idle_length)})
                            self.idle_periods.update({len(self.idle_periods): self.idle_data})
                        self.idle_data = dict()
                        self.idle_start_time = None

                    # realtime data on current window
                    current_time_spent = (datetime.now()-self.start_time).total_seconds()
                    current_active_time = (current_time_spent-self.idle_total_time)
                    self.current_data = {k: v for k, v in self.__dict__.items()
                                         if k in self.win_previous.__dict__.keys() and
                                         k not in self.private_data}
                    self.current_data.update({'time_spend': current_time_spent, 'active_time': current_active_time})
                    # sys.stdout.write(f"\r{self.current_data}")

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    error = {'err_type': str(exc_type), 'err_line': exc_tb.tb_lineno, 'err_desc': str(e)}
                    print(error)

            sleep(0.1)


if __name__ == '__main__':
    try:
        api = GatherData()
        api.events_tracker()
    except KeyboardInterrupt:
        pass


