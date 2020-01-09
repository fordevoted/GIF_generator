import tkinter as tk
import pyplayer
import Segmentation_Engine

# Create a window and pass it to the Application object

Segmentation_Engine.init()
root = tk.Tk()
root.geometry("1000x600")
app = pyplayer.App(root, "GIF Generator", "Lab4.mp4")
