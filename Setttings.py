import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import cv2
import PIL.ImageTk


# pass tk.Tk()
WIDTH = 854
HEIGHT = 480

def get_result(app, win, input_str):
    app.delay = int(float(input_str.get()))
    win.destroy()
    app.isStop = False


def modify_delay(app):
    app.isStop = True
    win = tk.Toplevel()
    win.wm_title("Mode Detail")

    label = ttk.Label(win, text="Input Delay Duration")
    label.grid(row=0, column=0)
    input_string = tk.StringVar()
    entry = ttk.Entry(win, text="Input", textvariable=input_string)
    entry.grid(row=1, column=0)

    b = ttk.Button(win, text="Okay", command=lambda: get_result(app, win, input_string))
    b.grid(row=2, column=0)


def Exit(app):
    app.window.destroy()


def OpenFile(app):
    ftypes = [('Video files', '*.mp4'), ('All files', '*')]
    dlg = tk.filedialog.Open(app.window, filetypes=ftypes)
    filename = dlg.show()
    app.vid = MyVideo(filename)
    # Create a canvas that can fit the above video source size
    app.canvas = tk.Canvas(app.window, width=WIDTH, height=HEIGHT)
    app.canvas.place(relx=0.12, rely=0.05)
    app.histogramR = tk.Label(app.window)
    app.histogramR.place(relx=0, rely=0)

    app.histogramG = tk.Label(app.window)
    app.histogramG.place(relx=0, rely=0.3)
    app.histogramB = tk.Label(app.window)
    app.histogramB.place(relx=0, rely=0.6)
    app.delay = 20
    app.btn_pin.configure(state="normal")
    app.btn_stop.configure(state="normal")
    app.btn_save.configure(state="normal")
    app.btn_complete.configure(state="normal")
    app.isInit = True
    app.stop()
    ret, frame = app.vid.get_frame()
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    if ret:
        app.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        app.canvas.create_image(0, 0, image=app.photo, anchor=tk.NW)
    app.update()


class MyVideo:
    def __init__(self, video_source):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return False, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
