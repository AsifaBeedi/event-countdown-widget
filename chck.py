import tkinter as tk
import tkinter.font as tkFont

root = tk.Tk()
fonts = tkFont.families()
fonts = sorted(f.lower() for f in fonts)  # lowercase for easy matching

print("Super Dream present?", any("super" in f for f in fonts))
print("Maellen present?", any("maellen" in f for f in fonts))

root.destroy()  # Close the hidden Tkinter window
