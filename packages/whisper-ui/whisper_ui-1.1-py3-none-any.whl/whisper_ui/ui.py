import os
import sys
import glob
import time
from functools import partial
import warnings
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename, askdirectory

import whisper

from whisper_ui.whisper_funcs import transcribe, check_model, AVAILABLE_MODELS
from whisper_ui.handle_prefs import set_option, USER_PREFS, AVAILABLE_LANGUAGES

warnings.filterwarnings('ignore')

def file_choose_wrapper():
    app.glob_path_entry.delete(0, len(app.glob_path_entry.get()))
    app.glob_path_entry.insert(0, os.path.normpath(askopenfilename()))
    
def dir_choose_wrapper():
    app.glob_path_entry.delete(0, len(app.glob_path_entry.get()))
    app.glob_path_entry.insert(
        0,
        os.path.normpath(os.path.join(askdirectory(),'*'))
    )
    
def paths_wrapper():
    print(f'Clicking "Transcribe" will process:')
    for path in glob.glob(app.glob_path_entry.get()):
        print(f'\t{os.path.normpath(path)}')
    print()

def transcribe_wrapper():
    transcribe(glob.glob(app.glob_path_entry.get()))
    
def set_output_dir_wrapper():
    new_value = app.output_dir_entry.get()
    set_option('output_dir', new_value)
    p = os.path.normpath(os.path.abspath(new_value))
    print(f'Outputs will be written to "{p}".\n')
    
def model_select_wrapper(event):
    new_value = app.model_clicked.get()
    set_option('model', new_value)
    print(f'Using model "{new_value}".\n')
    
def language_select_wrapper(event):
    new_value = app.language_clicked.get()
    set_option('language', new_value)
    print(f'Assuming language "{new_value}".\n')
    
def download_model(model_name):
    if not check_model(model_name):
        result = messagebox.askokcancel(
            'Confirm model download',
            f'Would you like to download {model_name}?'
        )
        if result:
            print(f'Downloading model {model_name}...')
            whisper.load_model(name=model_name)
            print(f'Downloaded model {model_name} successfully. Reloading window...\n')
            time.sleep(1)
            reload()
        else:
            print(f'Download canceled.\n')
    else:
        print(f'Model {model_name} already downloaded.\n')

def reload():
    global app
    app.destroy()
    app = MainGUI()
    app.mainloop()

class PrintLogger(object):  # create file like object

    def __init__(self, textbox: ScrolledText):  # pass reference to text widget
        self.textbox = textbox  # keep ref
        self.textbox.configure(state="disabled")

    def write(self, text):
        self.textbox.configure(state="normal")  # make field editable
        self.textbox.insert("end", text)  # write text to textbox
        if '%' in text:
            self.textbox.insert("end", '\r')
        self.textbox.see("end")  # scroll to end
        self.textbox.configure(state="disabled")  # make field readonly
        self.textbox.update_idletasks()
        
    def clear(self):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', tk.END)
        self.textbox.configure(state='disabled')

    def flush(self):  # needed for file like object
        pass



class MainGUI(Tk):

    def __init__(self):
        Tk.__init__(self)
        # window
        self.title("Whisper User Interface")
        w = 800 # width for the Tk root
        h = 500 # height for the Tk root
        # get screen width and height
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40
        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        
        
        # menu
        self.menu = Menu(self)
        self.file_menu = Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label='Open file', command=file_choose_wrapper)
        self.file_menu.add_command(label='Open directory', command=dir_choose_wrapper)
        self.models_menu = Menu(self.menu, tearoff=False)
        for model_name in AVAILABLE_MODELS:
            if check_model(model_name):
                self.models_menu.add_command(
                    label=model_name + ' ✓',
                    command=partial(download_model, model_name)
                )
            else:
                self.models_menu.add_command(
                    label=model_name + ' ⤓',
                    command=partial(download_model, model_name)
                )
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.menu.add_cascade(label='Download models', menu=self.models_menu)
        self.config(menu=self.menu)
        
        
        
        # frame
        self.root = Frame(self)
        
        
        
        # console log
        self.log_widget = ScrolledText(
            self.root,
            height=12,
            width=120,
            font=("consolas", "10", "normal")
        )
        self.logger = PrintLogger(self.log_widget)
        sys.stdout = self.logger
        sys.stderr = self.logger
        
        
        
        # file path entry
        self.glob_path_desc = Label(
            self,
            text = "File path(s) to transcribe:"
        )
        self.glob_path_entry = Entry(
            self,
            width=100
        )
        self.glob_path_entry.insert(0, os.path.join('test_audio', '*.m4a'))
        self.transcribe_button = Button(
            self,
            text = "Transcribe",
            fg = "red",
            command = transcribe_wrapper
        )
        # list file paths in glob
        self.list_files_button = Button(
            self,
            text = "List files",
            fg = "black",
            command = paths_wrapper
        )
        
        
        
        # edit output_dir
        self.output_dir_desc = Label(
            self,
            text = "Change output directory:"
        )
        self.output_dir_entry = Entry(
            self,
            width=20
        )
        self.output_dir_entry.insert(0, USER_PREFS['output_dir'])
        self.set_output_dir_button = Button(
            self,
            text = "Set output directory",
            fg = "black",
            command = set_output_dir_wrapper
        )
        
        
        
        # select model
        self.model_clicked = StringVar()
        self.model_clicked.set(USER_PREFS['model'])
        self.select_model_desc = Label(
            self,
            text = 'Currently selected Whisper model:'
        )
        self.select_model_entry = ttk.Combobox(
            self,
            textvariable=self.model_clicked,
            values=AVAILABLE_MODELS
        )
        self.select_model_entry.current(AVAILABLE_MODELS.index(USER_PREFS['model']))
        self.select_model_entry['state'] = 'readonly'
        self.select_model_entry.bind(
            '<<ComboboxSelected>>', model_select_wrapper
        )
        
        
        
        # clear log button
        self.clear_log_button = Button(
            self,
            text = "Clear output",
            fg = "black",
            command = self.logger.clear
        )
        
        
        
        # set language
        self.language_clicked = StringVar()
        self.language_clicked.set(USER_PREFS['language'])
        self.select_language_desc = Label(
            self,
            text = 'Currently selected Whisper language:'
        )
        self.select_language_entry = ttk.Combobox(
            self,
            textvariable=self.language_clicked,
            values=AVAILABLE_LANGUAGES
        )
        self.select_language_entry.current(AVAILABLE_LANGUAGES.index(USER_PREFS['language']))
        self.select_language_entry['state'] = 'readonly'
        self.select_language_entry.bind(
            '<<ComboboxSelected>>', language_select_wrapper
        )
        
        
        
        # layout
        self.root.pack()
        self.log_widget.pack()
        self.glob_path_desc.pack()
        self.glob_path_entry.pack()
        self.transcribe_button.pack()
        self.list_files_button.pack()
        self.output_dir_desc.pack()
        self.output_dir_entry.pack()
        self.set_output_dir_button.pack()
        self.select_model_desc.pack()
        self.select_model_entry.pack()
        self.clear_log_button.pack()
        self.select_language_desc.pack()
        self.select_language_entry.pack()



def main():
    app = MainGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
