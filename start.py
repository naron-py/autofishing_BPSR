# start.py
import threading
import tkinter as tk

from auto_mine import run_auto_mine
from main import run_auto_fish

class BotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Bot Controller")
        self.root.resizable(False, False)

        self.current_task = None
        self.thread = None
        self.stop_event = None

        self.status_var = tk.StringVar(value="Status: Idle")

        container = tk.Frame(root, padx=16, pady=16)
        container.pack()

        tk.Label(container, text="Auto Fish", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.start_fish_btn = tk.Button(container, text="Start", width=12, command=self.start_fish)
        self.start_fish_btn.grid(row=1, column=0, padx=(0, 8), pady=6)
        self.stop_fish_btn = tk.Button(container, text="Stop", width=12, command=self.stop_fish, state=tk.DISABLED)
        self.stop_fish_btn.grid(row=1, column=1, padx=(0, 8), pady=6)

        tk.Label(container, text="Auto Mine", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.start_mine_btn = tk.Button(container, text="Start", width=12, command=self.start_mine)
        self.start_mine_btn.grid(row=3, column=0, padx=(0, 8), pady=6)
        self.stop_mine_btn = tk.Button(container, text="Stop", width=12, command=self.stop_mine, state=tk.DISABLED)
        self.stop_mine_btn.grid(row=3, column=1, padx=(0, 8), pady=6)

        tk.Label(container, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(200, self.check_thread)

    def set_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def update_buttons(self):
        is_running = self.thread is not None and self.thread.is_alive()
        self.start_fish_btn.config(state=tk.NORMAL if not is_running else tk.DISABLED)
        self.start_mine_btn.config(state=tk.NORMAL if not is_running else tk.DISABLED)

        if self.current_task == "fish" and is_running:
            self.stop_fish_btn.config(state=tk.NORMAL)
            self.stop_mine_btn.config(state=tk.DISABLED)
        elif self.current_task == "mine" and is_running:
            self.stop_fish_btn.config(state=tk.DISABLED)
            self.stop_mine_btn.config(state=tk.NORMAL)
        else:
            self.stop_fish_btn.config(state=tk.DISABLED)
            self.stop_mine_btn.config(state=tk.DISABLED)

    def start_task(self, task_name, target):
        if self.thread is not None and self.thread.is_alive():
            self.set_status("Status: Stop the current task first.")
            return

        self.current_task = task_name
        self.stop_event = threading.Event()
        self.set_status(f"Status: Starting {task_name}...")

        def runner():
            try:
                target(self.stop_event)
            finally:
                self.set_status("Status: Idle")

        self.thread = threading.Thread(target=runner, daemon=True)
        self.thread.start()
        self.update_buttons()

    def start_fish(self):
        self.start_task("fish", run_auto_fish)

    def start_mine(self):
        self.start_task("mine", run_auto_mine)

    def stop_current(self):
        if self.stop_event is not None:
            self.set_status("Status: Stopping...")
            self.stop_event.set()

    def stop_fish(self):
        if self.current_task == "fish":
            self.stop_current()

    def stop_mine(self):
        if self.current_task == "mine":
            self.stop_current()

    def check_thread(self):
        if self.thread is not None and not self.thread.is_alive():
            self.thread = None
            self.stop_event = None
            self.current_task = None
        self.update_buttons()
        self.root.after(200, self.check_thread)

    def on_close(self):
        self.stop_current()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BotUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
