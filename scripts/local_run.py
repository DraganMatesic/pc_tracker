import os
import sys
import getpass
from pc_tracker import client
from subprocess import Popen, PIPE, call

try:
    from tkinter import *
    from os.path import join
    from functools import partial
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from pc_tracker.settings import framework_folder, save_config
except ImportError:
    p = Popen('py -c "import sys; import os; sys.stdout.write(sys.executable)" ', stdout=PIPE)
    lines = p.stdout.readlines()
    real_executable = lines[0]

    p = Popen('py -c "import sys; import os; sys.stdout.write(os.path.dirname(sys.executable))"', stdout=PIPE)
    lines = p.stdout.readlines()
    main_path = lines[0].decode()
    pycon_path = os.path.join(main_path, 'local_run.py')
    call('"{}" "{}"'.format(real_executable, pycon_path))


class LocalRun(object):
    def __init__(self):
        self.root = Tk()
        self.data_path = None

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

    def submit(self, textbox, win):
        data_path = textbox.get('1.0', END).strip()
        if len(data_path) == 0:
            messagebox.showerror("Path not valid", 'Specify valid path')
            return
        with open(save_config, 'w') as f:
            f.write(data_path)
        self.data_path = data_path
        win.destroy()

    def config_form(self):
        # setting up menu bar
        self.root.title('Configuration')
        frame = Frame(self.root, pady=5, padx=5)

        frame1 = Frame(frame)
        Label(frame1, text="Choose path where you want to save you data", anchor=NW).pack(anchor=NW)
        textbox = Text(frame1, height=1, width=50)
        textbox.pack(side=LEFT)

        browse = partial(self.browse, textbox=textbox)
        browse_btn = Button(frame1, text='Browse', command=browse)
        browse_btn.pack(side=LEFT)

        submit = partial(self.submit, textbox=textbox, win=self.root)
        submit_btn = Button(frame1, text='Submit', command=submit)
        submit_btn.pack(side=LEFT)

        frame1.pack(anchor=NW)
        frame.pack()

        self.root.mainloop()

    def start(self):
        if os.path.exists(framework_folder) is False:
            os.mkdir(framework_folder)

        p = Popen('py -c "import sys; import os; sys.stdout.write(sys.prefix)" ', stdout=PIPE)
        lines = p.stdout.readlines()
        lib_path = lines[0]

        if self.is_venv():
            print("location of venv ", lib_path)
            p = Popen('py -c "import sys; import os; sys.stdout.write(os.path.dirname(sys.executable))"', stdout=PIPE)
            lines = p.stdout.readlines()
            main_path = lines[0].decode()
            pycon_path = os.path.join(main_path, 'local_run.py')

            if os.path.exists(pycon_path) is False:
                sys.stdout.write("\n Can't locate local_run.py at {0} \n make sure you are using python "
                                 "version where you installed this package then try again...".format(pycon_path))
                input("Press Enter to continue")
                exit()
            sys.stdout.write("\rPath status O.K.\n")
            if os.path.exists(save_config) is False:
                self.config_form()
            else:
                with open(save_config, 'r') as f:
                    self.data_path = f.read()
                    if self.data_path == '':
                        self.config_form()
            try:
                api = client.GatherData(local=1)
                api.events_tracker()
            except KeyboardInterrupt:
                pass

        else:
            sys.stdout.write('\rPython3 is required\n')
            input("Press Enter to continue")


if __name__ == '__main__':
    api = LocalRun()
    api.start()
