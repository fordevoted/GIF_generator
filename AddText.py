from PIL import Image, ImageFont, ImageDraw
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk

ttf = ["ChangChengXiaoYaoTi-1.ttf",
       "DingDingWoYiQingChenTi-2.ttf",
       "YuShiXingShu-2.ttf",
       "Da113-1.ttf",
       "YingZhangXingShu-2.ttf", "modenBefore.ttf",
       "tichi.ttf", "complex.ttf"]
ttf_name = ["長城小姚體", "我逸清晨體", "魚石行書", "大髭字體", "英章行書", "今昔隸書", "方圓太極草書", "王翰宗行書繁"]

position = (0, 0)
color = (255, 255, 255)
size = 16
str = ""
font = ""
isAddText = False
text_apply_frame_count = 0

isFlash = False
flash_duration = 0


def get_result(app, win, inputs, listbox):
    global str
    str = inputs[0].get()
    global size
    size = int(inputs[1].get())
    global color
    color_str = inputs[2].get()
    color = (int(color_str[1:3], 16), int(color_str[3:5], 16), int(color_str[5:], 16))
    global position
    position_str = inputs[3].get().split(",")
    position = (int(position_str[0]), int(position_str[1]))
    global font
    font = ttf[listbox.curselection()[0]]
    global isAddText
    isAddText = True
    global text_apply_frame_count
    text_apply_frame_count = 0
    win.destroy()
    app.isStop = False


def popup_window(app):
    if not app.isInit:
        return
    app.isStop = True
    win = tk.Toplevel()
    win.wm_title("Effect Settings")
    inputs = []
    for i in range(4):
        inputs.append(tk.StringVar())
    label = ttk.Label(win, text="Add Text")
    label.grid(row=0, column=0)
    entry = tk.Entry(win, text="Input text", textvariable=inputs[0])
    inputs[0].set("1 6 3 b r a c e s")
    entry.grid(row=0, column=1)
    label = ttk.Label(win, text="text size")
    label.grid(row=1, column=0)
    entry = ttk.Entry(win, text="text size", textvariable=inputs[1])
    inputs[1].set("48")
    entry.grid(row=1, column=1)
    label = ttk.Label(win, text="text color")
    label.grid(row=2, column=0)
    entry = ttk.Entry(win, text="text color", textvariable=inputs[2])
    inputs[2].set("#cd8068")
    entry.grid(row=2, column=1)

    label = ttk.Label(win, text="text position")
    label.grid(row=3, column=0)
    entry = ttk.Entry(win, text="text position", textvariable=inputs[3])
    inputs[3].set("250,200")
    entry.grid(row=3, column=1)

    listbox = tk.Listbox(win)
    for i in range(8):
        listbox.insert(tk.END, ttf_name[i])
    listbox.grid(row=4, column=1)

    b = ttk.Button(win, text="Okay", command=lambda: get_result(app, win, inputs, listbox))
    b.grid(row=4, column=0)


def addText(app):
    global text_apply_frame_count
    global flash_duration
    if isAddText and (text_apply_frame_count < app.data.__len__()):
        if not isFlash or (flash_duration % 24 <= 21):
            img = Image.fromarray(app.data[0])
            # print("./font/" + font)
            font_use = ImageFont.truetype("./font/" + font, size)
            draw = ImageDraw.Draw(img)
            draw.text(position, str, color, font=font_use)
            text_apply_frame_count += 1
            app.data[0] = np.array(img)
            # cv2.imshow("text", np.array(img))
            flash_duration = 0 if flash_duration == 24 else flash_duration + 1


def Flash(menu):
    global isFlash
    global  text_apply_frame_count
    if not isFlash:
        menu.entryconfigure(0, label="* " + menu.entrycget(0, "label") + " On")
    else:
        menu.entryconfigure(0, label=menu.entrycget(0, "label")[2:-3])
        text_apply_frame_count = 0
    isFlash = not isFlash
