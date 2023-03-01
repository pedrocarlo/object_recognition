from functools import partial

import vlc
import os
from math import floor, ceil
from tkinter import *
import tkinter.ttk as ttk
from scrollable_frame import ScrollableFrame
from tkinter import filedialog, messagebox

CWD = os.getcwd()
MRL = r"C:\Users\Pedro Muniz\Desktop\object_detection\runs\detect\predict\test.mp4"
icons_path = CWD + '\\icons\\'
test_meta = CWD + '\\runs/detect/predict/out_video_meta.txt'


def time_calc(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return hours, minutes, seconds


class VideoPlayer(Frame):
    def __init__(self, mrl, *args, **kwargs):
        super(VideoPlayer, self).__init__(*args, **kwargs)
        self.is_player_paused = False
        self.button_frame = Frame(self, bd=1)
        self.mrl = mrl

        self.play_button = Button(self.button_frame, command=self.play, text="Play")
        self.pause_button = Button(self.button_frame, command=self.pause, text="Pause/Stop")
        # self.stop_button = Button(self.button_frame, command=self.stop, text="Stop")
        # self.play_icon = PhotoImage(icons_path + 'play.png', text)
        # self.pause_icon = PhotoImage(icons_path + 'pause.png')

        self.canvas = Canvas(self)

        self.vlcInstance = vlc.Instance("--network-caching=2000")
        self.player = self.vlcInstance.media_player_new()
        win_id = self.canvas.winfo_id()
        self.player.set_hwnd(win_id)
        self.player.set_mrl(self.mrl)
        self.player.play()
        self.wait_player()
        self.timeline = Timeline(self, self)
        self.play()

        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        self.canvas.grid(row=0, sticky=NSEW)
        self.button_frame.grid(row=2, sticky=NSEW)
        self.timeline.grid(row=1, sticky=NSEW)

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.play_button.grid(row=0, column=0, sticky=EW)
        self.pause_button.grid(row=0, column=1, sticky=EW)

        self.timeline.bind("<Configure>", self.timeline_configure)
        self.timeline.bind("<Leave>", self.on_mouse_leave)

    def play(self):
        self.player.play()
        self.is_player_paused = False
        ended = 6
        if self.player.get_state().value == ended:
            self.player.stop()
            self.player.play()
        self.wait_player()
        # ask timeline to track time
        self.track_time()

    def pause(self):
        self.player.pause()
        self.is_player_paused = True

    def track_time(self):
        if not self.is_player_paused and self.player.is_playing():
            self.timeline.track_player_time()
            self.after(200, self.track_time)

    def timeline_configure(self, event):
        timeline = self.timeline
        timeline.configure(height=self.winfo_height() // 10)
        self.timeline.delete("all")
        timeline.draw_timeline(self.player.get_length() // 1000)
        # Redraw

    def on_mouse_leave(self, event):
        self.timeline.track_player_time()

    def wait_player(self):
        while not self.player.is_playing():
            pass
        return

    def create_player(self):
        self.player = self.vlcInstance.media_player_new()
        win_id = self.canvas.winfo_id()
        self.player.set_hwnd(win_id)
        self.player.set_mrl(self.mrl)
        self.player.play()
        self.wait_player()


class Timeline(Canvas):
    def __init__(self, player: VideoPlayer, *args, **kwargs):
        super(Timeline, self).__init__(*args, **kwargs)
        self.tot_width = 1
        self.tot_height = 1
        self.video_widget = player
        self.padding_x = 20
        self.divisor = 24
        self.last_x = 0
        self.bind("<Motion>", self.track_mouse_time)
        self.after(1000, self.track_player_time)
        self.bind("<ButtonRelease-1>", self.change_time)

    # Time in seconds
    def draw_timeline(self, total_time):
        width, height = self.winfo_width() - self.padding_x, self.winfo_height()
        # Find width that is divisible by 10
        while width % self.divisor != 0:
            width -= 1
        self.tot_width, self.tot_height = width, height
        width += self.padding_x
        x_c, y_c = self.padding_x, height // 2
        self.create_line(x_c, y_c, width, y_c, fill="green", width=5)
        # draw 10 spaced bars
        step = width // self.divisor
        bar_height = height // 7
        minute_step = step // 5
        count = 0
        for x in range(x_c, width + 1, step):
            self.create_line(x, y_c - bar_height, x, y_c + bar_height)
            hours, minutes, seconds = time_calc((total_time // self.divisor) * count)
            self.create_text(x, y_c + bar_height + 5, text=f"{hours}:{minutes:02}:{seconds:02}")
            count += 1
            # for x2 in range(x, x + step, minute_step):
            #     self.create_line(x2, y_c - bar_height // 2, x2, y_c + bar_height // 2)
        # draw cursor for timeline
        self.last_x = step * self.divisor + 1 + x_c
        self.draw_cursor(self.padding_x, None)

    def draw_cursor(self, x, curr_time):
        self.delete("cursor", "cursor_text")  # delete cursor
        cursor_height = self.tot_height // 4
        y = self.tot_height // 2
        total_time = self.video_widget.player.get_length() // 1000
        if x is None:
            percent = curr_time / total_time
            x = self.padding_x + int(percent * self.tot_width)
        if curr_time is None:
            percent = (x - self.padding_x) / self.tot_width
            curr_time = int(percent * total_time)
        self.create_line(x, y - cursor_height, x, y + cursor_height, fill="red", width=2, tags="cursor")
        hours, minutes, seconds = time_calc(curr_time)
        self.create_text(x, y - cursor_height - 5, text=f"{hours}:{minutes:02}:{seconds:02}", tags="cursor_text")

    def track_mouse_time(self, event):
        x, y = event.x, event.y
        if self.padding_x <= x < self.last_x:
            self.draw_cursor(x, None)
        else:
            self.track_player_time()

    def track_player_time(self):
        # find root
        curr_time = self.video_widget.player.get_time() // 1000
        self.draw_cursor(None, curr_time)

    def change_time(self, event):
        x = event.x
        if self.padding_x <= x < self.last_x:
            total_time = self.video_widget.player.get_length()
            percent = (x - self.padding_x) / self.tot_width
            curr_time = int(percent * total_time)
            self.video_widget.player.set_time(curr_time)
            self.video_widget.play()

    # bind events for B1-Motion when browsing through the timeline with mouse button pressed down
    # bind events for Mouse motion in timeline when you just want to check the time in the timeline


class ClassTimeline(Frame):
    def __init__(self, player, metadata, *args, **kwargs):
        super(ClassTimeline, self).__init__(*args, **kwargs)
        # self.scroll_frame = ScrollableFrame(self)
        self.video_widget = player
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
        self.bind("<Configure>", self.on_class_list_configure)

    def select_item(self, a):
        curItem = self.tree.focus()
        time = self.tree.item(curItem)["values"]
        if time:
            self.video_widget.player.set_time(time[0] * 1000)
            self.video_widget.play()

    def on_class_list_configure(self, event):
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
        tot_time = self.video_widget.player.get_length() // 1000
        for label, times in labels_dict.items():
            times = list(times)
            times.sort(key=lambda x: int(x))
            start = int(times[0]) // 1000  # value is now in seconds
            prev = start
            curr = start
            interval = [curr]
            intervals = [interval]
            diff_triggered = False
            for i in range(1, len(times)):
                diff_triggered = False
                curr = int(times[i]) // 1000
                diff = curr - prev
                if diff > 1:
                    diff_triggered = True
                    interval = []
                    intervals.append(interval)
                prev = curr
                interval.append(prev)
            # TODO correct ending here as I think it is not quite correct
            if not diff_triggered:
                interval.append(tot_time)
            for i in range(len(intervals)):
                interval = intervals[i]
                intervals[i] = [interval[0], interval[-1]]
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


def choose_file(class_widget: ClassTimeline):
    video_extensions = ["*.mp4", "*.mkv", "*.mov", "*.avi", "*.dav"]
    text_extensions = ["*.txt"]
    files = filedialog.askopenfilenames(initialdir=CWD, title="Select 1 Video file and 1 Metadata file",
                                        filetypes=(
                                            ("video and metadata.txt files",
                                             ";".join(video_extensions + text_extensions)),
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
    class_widget.video_widget.player.set_mrl(video)
    class_widget.update_meta(metadata)
    class_widget.video_widget.play()


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

class_list = ClassTimeline(mainframe, test_meta, master=files_frame)
files_frame.grid(row=0, column=1, padx=2, sticky=NSEW)
class_list.grid(row=0, sticky=NS)
file_button = Button(files_frame, text="Choose File and Metadata", command=partial(choose_file, class_list))
file_button.grid(row=1, pady=2)
mainframe.timeline.update()
# mainframe.timeline.draw_timeline(1000)
root.mainloop()
