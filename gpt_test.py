import tkinter as tk
from scrollable_frame import ScrollableFrame

root = tk.Tk()

# Create a main frame to hold the ScrollableFrame and other widgets
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Create a ScrollableFrame with some widgets inside
scrollable_frame = ScrollableFrame(main_frame)
scrollable_frame.pack(fill="both", expand=True)

for i in range(20):
    label = tk.Label(scrollable_frame.scrollable_frame, text=f"Label {i}")
    label.pack(padx=20, pady=10, fill="both", expand=True)

# Add some other widgets below the ScrollableFrame
button = tk.Button(main_frame, text="Click me")
button.pack(side="right", padx=10, pady=10)

root.mainloop()
