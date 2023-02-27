from functools import partial

import vlc
import os
from tkinter import *
import tkinter.ttk as ttk
from scrollable_frame import ScrollableFrame
from tkinter import filedialog, messagebox

CWD = os.getcwd()
MRL = r"C:\Users\Pedro Muniz\Desktop\object_detection\runs\detect\predict\test.mp4"
icons_path = CWD + '\\icons\\'
test_meta = CWD + '\\runs/detect/predict/out_video_meta.txt'


class VideoPlayer(Frame):
    def __init__(self, mrl, *args, **kwargs):
        super(VideoPlayer, self).__init__(*args, **kwargs)
        self.is_player_paused = False
        self.is_player_active = False
        self.button_frame = Frame(self, bd=1)
        self.mrl = mrl

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
        self.player.set_mrl(self.mrl)
        self.player.play()
        self.is_player_active = True

    def play(self):
        if self.is_player_paused or not self.is_player_active:
            self.player.play()
            self.is_player_paused = False
            self.is_player_active = True

    def pause(self):
        if not self.is_player_paused and self.is_player_active:
            self.player.pause()
            self.is_player_paused = True


class FileSelector(Frame):
    def __init__(self, *args, **kwargs):
        super(FileSelector, self).__init__(*args, **kwargs)


class Timeline(Frame):
    def __init__(self, player, metadata, *args, **kwargs):
        super(Timeline, self).__init__(*args, **kwargs)
        # self.scroll_frame = ScrollableFrame(self)
        self.player = player
        self.metadata = metadata

        self.tree = ttk.Treeview(self, height=3)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=[None, 15])
        style.configure("Treeview", font=[None, 12])

        self.tree.heading('#0', text="Classes Identified", anchor='w')

        self.update_meta(self.metadata)


        self.tree.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        # xsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<ButtonRelease-1>', self.select_item)
        self.bind("<Configure>", self.on_timeline_configure)

    def select_item(self, a):
        curItem = self.tree.focus()
        time = self.tree.item(curItem)["values"]
        if time:
            self.player.set_time(time[0] * 1000)
            self.player.play()

    def on_timeline_configure(self, event):
        height = self.winfo_height()
        desired_height = (height - 26) // 20
        self.tree.configure(height=desired_height)

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

    def update_meta(self, metadata):
        self.metadata = metadata
        # delete all items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.labels_dict = self.read_meta()
        self.labels = list(self.labels_dict.keys())
        self.times = list(self.labels_dict.values())
        self.item_count = 0

        for i in range(len(self.labels)):
            parent = self.tree.insert('', 'end', text=self.labels[i], open=False)
            self.item_count += 1
            for j in range(len(self.times[i])):
                child = self.tree.insert(parent, 'end', text=str(self.times[i][j]), values=self.times[i][j], open=False)
                self.item_count += 1


def choose_file(timeline: Timeline):
    video_extensions = ["*.mp4", "*.mkv", "*.mov", "*.avi", "*.dav"]
    text_extensions = ["*.txt"]
    files = filedialog.askopenfilenames(initialdir=CWD, title="Select 1 Video file and 1 Metadata file",
                                        filetypes=(
                                        ("video and metadata.txt files", ";".join(video_extensions + text_extensions)),
                                        ("all files", "*.*")))
    video, metadata = None, None
    video_extensions = tuple(map(lambda x: x[1:], video_extensions))
    text_extensions = tuple(map(lambda x: x[1:], text_extensions))
    for file in files:
        if file.lower().endswith(video_extensions):
            video = file
        elif file.lower().endswith(text_extensions):
            metadata = file
    if not video:
        messagebox.showerror("Incorrect Video Filetype Error",
                             f"Please the choose correct filetypes for the video files: "
                             f"{video_extensions}")
        return
    if not metadata:
        messagebox.showerror("Incorrect Metadata Filetype Error",
                             f"Please the choose correct filetypes for the metadata files: "
                             f"{text_extensions}")
        return
    timeline.player.set_mrl(video)
    timeline.update_meta(metadata)
    timeline.player.play()


root = Tk()
root.geometry("1200x760")
root.columnconfigure(0, weight=1)
# root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
mainframe = VideoPlayer(MRL, root)
mainframe.grid(row=0, column=0, sticky=NSEW)
# mainframe.pack(side=LEFT, fill=BOTH, expand=True)
files_frame = Frame(root)
files_frame.rowconfigure(0, weight=1)

timeline = Timeline(mainframe.player, test_meta, master=files_frame)
files_frame.grid(row=0, column=1, padx=2, sticky=NSEW)
timeline.grid(row=0, sticky=NS)
file_button = Button(files_frame, text="Choose File and Metadata", command=partial(choose_file, timeline))
file_button.grid(row=1, pady=2)

root.mainloop()
