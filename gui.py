import threading
import tkinter as tk

# Tkinter GUI in a separate thread
def start_tkinter_thread(dr):
    if threading.active_count() == 1: 
        tkinter_thread = threading.Thread(target=start_tkinter, args=(dr,))
        tkinter_thread.daemon = True
        tkinter_thread.start()

def start_tkinter(dr):
    root = tk.Tk()
    root.title("Dice Roller")
    root.geometry("1024x600")
    root.configure(bg='#0a0000')

    frame = tk.Frame(root, bg='#0a0000')
    frame.pack(expand=True)

    label_var1 = tk.Label(frame, text=f"Task Points: {dr.task_points}", font=('Arial', 36), fg='white', bg='black')
    label_var1.pack()

    label_var2 = tk.Label(frame, text=f"Dice Points: {dr.dice_points}", font=('Arial', 36),fg='white', bg='black')
    label_var2.pack()

    def update_display():
        label_var1.config(text=f"Task Points: {dr.task_points}")
        label_var2.config(text=f"Dice Points: {dr.dice_points}")
        root.after(1000, update_display) # update every second

    update_display()
    root.mainloop()