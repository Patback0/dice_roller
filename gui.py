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

    # Main frame to hold all widgets
    main_frame = tk.Frame(root, bg='#0a0000')
    main_frame.pack(expand=True)

    # Task Points Label
    label_var1 = tk.Label(main_frame, text=f"Task Points: {dr.task_points}/20", font=('Arial', 36), fg='white', bg='black')
    label_var1.pack(pady=10)

    # Dice Points Label
    label_var2 = tk.Label(main_frame, text=f"Dice Points: {dr.dice_points}", font=('Arial', 36), fg='white', bg='black')
    label_var2.pack(pady=10)

    # Frame to hold past rolls
    past_rolls_frame = tk.Frame(main_frame, bg='#0a0000')
    past_rolls_frame.pack(pady=20)

    # Title for Past Rolls
    past_rolls_title = tk.Label(past_rolls_frame, text="Past Rolls:", font=('Arial', 24), fg='white', bg='#0a0000')
    past_rolls_title.pack()

    # Sub-frame to hold roll counters horizontally
    roll_counters_frame = tk.Frame(past_rolls_frame, bg='#0a0000')
    roll_counters_frame.pack(pady=10)

    # Dictionary to store roll number labels
    roll_labels = {}

    # Function to update past rolls display
    def update_past_rolls():
        # Update existing labels or create new ones if necessary
        for number, count in dr.past_rolls.items():
            if number in roll_labels:
                roll_labels[number].config(text=f"{number}: {count}")
            else:
                roll_counter = tk.Label(roll_counters_frame, text=f"{number}: {count}", font=('Arial', 18), fg='white', bg='#333', padx=10, pady=5)
                roll_counter.pack(side=tk.LEFT, padx=5)
                roll_labels[number] = roll_counter

    def update_display():
        label_var1.config(text=f"Task Points: {dr.task_points}/20")
        label_var2.config(text=f"Dice Points: {dr.dice_points}")
        update_past_rolls()
        root.after(1000, update_display)  # update every second

    update_display()
    root.mainloop()

