import vlc
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from typing import Iterable
from test import ScrollableFrame

CWD = os.getcwd()
MRL = r"C:\Users\Pedro Muniz\Desktop\object_detection\runs\detect\predict\test.mp4"
icons_path = CWD + '\\icons\\'
test_meta = CWD + '\\out_video_meta.txt'


class ScrollFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # create a frame (self)

        self.canvas = tk.Canvas(self, bg='yellow')  # place canvas on self
        self.viewPort = tk.Frame(self)  # place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)  # place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)  # attach scrollbar action to scroll of canvas

        # self.vsb.pack(side=RIGHT, fill=Y)  # pack scrollbar to right of self
        # self.viewPort.pack()
        self.canvas.pack()  # pack canvas to left of self and expand to fil
        self.canvas.create_window((0, 0), window=self.viewPort, anchor="nw", tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)  # bind an event whenever the size of the viewPort frame changes.
        # self.bind("<Configure>", self.onCanvasConfigure)  # bind an event whenever the size of the canvas frame changes.

        self.bind_all('<MouseWheel>', self.onMouseWheel)

        self.onFrameConfigure(None)  # perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)  # whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):  # cross platform scroll wheel event
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def onEnter(self, event):  # bind wheel events when the cursor enters the control
        self.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):  # unbind wheel events when the cursorl leaves the control
        self.unbind_all("<MouseWheel>")

class VideoPlayer(Frame):
    def __init__(self, *args, **kwargs):
        super(VideoPlayer, self).__init__(*args, **kwargs)
        self.is_player_paused = False
        self.is_player_active = False
        self.button_frame = Frame(self, bg="red", bd=1)

    def setup(self):
        # TODO find a way to remove space between buttons and player
        self.play_button = Button(self.button_frame, command=self.play, text="Play")
        self.pause_button = Button(self.button_frame, command=self.pause, text="Pause/Stop")
        # self.stop_button = Button(self.button_frame, command=self.stop, text="Stop")
        # self.play_icon = PhotoImage(icons_path + 'play.png', text)
        # self.pause_icon = PhotoImage(icons_path + 'pause.png')

        self.canvas = Canvas(self)

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        self.canvas.grid(row=0, sticky=NSEW)
        self.button_frame.grid(row=1, sticky=NSEW)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.play_button.grid(row=0, column=0, sticky=EW)
        self.pause_button.grid(row=0, column=1, sticky=EW)

        self.vlcInstance = vlc.Instance("--network-caching=2000")
        self.player = self.vlcInstance.media_player_new()
        win_id = self.canvas.winfo_id()
        self.player.set_hwnd(win_id)
        self.player.set_mrl(MRL)
        self.player.play()
        self.is_player_active = True

    def stop(self):
        self.player.stop()
        self.is_player_active = False

    def play(self):
        if self.is_player_paused or not self.is_player_active:
            self.player.play()
            self.is_player_paused = False
            self.is_player_active = True

    def pause(self):
        if not self.is_player_paused and self.is_player_active:
            self.player.pause()
            self.is_player_paused = True
        elif self.is_player_paused and self.is_player_active:
            self.stop()


class FileSelector(Frame):
    def __init__(self, *args, **kwargs):
        super(FileSelector, self).__init__(*args, **kwargs)


class TimeLine(Frame):
    def __init__(self, player, metadata, *args, **kwargs):
        super(TimeLine, self).__init__(*args, **kwargs)
        self.scroll_frame = ScrollFrame(self)
        self.player = player
        self.metadata = metadata
        self.labels_dict = self.read_meta()
        self.ungrided = set()
        self.listbox_list = []
        self.frames = self.label_organizer()
        # TODO set scrollbars on the frame with labels and the listboxes
        self.scroll_frame.pack()
        for frame in self.frames:
            frame.pack()

        # TODO make labels as part of a listbox and time intervals as part of listbox as well then labels can be

    #  clicked to minimize/hide their time intervals listbox
    def label_organizer(self):
        frames = []
        labels = list(self.labels_dict.keys())
        times = list(self.labels_dict.values())
        for i in range(len(labels)):
            var = StringVar()
            var.set(times[i])  # TODO Change times to be in format h:m:s instead of seconds
            frame = Frame(self.scroll_frame)
            curr_listbox = Listbox(frame, listvariable=var, selectmode='single')  # check add callback to listbox
            label = labels[i]
            label_object = Label(frame, text=label)
            label_object.bind("<Button-1>", lambda x, j=i: self.toggle_listbox(x, j))
            label_object.pack()
            curr_listbox.pack()
            curr_listbox.pack_forget()
            curr_listbox.bind('<<ListboxSelect>>', self.change_player_time)
            self.ungrided.add(label)
            self.listbox_list.append(curr_listbox)
            frames.append(frame)
        return frames

    def change_player_time(self, event):
        lb = event.widget
        time = lb.get(lb.curselection()[0])[0]
        self.player.play()
        self.player.set_time(time * 1000)
        self.player.play()

    # use widget.winfo_viewable to check if it is viewable
    def toggle_listbox(self, event, index):
        label = event.widget['text']
        listbox = self.listbox_list[index]
        if label not in self.ungrided:
            listbox.pack_forget()
            self.ungrided.add(label)
        else:
            listbox.pack()
            self.ungrided.remove(label)

    def read_meta(self):
        meta = open(self.metadata, 'r')
        lines = meta.readlines()
        # self.label_times = dict()
        labels_dict = dict()
        # TODO not very efficient as it goes line per line when it would be better to go every second e.g. 30 frames/s
        for line in lines:
            line = line.strip('\n')
            args = line.split(' ')
            milli_seconds = args[0]
            labels = args[1:]
            for label in labels:
                if label not in labels_dict:
                    labels_dict[label] = set()
                labels_dict[label].add(
                    milli_seconds)  # will probably add same time 30 times per seconds. Many repeated calls
        new_labels_dict = dict()
        for label, times in labels_dict.items():
            times = list(times)
            times.sort(key=lambda x: int(x))
            # print(label)
            # print(times)
            start = int(times[0]) // 1000  # value is now in seconds
            prev = start
            curr = start
            intervals = []
            for i in range(1, len(times)):
                curr = int(times[i]) // 1000
                diff = curr - prev
                if diff > 1:
                    old_interval = (start, prev)
                    intervals.append(old_interval)
                    start = curr
                prev = curr
            intervals.append((start, None))  # None represents that it did not find an end interval
            new_labels_dict[label] = intervals

        meta.close()
        return new_labels_dict




root = Tk()
root.geometry("900x550")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe = VideoPlayer(root)
mainframe.setup()
mainframe.grid(row=0, column=0, sticky=NSEW)
timeline = TimeLine(mainframe.player, test_meta, master=root, bg="red")
timeline.grid(row=0, column=1, padx=5, pady=5, sticky=NS)

root.mainloop()
