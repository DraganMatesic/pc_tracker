import os
import sys
import pickle
import getpass

from pc_tracker import client
from subprocess import Popen, PIPE, call
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR

pc_tracker_dir = r'C:\Users\{}\Documents\pc_tracker_client'.format(getpass.getuser())


try:
    from tkinter import *
    from os.path import join
    from functools import partial
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    # from pc_tracker.settings import framework_folder, save_config
except ImportError:
    p = Popen('py -c "import sys; import os; sys.stdout.write(sys.executable)" ', stdout=PIPE)
    lines = p.stdout.readlines()
    real_executable = lines[0]

    p = Popen('py -c "import sys; import os; sys.stdout.write(os.path.dirname(sys.executable))"', stdout=PIPE)
    lines = p.stdout.readlines()
    main_path = lines[0].decode()
    pycon_path = os.path.join(main_path, 'manage.py')
    call('"{}" "{}"'.format(real_executable, pycon_path))


def create_config_folder():
    if os.path.exists(pc_tracker_dir) is False:
        os.mkdir(pc_tracker_dir)


class Configuration:
    def __init__(self):
        self.admin = self.admin_check()
        self.root = Tk()
        self.data_path = None
        self.setings_path = os.path.join(pc_tracker_dir, 'setings_path')
        create_config_folder()

    @staticmethod
    def is_venv():
        return (hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    @staticmethod
    def browse(textbox):
        filename = filedialog.askdirectory()
        textbox.insert(END, filename)
        textbox.update()

    def admin_check(self):
        try:
            os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
        except WindowsError:
            return False
        return True

    def submit(self, form_data, win):
        settings_path = form_data.get('settings_path').get('1.0', END).strip()
        settings_data = dict()
        settings_keys = ['data_path']
        for key, textbox in form_data.items():
            value = textbox.get('1.0', END).strip()
            if os.path.exists(value) is False:
                messagebox.showerror("Path not valid", "Specify valid path for {0}".format(key))
                return
            if key in settings_keys:
                settings_data.update({key: value})

        # creates local file that saves reference where to look for local network settings
        settings_file = os.path.join(settings_path, 'settings')
        with open(self.setings_path, 'w') as f:
            f.write(settings_file)

        # only admin can create settings file that all other users will use
        if self.admin is True:
            if os.path.exists(settings_file):
                os.chmod(settings_file, S_IWUSR | S_IREAD)
            with open(settings_file, 'wb') as f:
                pickle.dump(settings_data, f)
            os.chmod(settings_file, S_IREAD | S_IRGRP | S_IROTH)
        win.destroy()

    def config_form(self, client=False):
        if client is True:
            self.admin = False
        # setting up menu bar
        self.root.title('Configuration')
        frame = Frame(self.root, pady=5, padx=5)
        admin_options = ['data_path']
        options = {'data_path': "Path where you want to save your data",
                   'settings_path': 'Path for settings file'}
        cnt = 0
        form_data = dict()
        for key_name, option in options.items():
            if self.admin is False and key_name in admin_options:
                continue
            label = Label(frame, text=option, anchor=NW)
            label.grid(row=cnt,column=1, padx=(10, 1), sticky="W")
            cnt += 1
            textbox = Text(frame, height=1, width=50)
            textbox.grid(row=cnt,column=1, pady=3, padx=(10, 1), sticky="W")
            browse = partial(self.browse, textbox=textbox)
            browse_btn = Button(frame, text='Browse', command=browse)
            browse_btn.grid(row=cnt,column=2, pady=3, padx=(1, 5), sticky="W")
            form_data.update({key_name: textbox})
            cnt += 1

        submit = partial(self.submit, form_data=form_data, win=self.root)
        submit_btn = Button(frame, text='Submit', command=submit, width=50)
        submit_btn.grid(row=cnt, column=1, pady=(5, 10), padx=(10, 5), sticky="W")
        frame.pack()

        self.root.mainloop()

    def precheck(self):
        p = Popen('py -c "import sys; import os; sys.stdout.write(sys.prefix)" ', stdout=PIPE)
        lines = p.stdout.readlines()
        lib_path = lines[0]

        if self.is_venv():
            print("location of venv ", lib_path)
            p = Popen('py -c "import sys; import os; sys.stdout.write(os.path.dirname(sys.executable))"', stdout=PIPE)
            lines = p.stdout.readlines()
            main_path = lines[0].decode()
            pycon_path = os.path.join(main_path, 'manage.py')

            if os.path.exists(pycon_path) is False:
                sys.stdout.write("\n Can't locate manage.py at {0} \n make sure you are using python "
                                 "version where you installed this package then try again...".format(pycon_path))
                input("Press Enter to continue")
                exit()
            sys.stdout.write("\rPath status O.K.\n")
            return 200
        else:
            sys.stdout.write('\rPython3 is required\n')
            input("Press Enter to continue")
        return 400


if __name__ == '__main__':
    argvs = sys.argv
    if 'config' in argvs:
        api = Configuration()
        api.config_form()
    elif 'configcl' in argvs:
        api = Configuration()
        api.config_form(client=True)
    elif 'runclient' in argvs:
        api = client.GatherData()
        api.events_tracker()
    else:
        argvs_op = {'config': "Starts configuration form.",
                    'runclient': "Starts client in windowed mode."}
        sys.stdout.write('\rArgument required:\n')
        input("Press Enter to continue")


