import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import json
import sys
import install_pkg
import io

# Paths and config
CONFIG_FILE = Path(__file__).parent / "config.json"
RESOURCE_DIR = Path(__file__).parent
TSV_DIR = RESOURCE_DIR / "tsv"

# Setup TSV paths relative to script
install_pkg.TSV_FILES = {
    'games': TSV_DIR / "PSV_GAMES.tsv",
    'dlcs': TSV_DIR / "PSV_DLCS.tsv",
    'themes': TSV_DIR / "PSV_THEMES.tsv"
}

# Config I/O
def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_config(pkg_path, exe_path):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"pkg_path": pkg_path, "vita3k_exe": exe_path}, f)

# Log redirection class
class TextRedirector(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass  # Required for Python 3 compatibility

# GUI functions
def select_pkg_folder():
    path = filedialog.askdirectory(title="Select PKG Folder")
    if path:
        pkg_path_var.set(path)

def select_vita3k_exe():
    path = filedialog.askopenfilename(
        title="Select Vita3K Executable",
        filetypes=[("Executable Files", "*.exe" if is_windows else "*")]
    )
    if path:
        exe_path_var.set(path)

def start_installation():
    pkg_path = pkg_path_var.get()
    exe_path = exe_path_var.get()

    if not pkg_path or not exe_path:
        messagebox.showerror("Missing Info", "Please select both PKG folder and Vita3K executable.")
        return

    # Save config
    save_config(pkg_path, exe_path)

    # Assign paths to script
    install_pkg.INPUT_PKG_FOLDER = str(Path(pkg_path))
    install_pkg.VITA3K_PROG_PATH = str(Path(exe_path))

    try:
        install_pkg.process_pkg_files()
        install_pkg.print_summary()
        messagebox.showinfo("Done", "Installation finished. See logs for details.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# OS check
is_windows = Path().anchor.startswith(('C:', 'D:', 'E:'))

# GUI setup
root = tk.Tk()
root.title("Vita3K PKG Installer")

# Vars
pkg_path_var = tk.StringVar()
exe_path_var = tk.StringVar()

# Load config if exists
cfg = load_config()
pkg_path_var.set(cfg.get("pkg_path", ""))
exe_path_var.set(cfg.get("vita3k_exe", ""))

# Layout
tk.Label(root, text="PKG Folder:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=pkg_path_var, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_pkg_folder).grid(row=0, column=2)

tk.Label(root, text="Vita3K Executable:").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=exe_path_var, width=50).grid(row=1, column=1)
tk.Button(root, text="Browse", command=select_vita3k_exe).grid(row=1, column=2)

tk.Button(root, text="Start Installation", command=start_installation).grid(
    row=2, column=0, columnspan=3, pady=8
)

# Log area
log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25, state=tk.NORMAL)
log_box.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Redirect stdout and stderr
sys.stdout = TextRedirector(log_box)
sys.stderr = TextRedirector(log_box)

root.mainloop()
