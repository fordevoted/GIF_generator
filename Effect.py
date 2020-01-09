import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import cv2
from PIL import Image, ImageTk

import Segmentation_Engine
import Scrollable
import random

NEGATIVE_FLASH = 0
GAMMA = 1
LIGHT_FLASH = 2
SHAKE = 3
SLIDE = 4
SEGMENTATION = 5
TEXTURE = 6
BACKGROUND = 7
GAUSSIAN_BLUR = 8
CANNY_EDGE_DETECT = 9
GAUSSIAN_NOISE = 10
WHITE_NOISE = 11

mode = []
for i in range(12):
    mode.append(False)
mode_apply_frame_count = []
for i in range(12):
    mode_apply_frame_count.append(0)
mode_effect_text = ["Input Effect Level", "Input Gamma (range:.01 - 25)(default:20)",
                    "Input Flash Duration( Every few frames)(default:5)", "Input Shake level(a few pixels)(default:5)",
                    "Input Slide Direction(default:right)", "Input Background color((default:#000000))",
                    "Choose Texture", "Choose Background", "Input Kernel Size(default:7)",
                    "Input Lower And Upper Bound(default:30,160)", "Input Noise Level(Range:0-255)(default:40)",
                    "Input Update Duration(default:3)"]

gamma_level = 0

light_flash_frame = 0
light_flash_count = 0

shake_pixels = 1
shake_count = [0, 0]

slide_direction = 0

segmentation_bg = ""

images = []
texture_index = 0
texture_shake_count = [0, 0]
texture_shake_pixel = 0
background_index = 0
isBackgroundSlide = False
isBackgroundShake = False


background_shake_count = [0, 0]
background_shake_pixel = 0

blur_kernel_size = 0

canny_lower_bound = 0
canny_upper_bound = 0

noise_level = 0

white_noise = []
white_noise_update = 0


def get_result(app, win, input_str, index, i=-1):
    if index == GAMMA:
        global gamma_level
        if input_str.get().__len__() == 0:
            gamma_level = 20
        else:
            gamma_level = float(input_str.get())
            if gamma_level > 25:
                gamma_level = 25
            elif gamma_level < .01:
                gamma_level = .01
    elif index == LIGHT_FLASH:
        global light_flash_frame
        if input_str.get().__len__() == 0:
            light_flash_frame = 5
        else:
            light_flash_frame = int(float(input_str.get()))
    elif index == SHAKE:
        global shake_pixels
        if input_str.get().__len__() == 0:
            shake_pixels = 5
        else:
            shake_pixels = int(float(input_str.get()))
    elif index == SLIDE:
        global slide_direction
        if input_str.get().__len__() == 0:
            slide_direction = 'right'
        else:
            slide_direction = str(input_str.get())
    elif index == SEGMENTATION:
        global segmentation_bg
        if input_str.get().__len__() == 0:
            segmentation_bg = "#000000"
        else:
            segmentation_bg = str(input_str.get())
    elif index == TEXTURE:
        global texture_index
        texture_index = i
    elif index == BACKGROUND:
        global background_index
        background_index = i
    elif index == GAUSSIAN_BLUR:
        global blur_kernel_size
        if input_str.get().__len__() == 0:
            blur_kernel_size = 7
        else:
            blur_kernel_size = int(input_str.get())
    elif index == CANNY_EDGE_DETECT:
        if input_str.get().__len__() == 0:
            bounds = "30,160"
        else:
            bounds = input_str.get().split(",")
        global canny_lower_bound
        canny_lower_bound = int(bounds[0])
        global canny_upper_bound
        canny_upper_bound = int(bounds[1])
    elif index == GAUSSIAN_NOISE:
        global noise_level
        if input_str.get().__len__() == 0:
            noise_level = 40
        else:
            noise_level = float(input_str.get())
    elif index == WHITE_NOISE:
        global white_noise_update
        if input_str.get().__len__() ==0:
            white_noise_update = 3
        else:
            white_noise_update = int(input_str.get())
    win.destroy()
    app.isStop = False


def background_slide_selected(v):
    global isBackgroundSlide
    global isBackgroundShake
    global background_shake_count
    global background_shake_pixel
    global texture_shake_count
    global texture_shake_pixel
    if v.get() == 1:
        isBackgroundSlide = True
        isBackgroundShake = False
    if v.get() == 2:
        isBackgroundShake = True
        isBackgroundSlide = False
    background_shake_count = texture_shake_count = [0, 0]
    background_shake_pixel = texture_shake_pixel = 3


def popup_window(app, menu, index):
    app.isStop = True
    win = tk.Toplevel()
    win.wm_title("Effect Settings")
    label = ttk.Label(win, text=mode_effect_text[index])
    label.grid(row=0, column=0)
    if index != TEXTURE and index != BACKGROUND:
        input = tk.StringVar()
        entry = ttk.Entry(win, text="Input", textvariable=input)
        entry.grid(row=1, column=0)
        b = ttk.Button(win, text="Okay", command=lambda: get_result(app, win, input, index))
        b.grid(row=2, column=0)
    else:
        v = tk.IntVar()
        r = tk.Radiobutton(win, text="still", variable=v, value=0,
                           command=lambda v=v: background_slide_selected(v))
        r.select()
        r.grid(row=1, column=0)
        tk.Radiobutton(win, text="back ground slide (right)", variable=v, value=1,
                       command=lambda v=v: background_slide_selected(v)).grid(row=1, column=1)
        tk.Radiobutton(win, text="back ground shake ", variable=v, value=2,
                       command=lambda v=v: background_slide_selected(v)).grid(row=1, column=2)
        root = ttk.Frame(win)
        root.grid(row=2, column=0)
        scroll = Scrollable.Scrollable(root)
        global images
        for i in range(17):
            im = Image.open("./resources/texture" + str(i) + ".jpg")

            im = im.resize((150, 150), resample=0)
            imtk = ImageTk.PhotoImage(im)
            images.append(im)
            b = ttk.Button(scroll, image=imtk)
            b.index = i
            if index == TEXTURE:
                b.configure(command=lambda i=i: get_result(app, win, tk.StringVar(), TEXTURE, i))
            else:

                b.configure(command=lambda i=i: get_result(app, win, tk.StringVar(), BACKGROUND, i))
            b.grid(row=int(i / 2) + 2, column=int(i % 2))
            b.image = imtk
        scroll.update()


def NegativeFlash(app, menu):
    if app.isInit:
        update_label(menu, NEGATIVE_FLASH)
        # do whatever the NEGATIVE_FLASH is
        mode_apply_frame_count[NEGATIVE_FLASH] = 0


def Gamma(app, menu):
    if app.isInit:
        update_label(menu, GAMMA)
        if mode[GAMMA]:
            popup_window(app, menu, GAMMA)
            mode_apply_frame_count[GAMMA] = 0


def LightFlash(app, menu):
    if app.isInit:
        update_label(menu, LIGHT_FLASH)
        if mode[LIGHT_FLASH]:
            popup_window(app, menu, LIGHT_FLASH)
            mode_apply_frame_count[LIGHT_FLASH] = 0


def Shake(app, menu):
    if app.isInit:
        update_label(menu, SHAKE)
        if mode[SHAKE]:
            popup_window(app, menu, SHAKE)
            mode_apply_frame_count[SHAKE] = 0


def Slide(app, menu):
    if app.isInit:
        update_label(menu, SLIDE)
        if mode[SLIDE]:
            popup_window(app, menu, SLIDE)
            mode_apply_frame_count[SLIDE] = 0


def Segmentation(app, menu):
    if app.isInit:
        update_label(menu, SEGMENTATION)
        if mode[SEGMENTATION]:
            popup_window(app, menu, SEGMENTATION)
            mode_apply_frame_count[SEGMENTATION] = 0


def Texture(app, menu):
    if app.isInit:
        update_label(menu, TEXTURE)
        if mode[TEXTURE]:
            popup_window(app, menu, TEXTURE)
            mode_apply_frame_count[TEXTURE] = 0


def Background(app, menu):
    if app.isInit:
        update_label(menu, BACKGROUND)
        if mode[BACKGROUND]:
            popup_window(app, menu, BACKGROUND)
            mode_apply_frame_count[BACKGROUND] = 0


def GaussianBlur(app, menu):
    if app.isInit:
        update_label(menu, GAUSSIAN_BLUR)
        if mode[GAUSSIAN_BLUR]:
            popup_window(app, menu, GAUSSIAN_BLUR)
            mode_apply_frame_count[GAUSSIAN_BLUR] = 0


def CannyEdgeDetect(app, menu):
    if app.isInit:
        update_label(menu, CANNY_EDGE_DETECT)
        if mode[CANNY_EDGE_DETECT]:
            popup_window(app, menu, CANNY_EDGE_DETECT)
            mode_apply_frame_count[CANNY_EDGE_DETECT] = 0


def GaussianNoise(app, menu):
    if app.isInit:
        update_label(menu, GAUSSIAN_NOISE)
        if mode[GAUSSIAN_NOISE]:
            popup_window(app, menu, GAUSSIAN_NOISE)
            mode_apply_frame_count[GAUSSIAN_NOISE] = 0


def WhiteNoise(app, menu):
    if app.isInit:
        update_label(menu, WHITE_NOISE)
        if mode[WHITE_NOISE]:
            popup_window(app, menu, WHITE_NOISE)
            mode_apply_frame_count[WHITE_NOISE] = 0


def update_label(menu, index):
    if not mode[index]:
        menu.entryconfigure(index, label="* " + menu.entrycget(index, "label") + " On")
    else:
        menu.entryconfigure(index, label=menu.entrycget(index, "label")[2:-3])
    mode[index] = not mode[index]


def apply_effect(app):
    frame = app.data[0]
    if mode[NEGATIVE_FLASH]:
        if mode_apply_frame_count[NEGATIVE_FLASH] < app.data.__len__():
            frame = 255 - frame
            mode_apply_frame_count[NEGATIVE_FLASH] += 1
    if mode[GAMMA]:
        if mode_apply_frame_count[GAMMA] < app.data.__len__():
            frame = frame ** gamma_level
            frame = frame * (255 / np.max(frame))
            frame = np.array(frame, dtype=np.uint8)
            mode_apply_frame_count[GAMMA] += 1
    if mode[LIGHT_FLASH]:
        if mode_apply_frame_count[LIGHT_FLASH] < app.data.__len__():
            global light_flash_count
            if light_flash_count % light_flash_frame == 0:
                frame = frame ** .5
                frame = frame * (255 / np.max(frame))
                frame = np.array(frame, dtype=np.uint8)
            light_flash_count += 1
            mode_apply_frame_count[GAMMA] += 1
    if mode[SHAKE]:
        if mode_apply_frame_count[SHAKE] < app.data.__len__():
            global shake_pixels
            b, g, r = cv2.split(frame)
            b = np.roll(b, shake_pixels * (-1 ** (shake_count[1] % 2)), axis=0 if (shake_count[1] % 2) == 0 else 1)
            g = np.roll(g, shake_pixels * (-1 ** (shake_count[1] % 2)), axis=0 if (shake_count[1] % 2) == 0 else 1)
            r = np.roll(r, shake_pixels * (-1 ** (shake_count[1] % 2)), axis=0 if (shake_count[1] % 2) == 0 else 1)
            shake_count[0] = (shake_count[0] + 1) % 4
            if shake_count[0] == 0:
                shake_count[1] += 1
                if shake_count[1] == 2:
                    shake_pixels *= 2  # shake back and be balanceaxis=0 if (shake_count[1] % 2) == 0 else 1
            frame = cv2.merge((b, g, r)).astype(np.uint8)
            mode_apply_frame_count[SHAKE] += 1
    if mode[SLIDE]:
        if mode_apply_frame_count[SLIDE] < app.data.__len__():
            global slide_direction
            if slide_direction == 'top':
                dir = 0
            elif slide_direction == 'left':
                dir = 1
            elif slide_direction == 'down':
                dir = 2
            else:
                dir = 3
            b, g, r = cv2.split(frame)
            b = np.roll(b, 5 * (mode_apply_frame_count[SLIDE] + 1) * (-1 if dir < 2 else 1),
                        axis=0 if (dir % 2) == 0 else 1)
            g = np.roll(g, 5 * (mode_apply_frame_count[SLIDE] + 1) * (-1 if dir < 2 else 1),
                        axis=0 if (dir % 2) == 0 else 1)
            r = np.roll(r, 5 * (mode_apply_frame_count[SLIDE] + 1) * (-1 if dir < 2 else 1),
                        axis=0 if (dir % 2) == 0 else 1)
            frame = cv2.merge((b, g, r)).astype(np.uint8)
            mode_apply_frame_count[SLIDE] += 5
    if mode[SEGMENTATION]:
        if mode_apply_frame_count[SEGMENTATION] < app.data.__len__():
            frame = Segmentation_Engine.segmentation(
                Segmentation_Engine.graph, Segmentation_Engine.LABEL_NAMES, frame, segmentation_bg)
            print(mode_apply_frame_count[SEGMENTATION])
            mode_apply_frame_count[SEGMENTATION] += 1
    if mode[TEXTURE]:
        if mode_apply_frame_count[TEXTURE] < app.data.__len__():
            im = cv2.imread("./resources/texture" + str(texture_index) + ".jpg")
            im = im[:, :, ::-1]  # BGR to RGB
            image = cv2.resize(im, (frame.shape[1], frame.shape[0]))
            if isBackgroundSlide:
                b, g, r = cv2.split(frame)
                b = np.roll(b, 3 * (mode_apply_frame_count[TEXTURE] + 1), axis=1)
                g = np.roll(g, 3 * (mode_apply_frame_count[TEXTURE] + 1), axis=1)
                r = np.roll(r, 3 * (mode_apply_frame_count[TEXTURE] + 1), axis=1)
                frame = cv2.merge((b, g, r)).astype(np.uint8)
            if isBackgroundShake:
                global texture_shake_pixel
                b, g, r = cv2.split(frame)
                b = np.roll(b, texture_shake_pixel * (-1 ** (texture_shake_count[1] % 2)),
                            axis=0 if (texture_shake_count[1] % 2) == 0 else 1)
                g = np.roll(g, texture_shake_pixel * (-1 ** (texture_shake_count[1] % 2)),
                            axis=0 if (texture_shake_count[1] % 2) == 0 else 1)
                r = np.roll(r, texture_shake_pixel * (-1 ** (texture_shake_count[1] % 2)),
                            axis=0 if (texture_shake_count[1] % 2) == 0 else 1)
                texture_shake_count[0] = (texture_shake_count[0] + 1) % 4
                if texture_shake_count[0] == 0:
                    texture_shake_count[1] += 1

                    if texture_shake_count[1] == 2:
                        texture_shake_pixel *= 2  # shake back and be balance
                frame = cv2.merge((b, g, r)).astype(np.uint8)

            framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 將圖片灰度化
            ret, mask = cv2.threshold(framegray, 20, 255, cv2.THRESH_BINARY)  # ret是閾值（175）mask是二值化圖像
            mask_inv = cv2.bitwise_not(mask)  # 獲取把logo的區域取反 按位運算

            img1_bg = cv2.bitwise_and(image, image, mask=mask)  # 在img1上面，將logo區域和mask取與使值爲0
            img2_fg = cv2.bitwise_and(frame, frame, mask=mask_inv)  # 獲取logo的像素信息
            if texture_index == 16:
                frame = cv2.add(frame, img1_bg)
            else:
                frame = cv2.add(img1_bg, img2_fg)  # 相加即可
            mode_apply_frame_count[TEXTURE] += 1
    if mode[BACKGROUND]:
        if mode_apply_frame_count[BACKGROUND] < app.data.__len__():
            im = cv2.imread("./resources/texture" + str(background_index) + ".jpg")
            im = im[:, :, ::-1]  # BGR to RGB
            image = cv2.resize(im, (frame.shape[1], frame.shape[0]))
            if isBackgroundSlide:
                b, g, r = cv2.split(image)
                b = np.roll(b, 3 * (mode_apply_frame_count[BACKGROUND] + 1), axis=1)
                g = np.roll(g, 3 * (mode_apply_frame_count[BACKGROUND] + 1), axis=1)
                r = np.roll(r, 3 * (mode_apply_frame_count[BACKGROUND] + 1), axis=1)
                image = cv2.merge((b, g, r)).astype(np.uint8)
            if isBackgroundShake:
                global background_shake_pixel
                b, g, r = cv2.split(image)
                b = np.roll(b, background_shake_pixel * (-1 ** (background_shake_count[1] % 2)),
                            axis=0 if (background_shake_count[1] % 2) == 0 else 1)
                g = np.roll(g, background_shake_pixel * (-1 ** (background_shake_count[1] % 2)),
                            axis=0 if (background_shake_count[1] % 2) == 0 else 1)
                r = np.roll(r, background_shake_pixel * (-1 ** (background_shake_count[1] % 2)),
                            axis=0 if (background_shake_count[1] % 2) == 0 else 1)
                background_shake_count[0] = (background_shake_count[0] + 1) % 4
                if background_shake_count[0] == 0:
                    background_shake_count[1] += 1

                    if background_shake_count[1] == 2:
                        background_shake_pixel *= 2  # shake back and be balance
                image = cv2.merge((b, g, r)).astype(np.uint8)
            _, frame_gray = cv2.threshold(frame, 4, 255, cv2.THRESH_BINARY)
            frame_ivt = cv2.bitwise_not(frame_gray)
            # cv2.imshow("frame ivt", frame_ivt)
            image = cv2.bitwise_and(frame_ivt, image)
            # cv2.imshow("post image(invert people black)", image)
            frame = cv2.add(frame, image)
            mode_apply_frame_count[BACKGROUND] += 1
    if mode[GAUSSIAN_BLUR]:
        if mode_apply_frame_count[GAUSSIAN_BLUR] < app.data.__len__():
            frame = cv2.GaussianBlur(frame, (blur_kernel_size, blur_kernel_size), cv2.BORDER_DEFAULT)
            mode_apply_frame_count[GAUSSIAN_BLUR] += 1
    if mode[CANNY_EDGE_DETECT]:
        if mode_apply_frame_count[CANNY_EDGE_DETECT] < app.data.__len__():
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, canny_lower_bound, canny_upper_bound)
            frame = np.uint8(np.absolute(canny))
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            mode_apply_frame_count[CANNY_EDGE_DETECT] += 1
    if mode[GAUSSIAN_NOISE]:
        if mode_apply_frame_count[GAUSSIAN_NOISE] < app.data.__len__():
            row, col, ch = frame.shape
            gauss = np.random.normal(0, 0.01, (row, col, ch))
            gauss = gauss.reshape(row, col, ch)
            # gauss = 255 * (gauss / np.max(gauss))
            # gauss = gauss.astype(np.uint8)
            gauss = gauss * noise_level
            gauss = gauss.astype(np.uint8)
            frame = cv2.add(frame, gauss)
           # frame = 255 * (frame / np.max(frame))
            frame = frame.astype(np.uint8)
            mode_apply_frame_count[GAUSSIAN_NOISE] += 1
    if mode[WHITE_NOISE]:
        if mode_apply_frame_count[WHITE_NOISE] < app.data.__len__():
            row, col, ch = frame.shape
            global white_noise
            if mode_apply_frame_count[WHITE_NOISE] % white_noise_update == 0:
                white_noise.clear()
                for i in range(200):
                    white_noise.append((int(random.random() * row), int(random.random() * col)))
            for i in range(200):
                height = white_noise[i][0]
                width = white_noise[i][1]
                for j in range(3):
                    frame[height][width][j] = 255
                if i > 100:
                    for j in range(3):
                        frame[height][width][j] = 255
                        frame[height + 1 if height + 1 < row else height][width][j] = 255
                        frame[height - 1 if height - 1 > 0 else height][width][j] = 255
                        frame[height][width + 1 if width + 1 < col else width][j] = 255
                        frame[height][width - 1 if width - 1 > 0 else width][j] = 255
            mode_apply_frame_count[WHITE_NOISE] += 1
    app.data[0] = frame
