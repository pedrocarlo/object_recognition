import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create a canvas object and a vertical scrollbar for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Link the scrollbar to the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas which will be scrolled with the scrollbar
        self.scrollable_frame = tk.Frame(self.canvas)

        # Add the scrollbar and the scrollable frame to the main frame
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Set the scrollable frame to expand with the canvas
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

        # Bind mousewheel to scroll canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event):
        # Update the scroll region to match the size of the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        # On mousewheel event scroll one unit
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

if __name__ == "__main__":

    root = tk.Tk()

    scrollable_frame = ScrollableFrame(root)
    scrollable_frame.pack(fill="both", expand=True)

    for i in range(50):
        tk.Label(scrollable_frame.scrollable_frame, text=f"Label {i}").pack()

    root.mainloop()
