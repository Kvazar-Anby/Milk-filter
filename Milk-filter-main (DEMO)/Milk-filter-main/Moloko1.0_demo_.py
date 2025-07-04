import os
import sys
import random
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import tempfile

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# HYNYA optimiZZZation
def apply_custom_filter_optimized(image_or_path, milk_mode=True, punt=50):
    if isinstance(image_or_path, str):
        image = Image.open(image_or_path).convert("RGBA")
    else:
        image = image_or_path.convert("RGBA")

    data = np.array(image)
    brightness = data[..., :3].mean(axis=2)
    output = data.copy()
    rand_mask = np.random.rand(*brightness.shape) < (punt / 100)

    if milk_mode:
        output[brightness <= 25] = [0, 0, 0, 255]
        output[(brightness >= 120) & (brightness < 200)] = [102, 0, 31, 255]
        output[brightness >= 230] = [137, 0, 146, 255]
        mask = (brightness > 25) & (brightness <= 70)
        output[mask & rand_mask] = [0, 0, 0, 255]
        output[mask & ~rand_mask] = [102, 0, 31, 255]
        mask = (brightness > 70) & (brightness < 120)
        output[mask & rand_mask] = [102, 0, 31, 255]
        output[mask & ~rand_mask] = [0, 0, 0, 255]
        mask = (brightness >= 200) & (brightness < 230)
        output[mask & rand_mask] = [137, 0, 146, 255]
        output[mask & ~rand_mask] = [102, 0, 31, 255]
    else:
        output[brightness <= 25] = [0, 0, 0, 255]
        output[(brightness >= 90) & (brightness < 150)] = [92, 36, 60, 255]
        output[brightness >= 200] = [203, 43, 43, 255]
        mask = (brightness > 25) & (brightness <= 70)
        output[mask & rand_mask] = [0, 0, 0, 255]
        output[mask & ~rand_mask] = [92, 36, 60, 255]
        mask = (brightness > 70) & (brightness < 90)
        output[mask & rand_mask] = [92, 36, 60, 255]
        output[mask & ~rand_mask] = [0, 0, 0, 255]
        mask = (brightness >= 150) & (brightness < 200)
        output[mask & rand_mask] = [203, 43, 43, 255]
        output[mask & ~rand_mask] = [92, 36, 60, 255]

    return Image.fromarray(output)

# гуи уи
window = tk.Tk()
window.title("Milk Filter")
window.geometry("800x650")

filename = None
original_image = None
filtered_image = None
is_video = False
video_temp_output = None

# рамОчки
frame_top = ttk.Frame(window)
frame_top.pack(pady=10)

frame_center = ttk.Frame(window)
frame_center.pack()

frame_bottom = ttk.Frame(window)
frame_bottom.pack(pady=10)

# текстики
label_original = tk.Label(frame_center, text="Исходная фоточка / видео")
label_original.grid(row=0, column=0, padx=10)

label_filtered = tk.Label(frame_center, text="Под молочком :3")
label_filtered.grid(row=0, column=1, padx=10)

display_original = tk.Label(frame_center)
display_original.grid(row=1, column=0)

display_filtered = tk.Label(frame_center)
display_filtered.grid(row=1, column=1)

# кнопачки винтики шпунчики
milk = tk.IntVar(value=1)
eff = tk.IntVar(value=1)
comp = tk.IntVar(value=0)
slider_int = tk.IntVar(value=0)

tk.Checkbutton(frame_bottom, text="фиолетовый mode", variable=milk).pack(anchor="w", pady=2)
tk.Checkbutton(frame_bottom, text="Вырвиглазность", variable=eff).pack(anchor="w", pady=2)
tk.Checkbutton(frame_bottom, text="Сжать (JPEG)", variable=comp).pack(anchor="w", pady=2)

tk.Label(frame_bottom, text="сжатие (0-100)").pack(anchor="w", pady=(10, 0))
slider = ttk.Scale(frame_bottom, variable=slider_int, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
slider.pack(anchor="w", pady=2)

# функциАнал
def show_image(img, widget):
    resized = img.resize((300, 300), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized)
    widget.config(image=tk_img)
    widget.image = tk_img

def select_file():
    global filename, original_image, is_video
    file = filedialog.askopenfilename(filetypes=[
        ("Images and Videos", "*.png *.jpg *.jpeg *.bmp *.mp4 *.avi"),
        ("All files", "*.*")
    ])
    if file:
        filename = file
        is_video = file.lower().endswith(('.mp4', '.avi'))
        if not is_video:
            original_image = Image.open(file).convert("RGBA")
            show_image(original_image, display_original)
        else:
            cap = cv2.VideoCapture(file)
            ret, frame = cap.read()
            cap.release()
            if ret:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
                original_image = img
                show_image(img, display_original)

def apply_filter():
    global filtered_image, video_temp_output
    if not filename:
        messagebox.showwarning("нет фотачки", "Дурашка, сначала файл выбери")
        return

    punt = 70 if eff.get() else 100
    temp_path = filename

    if not is_video:
        if comp.get():
            compressed = Image.open(filename).convert("RGB")
            compressed.save("temp.jpg", quality=100-slider_int.get())
            temp_path = "temp.jpg"
        filtered_image = apply_custom_filter_optimized(temp_path, milk_mode=bool(milk.get()), punt=punt)
        show_image(filtered_image, display_filtered)
    else:
        cap = cv2.VideoCapture(filename)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        os.close(temp_fd)
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
            img = apply_custom_filter_optimized(img, milk_mode=bool(milk.get()), punt=punt)
            out_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
            out.write(out_frame)

        cap.release()
        out.release()
        video_temp_output = temp_path
        messagebox.showinfo("Ура", "Видео полили молочком!")

def save_filtered():
    if not is_video and not filtered_image:
        messagebox.showwarning("Нет фильтра", "фильтр налажи дурашка")
        return

    filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg")] if not is_video else [("MP4 Video", "*.mp4")]
    ext = ".png" if not is_video else ".mp4"

    file = filedialog.asksaveasfilename(defaultextension=ext, filetypes=filetypes)
    if file:
        if not is_video:
            filtered_image.save(file)
        else:
            if video_temp_output:
                os.replace(video_temp_output, file)

# кнопачки
ttk.Button(frame_top, text="Выбрать файл", command=select_file).pack(side=tk.LEFT, padx=10)
ttk.Button(frame_top, text="Малачко", command=apply_filter).pack(side=tk.LEFT, padx=10)
ttk.Button(frame_top, text="Сохранить", command=save_filtered).pack(side=tk.LEFT, padx=10)

window.mainloop()