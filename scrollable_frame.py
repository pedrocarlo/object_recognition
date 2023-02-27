import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create a canvas and add it to the frame
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg='red')
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar and add it to the frame
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas and add it to the canvas
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind the canvas to the function that adjusts the size of the inner frame
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Bind the canvas to the function that allows scrolling with the mouse wheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Set initial canvas height to 0
        self.canvas_height = 0

    def on_canvas_configure(self, event):
        # Configure the inner frame to have the same width as the canvas
        self.canvas.itemconfigure(self.inner_frame_id, width=event.width)

        # Resize the canvas scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # If the inner frame is taller than the canvas, resize the canvas to fit the inner frame
        if self.inner_frame.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.configure(height=self.inner_frame.winfo_reqheight())
        else:
            # Reset canvas height to zero if inner frame is smaller
            if self.canvas_height != 0:
                self.canvas_height = 0
                self.canvas.configure(height=0)
            else:
                self.canvas.configure(width=event.width)

        # Update the id of the inner frame to ensure the new size is saved
        self.inner_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")


# # Create the root window
# root = tk.Tk()
# root.geometry("400x400")
#
# # Create a scrollable frame and add it to the root window
# scrollable_frame = ScrollableFrame(root)
# scrollable_frame.pack(fill="both", expand=True)
#
# # Create a large number of labels and add them to the inner frame of the scrollable frame
# for i in range(100):
#     label = ttk.Label(scrollable_frame.inner_frame, text=f"Label {i}")
#     label.pack()
#
# # Run the Tkinter event loop
# root.mainloop()
