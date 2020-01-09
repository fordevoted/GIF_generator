import tkinter as tk
from tkinter import ttk
import numpy as np

import PIL.Image
import PIL.ImageTk
import Setttings
import Effect
import AddText
import imageio
import pygifsicle
import cv2


class App:
    def __init__(self, window, window_title, video_source):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.isStop = False
        self.isInit = False
        self.isPin = False

        self.vid = None
        self.canvas = None
        self.histogramR = None
        self.histogramG = None
        self.histogramB = None

        self.delay = None
        self.job = None

        self.label_mode = None
        self.data = []

        self.recording_image = None
        self.init_menu_bar()

        # image need to store in tk, then we can change image in button dynamically

        # Create Button
        img_open = PIL.Image.open('./resources/stop32.png')
        self.window.icon_stop = PIL.ImageTk.PhotoImage(img_open)
        self.bn_stop_text = tk.StringVar()
        self.btn_stop = ttk.Button(window, image=self.window.icon_stop, text="Stop", compound="left", width=15,
                                   state='disabled', command=self.stop)
        self.btn_stop.place(relx=0.5, rely=0.90)
        # self.bn_stop_text.set("Stop")

        img_open = PIL.Image.open('./resources/pin32.png')
        icon_pin = PIL.ImageTk.PhotoImage(img_open)
        self.btn_pin = ttk.Button(window, image=icon_pin, text="Pin Start", state='disabled', compound="left", width=15,
                                  command=self.pin)
        self.btn_pin.place(relx=0.25, rely=0.90)

        img_open = PIL.Image.open('./resources/tick24.png')
        icon_complete = PIL.ImageTk.PhotoImage(img_open)
        style = ttk.Style()
        style.configure('C.TButton', padding='0 5 0 5', width=15)
        self.btn_complete = ttk.Button(window, image=icon_complete, text="Complete",
                                       compound="left", style="C.TButton", state='disabled', command=self.complete)
        self.btn_complete.place(relx=0.04, rely=0.90)

        img_open = PIL.Image.open('./resources/save32.png')
        icon_save = PIL.ImageTk.PhotoImage(img_open)
        self.btn_save = ttk.Button(window, image=icon_save, text="Save", compound="left", width=15, state='disabled',
                                   command=self.save)
        self.btn_save.place(relx=0.75, rely=0.90)
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.window.mainloop()

    def stop(self):
        img_open = PIL.Image.open('./resources/play24.png')
        self.window.icon_play = PIL.ImageTk.PhotoImage(img_open)
        self.btn_stop.config(image=self.window.icon_stop, text="Stop", compound="left") if self.isStop \
            else self.btn_stop.config(image=self.window.icon_play, text="Play", compound="left", style='C.TButton')
        self.isStop = not self.isStop
        #    cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def complete(self):
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="#279189", font=("Courier", 18), width=25)
        self.label_mode = ttk.Label(self.window, text="Edit Mode", style="BW.TLabel")
        self.label_mode.place(relx=0.4, rely=0)
        if self.data.__len__() == 0:
            self.label_mode.configure(text="editable data is empty")
            return
        elif self.data.__len__() <= 24:  # edit as photo type
            image = self.data.pop(0)
            self.data.clear()
            for i in range(24):
                self.data.append(image.copy())
        if self.job is not None:
            self.window.after_cancel(self.job)
            self.job = None

        self.window.after(self.delay, self.update_Editor)

    def pin(self):
        self.isPin = not self.isPin
        if self.isPin:
            img_open = PIL.Image.open('./resources/recording32_2.png')
            self.window.icon_recording = PIL.ImageTk.PhotoImage(img_open)
            self.recording_image = self.label_mode = ttk.Label(self.window, image=self.window.icon_recording)
            self.recording_image.place(relx=0.9, rely=0)
        else:
            self.recording_image.place_forget()
        self.btn_pin.configure(text="Pin End") if self.isPin else self.btn_pin.configure(text="Pin Start")

    def save(self):
        imageio.mimsave("result.gif", self.data, 'GIF', duration=(1 / (20 ** 2)) * self.delay)
        print((1 / (24 ** 2)) * self.delay)
        if self.job is not None:
            self.window.after_cancel(self.job)
            self.job = None
        self.vid.__del__()
        self.canvas.delete("all")
        self.label_mode.configure(text="End of Saving GIF")

    def update(self):
        # Get a frame from the video source
        if not self.isInit:
            return
        if self.isStop:
            ret = False
        else:
            ret, frame = self.vid.get_frame()
            frame = cv2.resize(frame, (Setttings.WIDTH, Setttings.HEIGHT))
            # print(frame.shape)
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            update_histogram(self, frame)
            if self.isPin:
                self.data.append(frame)
            # print(self.isStop)
        self.job = self.window.after(self.delay, self.update)

    def update_Editor(self):

        if not self.isStop:
            Effect.apply_effect(self)
            AddText.addText(self)
            self.data.append(self.data[0])
            frame = self.data.pop(0)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            update_histogram(self, frame)
        self.job = self.window.after(self.delay, self.update_Editor)

    def init_menu_bar(self):
        menu_bar = tk.Menu(self.window)
        # menu_bar.add_command(label="Setting", command=setting)

        setting_menu = tk.Menu(menu_bar, tearoff=0)
        setting_menu.add_command(label="Open File", command=lambda: Setttings.OpenFile(self))
        setting_menu.add_command(label="Change Delay Duration", command=lambda: Setttings.modify_delay(self))
        setting_menu.add_command(label="Exit", command=lambda: Setttings.Exit(self))
        menu_bar.add_cascade(label="Setting", menu=setting_menu)

        effect_menu = tk.Menu(menu_bar, tearoff=0)
        effect_menu.add_command(label="Negative Flash", command=lambda: Effect.NegativeFlash(self, effect_menu))
        effect_menu.add_command(label="Gamma Correction", command=lambda: Effect.Gamma(self, effect_menu))
        effect_menu.add_command(label="Light Flash", command=lambda: Effect.LightFlash(self, effect_menu))
        effect_menu.add_command(label="Shake", command=lambda: Effect.Shake(self, effect_menu))
        effect_menu.add_command(label="Slide", command=lambda: Effect.Slide(self, effect_menu))
        effect_menu.add_command(label="Segmentation", command=lambda: Effect.Segmentation(self, effect_menu))
        effect_menu.add_command(label="Foreground", command=lambda: Effect.Texture(self, effect_menu))
        effect_menu.add_command(label="Background", command=lambda: Effect.Background(self, effect_menu))
        effect_menu.add_command(label="Gaussian Blur", command=lambda: Effect.GaussianBlur(self, effect_menu))
        effect_menu.add_command(label="Canny Edge Detect", command=lambda: Effect.CannyEdgeDetect(self, effect_menu))
        effect_menu.add_command(label="Gaussian Noise", command=lambda: Effect.GaussianNoise(self, effect_menu))
        effect_menu.add_command(label="White Point Noise", command=lambda: Effect.WhiteNoise(self, effect_menu))
        menu_bar.add_cascade(label="Mode", menu=effect_menu)
        text_menu = tk.Menu(menu_bar, tearoff=0)
        text_menu.add_command(label="Text Flash", command=lambda: AddText.Flash(text_menu))
        text_menu.add_command(label="Add Text", command=lambda: AddText.popup_window(self))
        menu_bar.add_cascade(label="Text", menu=text_menu)
        self.window.config(menu=menu_bar)


def update_histogram(self, frame):
    r, g, b = cv2.split(frame)
    histImgG = calcAndDrawHist(g, [0, 255, 0])
    histImgR = calcAndDrawHist(r, [0, 0, 255])
    histImgB = calcAndDrawHist(b, [255, 0, 0])
    histImgR = cv2.resize(histImgR, (130, 130))
    histImgG = cv2.resize(histImgG, (130, 130))
    histImgB = cv2.resize(histImgB, (130, 130))

    histImgR = PIL.Image.fromarray(histImgR)
    histImgG = PIL.Image.fromarray(histImgG)
    histImgB = PIL.Image.fromarray(histImgB)
    histImgR = PIL.ImageTk.PhotoImage(histImgR)
    histImgG = PIL.ImageTk.PhotoImage(histImgG)
    histImgB = PIL.ImageTk.PhotoImage(histImgB)
    self.histogramR.configure(image=histImgR)
    self.histogramR.image = histImgR
    self.histogramG.configure(image=histImgG)
    self.histogramG.image = histImgG
    self.histogramB.configure(image=histImgB)
    self.histogramB.image = histImgB


def calcAndDrawHist(image, color):
    hist = cv2.calcHist([image], [0], None, [256], [0.0, 255.0])
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
    histImg = np.zeros([256, 256, 3], np.uint8)
    hpt = int(0.9 * 256)

    for h in range(256):
        intensity = int(hist[h] * hpt / maxVal)
        cv2.line(histImg, (h, 256), (h, 256 - intensity), color)

    return histImg
