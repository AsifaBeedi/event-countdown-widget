import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import json
import os

DATA_FILE = "event_data.json"
BG_COLOR = "#f5f5dc"
TEXT_COLOR = "#013220"

ctk.set_appearance_mode("light")
# Remove theme if it sets default font to Maellen
# ctk.set_default_color_theme("green")  # optional, or keep if you want

def load_event():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

def save_event(name, date_str):
    with open(DATA_FILE, "w") as f:
        json.dump({"event": name, "date": date_str}, f)

def get_days_left(event_date):
    try:
        deadline = datetime.strptime(event_date, "%Y-%m-%d").date()
        today = datetime.today().date()
        return (deadline - today).days
    except Exception as e:
        return None

def prompt_for_event():
    prompt = ctk.CTk()
    prompt.title("Set Countdown")
    prompt.geometry("300x200")

    def save():
        name = name_entry.get()
        date = date_entry.get()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except:
            messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format.")
            return
        save_event(name, date)
        prompt.destroy()
        main()

    ctk.CTkLabel(prompt, text="Event Name:").pack(pady=5)
    name_entry = ctk.CTkEntry(prompt)
    name_entry.pack()

    ctk.CTkLabel(prompt, text="Event Date (YYYY-MM-DD):").pack(pady=5)
    date_entry = ctk.CTkEntry(prompt)
    date_entry.pack()

    ctk.CTkButton(prompt, text="Save", command=save).pack(pady=15)
    prompt.mainloop()

def main():
    data = load_event()
    if not data:
        prompt_for_event()
        return

    days = get_days_left(data["date"])
    if days is None:
        messagebox.showerror("Error", "Invalid date found.")
        return

    msg = f"✨ {days} days to go\nfor {data['event']}!"
    if days < 0:
        msg = f"🎉 {data['event']} is over!"

    app = ctk.CTk()
    app.geometry("300x150")
    app.title("Countdown Widget")
    app.configure(fg_color=BG_COLOR)

    label = ctk.CTkLabel(
        app,
        text=msg,
        font=("Super Dream", 20, "bold"),  # Use only Super Dream here
        text_color=TEXT_COLOR,
        justify="center",
    )
    label.pack(expand=True)

    def reset_event():
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        app.destroy()
        main()

    ctk.CTkButton(app, text="⟳ Reset", command=reset_event).pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    main()
