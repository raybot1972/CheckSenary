import subprocess
import re
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END
from datetime import datetime

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def get_inf_list(provider):
    output = run_cmd("pnputil /enum-drivers")
    blocks = re.findall(r"(Published Name:.*?Attributes:.*?)(?=Published Name:|$)", output, re.DOTALL)
    infs = []
    for block in blocks:
        if f"Provider Name:      {provider}" in block:
            match = re.search(r"Published Name:\s+(oem\d+\.inf)", block)
            if match:
                infs.append(match.group(1))
    return infs

def purge_selected():
    selected = [listbox.get(i) for i in listbox.curselection()]
    if not selected:
        messagebox.showinfo("No Selection", "Please select one or more INF files to purge.")
        return

    log_file = f"DriverPurgeLog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, "w") as log:
        for inf in selected:
            cmd = f"pnputil /delete-driver {inf} /uninstall /force"
            result = run_cmd(cmd)
            log.write(f"Deleted {inf}:\n{result}\n")
    messagebox.showinfo("Purge Complete", f"Deleted {len(selected)} INF(s).\nLog saved to {log_file}")

def refresh_list():
    listbox.delete(0, END)
    infs = get_inf_list(provider_entry.get())
    for inf in infs:
        listbox.insert(END, inf)

# GUI setup
root = tk.Tk()
root.title("Driver Purge Tool")

tk.Label(root, text="Provider Name:").pack()
provider_entry = tk.Entry(root)
provider_entry.insert(0, "Senary")
provider_entry.pack()

tk.Button(root, text="Refresh INF List", command=refresh_list).pack()

frame = tk.Frame(root)
frame.pack()

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = Listbox(frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, width=40, height=10)
listbox.pack(side=tk.LEFT)
scrollbar.config(command=listbox.yview)

tk.Button(root, text="Purge Selected Drivers", command=purge_selected).pack(pady=10)

root.mainloop()