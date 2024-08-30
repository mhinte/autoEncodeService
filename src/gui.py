import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time

from src.helper.constants import LOG_PATH


# Function to start the script
def start_script():
    global running
    if not running:
        running = True
        update_status_dot("green")  # Update status dot to green
        add_to_log("Script started...\n")
        threading.Thread(target=run_script).start()
    else:
        messagebox.showinfo("Information", "The script is already running.")

# Function to stop the script
def stop_script():
    global running
    if running:
        running = False
        update_status_dot("red")  # Update status dot to red
        add_to_log("Script stopped.\n")

# Dummy function to simulate the script running
def run_script():
    while running:
        add_to_log("The script is running...\n")
        time.sleep(2)  # Simulate work
    add_to_log("The script has stopped running.\n")

# Function to select a folder
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder_selected)

# Function to update the status dot color
def update_status_dot(color):
    canvas.itemconfig(status_dot, fill=color)

# Function to add text to the log
def add_to_log(message):
    log_text.insert(tk.END, message)
    log_text.see(tk.END)  # Automatically scroll to the end of the log


def get_log():
    with open("../" + LOG_PATH) as log:
        return log.read()


def main():
    global root, log_text, running, path_entry, canvas, status_dot

    # Main application window
    root = tk.Tk()
    root.title("AutoEncoder")

    running = False

    tab_control = ttk.Notebook(root)

    control_tab = ttk.Frame(tab_control)
    log_tab = ttk.Frame(tab_control)

    tab_control.add(control_tab, text='Control')
    tab_control.add(log_tab, text='Log')

    tab_control.pack(expand=1, fill="both")

    # Start and Stop buttons
    start_button = ttk.Button(control_tab, text="Start", command=start_script)
    start_button.grid(row=2, column=0, padx=5, pady=5)

    stop_button = ttk.Button(control_tab, text="Stop", command=stop_script)
    stop_button.grid(row=2, column=1, padx=5, pady=5)

    # Status indicator canvas
    canvas = tk.Canvas(control_tab, width=20, height=20, highlightthickness=0)
    canvas.grid(row=2, column=2, padx=5, pady=5)
    status_dot = canvas.create_oval(5, 5, 15, 15, fill='red')  # Initial color is red


    path_label = ttk.Label(control_tab, text="Path to Watch Folder:")
    path_label.grid(row=0, column=0, padx=5, pady=5)

    path_entry = ttk.Entry(control_tab, width=50)
    path_entry.grid(row=0, column=1, padx=5, pady=5)

    path_button = ttk.Button(control_tab, text="Select", command=select_folder)
    path_button.grid(row=0, column=2, padx=5, pady=5)


    log_text = tk.Text(log_tab, wrap='word', height=15)
    log_text.insert(tk.END, get_log())
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    log_scrollbar = ttk.Scrollbar(log_tab, orient='vertical', command=log_text.yview)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text['yscrollcommand'] = log_scrollbar.set

    # Center the control_frame
    root.update_idletasks()

    # Start Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()