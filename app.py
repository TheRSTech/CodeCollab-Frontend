import tkinter as tk
from tkinter import scrolledtext, filedialog
from tkinter.ttk import Treeview
import subprocess
import threading
import os
from lib.file_ops.file_operations import new_file, open_file, save_file, save_file_as, exit_editor, open_folder
from lib.file_ops.edit_operations import copy_line, paste_line, cut_line, redo_function, undo_function
from lib.utils.check_system import check_system

def create_menu(root, text_area, current_file):
    menu = tk.Menu(root)
    root.config(menu=menu)

    #File Menu
    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New File", command=lambda: new_file(
        text_area, current_file, root))
    file_menu.add_command(label="Open File", command=lambda: open_file(
        text_area, current_file, root))
    file_menu.add_command(
        label="Save File", command=lambda: save_file(text_area, current_file))
    file_menu.add_command(label="Open Folder",
                          command=lambda: open_folder(tree, folder_name_label))
    file_menu.add_command(label="Save File As",
                          command=lambda: save_file_as(text_area, current_file))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: exit_editor(
        root, text_area, current_file))
    

    # Edit Menu
    edit_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Copy", command=lambda: copy_line(text_area))
    edit_menu.add_command(label="Cut", command=lambda: cut_line(text_area))
    edit_menu.add_command(label="Paste", command=lambda: paste_line(text_area))
    edit_menu.add_separator()
    edit_menu.add_command(label="Undo", command=lambda: undo_function(text_area))
    edit_menu.add_command(label="Redo", command=lambda: redo_function(text_area))

    # Additional platform-specific configuration for macOS
    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        root.createcommand('::tk::mac::Quit', lambda: exit_editor(
            root, text_area, current_file))
        # Ensure the app name appears correctly in the menu bar
        root.createcommand('tk::mac::ShowPreferences', lambda: None)

class TerminalApp:
    def __init__(self, terminal_area, scrollbar):
        self.terminal_area = terminal_area
        self.scrollbar = scrollbar
        self.terminal_area.bind("<Return>", self.enter_command)
        self.command_queue = []
        self.command_lock = threading.Lock()
        
        sys = check_system()
        if sys == "Windows":
            self.process = subprocess.Popen(['powershell'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, text=True, bufsize=1)
        elif sys == "Darwin":
            self.process = subprocess.Popen(['zsh'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, text=True, bufsize=1)
        elif sys == "Linux":
            self.process = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, text=True, bufsize=1)

        self.read_thread = threading.Thread(target=self.read_output)
        self.read_thread.daemon = True
        self.read_thread.start()

    def read_output(self):
        while True:
            output = self.process.stdout.readline()
            if output:
                self.terminal_area.insert(tk.END, output)
                self.terminal_area.see(tk.END)
                self.scrollbar.set(1.0, 1.0)  # Automatically scroll to the bottom
            else:
                break

    def enter_command(self, event):
        command = self.terminal_area.get("end-2l", "end-1c").strip() + "\n"
        self.process.stdin.write(command)
        self.process.stdin.flush()
        self.terminal_area.insert(tk.END, command)
        self.terminal_area.see(tk.END)
        self.scrollbar.set(1.0, 1.0)  # Automatically scroll to the bottom
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Basic Code Editor")

    # Set the application to maximize
    root.state('zoomed')

    # Main PanedWindow
    main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    main_pane.pack(fill=tk.BOTH, expand=1)

    # Left Frame for file and folder viewer
    left_frame = tk.Frame(main_pane, width=300)
    left_frame.pack(fill=tk.Y, expand=0)
    main_pane.add(left_frame)

    # Add label for File Explorer
    file_explorer_label = tk.Label(left_frame, text="File Explorer")
    file_explorer_label.pack(anchor='w')

    # Add label for opened folder name
    folder_name_label = tk.Label(left_frame, text="Opened Folder: None")
    folder_name_label.pack(anchor='w')

    # Add Treeview for file and folder viewer
    tree = Treeview(left_frame)
    tree.pack(fill=tk.BOTH, expand=1)

    # Middle PanedWindow for open files and text editor
    middle_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL)
    middle_pane.pack(fill=tk.BOTH, expand=1)
    main_pane.add(middle_pane)

    # Top Frame for open files
    top_frame = tk.Frame(middle_pane, height=30)
    top_frame.pack(fill=tk.X, expand=0)
    middle_pane.add(top_frame)

    # Add a label to simulate open files (you can replace this with your logic)
    open_files_label = tk.Label(top_frame, text="Open Files: file1.txt, file2.py")
    open_files_label.pack(side=tk.LEFT, padx=10)

    # Text area for code editing
    text_area = scrolledtext.ScrolledText(middle_pane, wrap=tk.WORD, undo=True)
    text_area.pack(fill=tk.BOTH, expand=1)
    middle_pane.add(text_area)

    # Bottom Frame for terminal/output area
    bottom_frame = tk.Frame(middle_pane, height=150)
    bottom_frame.pack(fill=tk.X, expand=0)
    middle_pane.add(bottom_frame)

    # Add label for Terminal/Output
    terminal_label = tk.Label(bottom_frame, text="Terminal/Output")
    terminal_label.pack(anchor='w')

    # Add a frame to hold terminal_area and its scrollbar
    terminal_frame = tk.Frame(bottom_frame)
    terminal_frame.pack(fill=tk.BOTH, expand=1)

    # Add a scrollbar for the terminal/output
    terminal_scrollbar = tk.Scrollbar(terminal_frame)
    terminal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add a text area for terminal/output
    terminal_area = scrolledtext.ScrolledText(terminal_frame, wrap=tk.WORD, undo=True, height=8, yscrollcommand=terminal_scrollbar.set)
    terminal_area.pack(fill=tk.BOTH, expand=1)

    terminal_scrollbar.config(command=terminal_area.yview)

    # Initialize the TerminalApp
    terminal_app = TerminalApp(terminal_area, terminal_scrollbar)

    # Current file path as a list to allow modifications within functions
    current_file = [None]

    create_menu(root, text_area, current_file)

    root.mainloop()
    