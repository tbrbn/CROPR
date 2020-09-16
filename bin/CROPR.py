import sys
import os
from imageio import imread
from tkinter import Canvas, Tk, CENTER, \
    Button, Scrollbar, VERTICAL, HORIZONTAL, RIGHT, BOTTOM, Y, X, LEFT, BOTH, messagebox, Checkbutton, IntVar
from PIL import ImageTk, Image, ImageEnhance
from tkinter.filedialog import askopenfile, askdirectory, Frame
from scipy import ndimage as ndi
from skimage import feature
from numpy import asanyarray
from win32api import GetSystemMetrics

img_path = None
img = None


class MainWindow:
    def __init__(self, root):
        self.screen_w = GetSystemMetrics(0)
        self.screen_h = GetSystemMetrics(1)
        self.scale_factor = 1
        self.lines = None
        self.lines_ground = None
        self.root = root
        self.canvas = Canvas(root, width=400, height=400)
        self.img_path = None
        self.img_dir = None
        self.img_name = None
        self.img_is_loaded = False
        self.box_settings_var = IntVar()
        self.frame_buttons = Frame()
        self.img = ImageTk.PhotoImage(Image.open(resource_path("CROPR_intro.png")).convert("RGBA").resize((400, 400)))
        self.img_on_canvas = self.canvas.create_image(202, 202, anchor=CENTER, image=self.img, )
        self.button = Button(self.frame_buttons, text="Import image", command=lambda: self.file_opener())
        self.button_dir = Button(self.frame_buttons, text="Output directory", command=lambda: self.choose_output_dir())
        self.box_settings = Checkbutton(self.frame_buttons, variable=self.box_settings_var,
                                        text="All views", onvalue = 1, offvalue = 0)
        self.button.pack(side=LEFT, padx=3, pady=3)
        self.button_dir.pack(side=LEFT, padx=3, pady=3)
        self.box_settings.pack(side=BOTTOM, padx=3, pady=3)
        self.frame_buttons.pack()
        self.ctrl_v = self.root.bind('<Control-v>', lambda e: self.clipboard_import(e))
        self.canvas.pack()
        self.images_unscaled = []

    def reset_canvas(self):
        self.frame_buttons.destroy()
        self.canvas.destroy()
        self.root.geometry("400x430")
        self.__init__(self.root)

    def file_opener(self):
        var = self.box_settings_var.get()
        self.reset_canvas()
        self.box_settings_var.set(var)
        a = askopenfile()
        if a is not None:
            self.img_path = a.name
            self.img_is_loaded = True
            b = self.img_path.split("/")[-1]
            self.img_name = "".join(str(b).split(".")[:-1])
            self.img_dir = "/".join(str(self.img_path).split("/")[0:-1]) + "/"
            self.img = ImageTk.PhotoImage(Image.open(self.img_path).convert("RGBA"))
            self.root.wm_title("CROPR 0.1 [" + self.img_dir + "]")
            self.update_canvas()

    def update_canvas(self):
        w = self.img.width()
        h = self.img.height()
        self.canvas.itemconfig(self.img_on_canvas, image=self.img, anchor=CENTER)
        self.get_size()
        self.canvas.coords(self.img_on_canvas, self.img.width() / 2 + 2, self.img.height() / 2 + 2)
        sbarV = Scrollbar(self.canvas, orient=VERTICAL)
        sbarH = Scrollbar(self.canvas, orient=HORIZONTAL)
        sbarV.config(command=self.canvas.yview)
        sbarH.config(command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=sbarV.set, xscrollcommand=sbarH.set)
        sbarV.pack(side=RIGHT, fill=Y)
        sbarH.pack(side=BOTTOM, fill=X)
        self.canvas.config(scrollregion=(0, 0, self.img.width() + 20, self.img.height() + 20),
                           width=self.img.width() + 2, height=self.img.height() + 2)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        self.lines = Lines(self, self.root, self.canvas)
        if self.screen_h < h or self.screen_w < w:
            self.root.state('zoomed')
        else:
            self.root.geometry(str(w + 100) + "x" + str(h + 100))

    def clipboard_import(self, event):
        try:
            a = self.img_dir
            self.reset_canvas()
            self.img_path = self.root.clipboard_get()
            self.img_is_loaded = True
            b = self.img_path.split("/")[-1]
            self.img_name = "".join(str(b).split(".")[:-1])
            if a is None:
                self.img_dir = "/".join(str(self.img_path).split("/")[0:-1]) + "/"
            else:
                self.img_dir = a
            self.img = ImageTk.PhotoImage(Image.open(self.img_path).convert("RGBA"))
            # self.root.unbind('<Control-v>', self.ctrl_v)
            self.root.wm_title("CROPR 0.1 [" + self.img_dir + "]")
            self.update_canvas()
        except:
            pass

    def choose_output_dir(self):
        if self.img_is_loaded:
            a = askdirectory()
            if a is not "":
                self.img_dir = a + "/"
            self.root.wm_title("CROPR 0.1 [" + self.img_dir + "]")
        else:
            messagebox.showinfo(message="Load an image first!")

    def get_size(self):
        self.img_x = self.img.width()
        self.img_y = self.img.height()

    def zoom_out(self):
        size = self.img.width() * 0.9, self.img.height() * 0.9
        im = Image.open(self.img_path).convert("RGBA")
        im.thumbnail(size)
        # self.scale_factor = im.size[0] / self.img.width()
        self.scale_factor = 0.9 * self.scale_factor
        # print(self.scale_factor)
        self.img = ImageTk.PhotoImage(im)
        self.canvas.itemconfig(self.img_on_canvas, image=self.img, anchor=CENTER)
        self.canvas.coords(self.img_on_canvas, self.img.width() / 2 + 2, self.img.height() / 2 + 2)
        self.get_size()

    def zoom_in(self):
        size = self.img.width() * 1.1, self.img.height() * 1.1
        im = Image.open(self.img_path).convert("RGBA")
        im.thumbnail(size)
        # self.scale_factor = im.size[0] / self.img.width()
        self.scale_factor = 1.1 * self.scale_factor
        if self.scale_factor > 1:
            self.scale_factor = 1
        # print(self.scale_factor)
        self.img = ImageTk.PhotoImage(im)
        self.canvas.itemconfig(self.img_on_canvas, image=self.img, anchor=CENTER)
        self.canvas.coords(self.img_on_canvas, self.img.width() / 2 + 2, self.img.height() / 2 + 2)
        self.get_size()


class Lines:
    def __init__(self, mainwindow, master, canvas):
        self.zoom_text = "<+>/<-> - Zoom In/Out\n"
        self.ground_mode_follow = False
        self.ground_mode = False
        self.contour_mode = False
        self.mask_mode = False
        self.manual_mode = False
        self.contrast_mode = False
        self.action_text = "<ESC> - skip\n<CTRL-Z> - undo\n"
        self.ground_mode_text = "<G> - Ground mode off\n"
        self.contour_mode_text = "<A> - Contour mode off\n"
        self.mask_mode_text = "<M> - Mask mode off\n"
        self.contrast_mode_text = "<C> - Contrast mode off\n"
        self.manual_mode_text = "<N> - Manual mode off\n"
        self.view_text = "Side\n"
        self.main_window = mainwindow
        self.master = master
        self.mask = None
        self.rect_dash = []
        self.cropbot = []
        self.on_off = [1, 1, 1, 1, 1, 1]
        self.master.bind(
            '<Escape>', lambda e: self.skip())
        self.master.bind(
            '<g>', lambda e: self.ground_mode_switch())
        # self.master.bind(
        #    '<a>', lambda e: self.contour_mode_switch())
        self.master.bind(
            '<m>', lambda e: self.mask_mode_switch())
        self.master.bind(
            '<Control-z>', lambda e: self.control_z())
        self.master.bind(
            '-', lambda e: self.main_window.zoom_out())
        self.master.bind(
            '+', lambda e: self.main_window.zoom_in())
        self.master.bind(
            '<c>', lambda e: self.contrast_mode_switch())
        self.master.bind(
            '<n>', lambda e: self.manual_mode_switch())
        self.escaped = False
        self.clicks = []
        self.clicks_ground_mode = []
        self.i = 0
        self.boxes = []
        self.boxes_ground_mode = []
        self.isMoving = True
        self.canvas = canvas
        self.vline1 = None
        self.hline1 = None
        self.new_cross(1)
        self.canvas.pack()
        self.text = self.canvas.create_text(0, 0, text=self.get_text())
        self.follow_the_mouse = self.canvas.bind(
            '<Motion>', lambda e: self.follow_mouse(e, self.vline, self.hline, self.text))
        self.canvas.bind(
            '<Button-1>', lambda e: self.on_click(e))
        self.canvas.bind(
            '<MouseWheel>', lambda e: self.on_mousewheel(e))
        self.canvas.bind(
            '<Shift-MouseWheel>', lambda e: self.on_shift_mousewheel(e))

    def ground_mode_switch(self):
        self.turn_all_off_except("ground_mode")
        if self.ground_mode:
            self.ground_mode = False
            self.ground_mode_text = "<G> - Ground mode off\n"
            self.canvas.configure(bg="SystemButtonFace")
        else:
            self.ground_mode = True
            self.ground_mode_text = "<G> - Ground mode ON\n"
            self.canvas.configure(bg="lightblue")
        self.refresh_text()

    def manual_mode_switch(self):
        self.turn_all_off_except("manual_mode")
        if self.manual_mode:
            self.manual_mode = False
            self.manual_mode_text = "<N> - Manual mode off\n"
            self.canvas.configure(bg="SystemButtonFace")
        else:
            self.manual_mode = True
            self.manual_mode_text = "<N> - Manual mode ON\n"
            self.canvas.configure(bg="gold3")
        self.refresh_text()

    def contrast_mode_switch(self):
        self.turn_all_off_except("contrast_mode")
        if self.contrast_mode:
            self.contrast_mode = False
            self.contrast_mode_text = "<C> - Contrast mode off\n"
            self.canvas.configure(bg="SystemButtonFace")
        else:
            self.contrast_mode = True
            self.contrast_mode_text = "<C> - Contrast mode ON\n"
            self.canvas.configure(bg="thistle4")
        self.refresh_text()

    def contour_mode_switch(self):
        self.turn_all_off_except("contour_mode")
        if self.contour_mode:
            self.contour_mode = False
            self.contour_mode_text = "<C> - Contour mode off\n"
            self.canvas.configure(bg="SystemButtonFace")
        else:
            self.contour_mode = True
            self.contour_mode_text = "<C> - Contour mode ON\n"
            self.canvas.configure(bg="DarkOrange1")
        self.refresh_text()

    def mask_mode_switch(self):
        self.turn_all_off_except("mask_mode")
        if self.mask_mode:
            self.mask_mode = False
            self.mask_mode_text = "<M> - Mask mode off\n"
            self.canvas.configure(bg="SystemButtonFace")
        else:
            self.mask_mode = True
            self.mask_mode_text = "<M> - Mask mode ON\n"
            self.canvas.configure(bg="Grey34")
        self.refresh_text()

    def turn_all_off_except(self, switch_to_keep):
        # if switch_to_keep is something else than below, it will turn all off (cf. confirm functions further down)
        if self.mask_mode and switch_to_keep is not "mask_mode":
            self.mask_mode_switch()
        if self.ground_mode and switch_to_keep is not "ground_mode":
            self.ground_mode_switch()
        if self.manual_mode and switch_to_keep is not "manual_mode":
            self.manual_mode_switch()
        if self.contour_mode and switch_to_keep is not "contour_mode":
            self.contour_mode_switch()
        if self.contrast_mode and switch_to_keep is not "contrast_mode":
            self.contrast_mode_switch()

    def refresh_text(self):
        self.canvas.itemconfig(self.text, text=self.view_text
                                               + self.action_text
                                               + self.zoom_text
                                               + self.ground_mode_text
                                               + self.mask_mode_text
                                               + self.contrast_mode_text
                                               + self.manual_mode_text)
        # + self.contour_mode_text)

    def get_text(self):
        return self.view_text \
               + self.action_text \
               + self.zoom_text \
               + self.ground_mode_text \
               + self.mask_mode_text \
               + self.contrast_mode_text \
               + self.manual_mode_text

    def rebind(self, which_mode):
        self.turn_all_off_except(which_mode)
        self.follow_the_mouse = self.canvas.bind(
            '<Motion>', lambda e: self.follow_mouse(e, self.vline, self.hline, self.text))
        self.canvas.bind(
            '<Button-1>', lambda e: self.on_click(e))
        self.master.bind(
            '<Escape>', lambda e: self.skip())

    def skip(self):
        self.escaped = True
        for line in [self.vline, self.vline1, self.hline, self.hline1]:
            self.canvas.delete(line)
        self.new_cross(1)
        self.follow_the_mouse = self.canvas.bind(
            '<Motion>', lambda e: self.follow_mouse(e, self.vline, self.hline, self.text))
        # reset clicks and append NADA to box
        self.boxes.append((0, 0, 0, 0))
        self.clicks = []
        self.on_off[self.i] = 0
        self.i = self.i + 1
        self.update_text(self.i)
        self.main_window.images_unscaled.append(Image.open(self.main_window.img_path))
        self.cropbot.append(None)
        if self.i == 4:
            self.master.unbind('<Escape>')
            if len(self.clicks) == 1:
                self.autoscale_finish()

    def reset(self):
        for line in [self.vline, self.vline1, self.hline, self.hline1]:
            self.canvas.delete(line)
        self.canvas.delete(self.text)

    def update_text(self, i):
        if self.main_window.box_settings_var.get() == 0:
            if i == 0:
                self.view_text = "Side\n"
            if i == 1:
                self.view_text = "Front\n"
            if i == 2:
                self.view_text = "Top\n"
            if i == 3:
                self.view_text = "Rear\n"
            self.refresh_text()
            if i == 4:
                self.view_text = "Click to finish\n<CTRL-Z> - undo\n" + self.zoom_text
                self.canvas.itemconfig(self.text, text=self.view_text)
        else:
            if i == 0:
                self.view_text = "Left\n"
            if i == 1:
                self.view_text = "Right\n"
            if i == 2:
                self.view_text = "Front\n"
            if i == 3:
                self.view_text = "Rear\n"
            if i == 4:
                self.view_text = "Top\n"
            if i == 5:
                self.view_text = "Bottom\n"
            self.refresh_text()
            if i == 6:
                self.view_text = "Click to finish\n<CTRL-Z> - undo\n" + self.zoom_text
                self.canvas.itemconfig(self.text, text=self.view_text)


    def follow_mouse(self, event, vline, hline, text):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.canvas.coords(vline, wx0, 0, wx0, 6000)
        self.canvas.coords(hline, 0, wy0, 6000, wy0)
        if self.ground_mode_follow:
            self.canvas.coords(text, wx0 + 70, wy0 + 30)
        else:
            self.canvas.coords(text, wx0 + 70, wy0 + 86)

    def follow_mouse_verti(self, event, line, text):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.canvas.coords(line, wx0, 0, wx0, 6000)
        self.canvas.coords(text, wx0, wy0)

    def follow_mouse_horiz(self, event, line, text):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.canvas.coords(line, 0, wy0, 6000, wy0)
        self.canvas.coords(text, wx0, wy0)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_click(self, event):
        self.master.unbind('+')
        self.master.unbind('-')
        self.zoom_text = "Zoom locked\n"
        self.update_text(self.i)
        self.main_window.box_settings['state'] = 'disabled'
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        if wx0 > self.main_window.img.width():
            wx0 = self.main_window.img.width()
        if wy0 > self.main_window.img.height():
            wy0 = self.main_window.img.height()
        if wx0 < 0:
            wx0 = 0
        if wy0 < 0:
            wy0 = 0
        self.clicks.append([wx0, wy0])
        self.canvas.unbind('<Motion>', self.follow_the_mouse)
        if len(self.clicks) == 1:
            self.master.unbind('<Control-z>')
            self.master.unbind('<Escape>')
            self.new_cross(0)
            self.follow_the_mouse = self.canvas.bind(
                '<Motion>', lambda e: self.follow_mouse(e, self.vline1, self.hline1, self.text))
            self.refresh_text()
            # + self.contour_mode_text)
        if len(self.clicks) == 2:
            self.master.bind('<Control-z>', lambda e: self.control_z())
            self.master.bind('<Escape>', lambda e: self.skip())
            self.boxes.append(
                (min(self.clicks[0][0], self.clicks[1][0]),
                 min(self.clicks[0][1], self.clicks[1][1]),
                 max(self.clicks[0][0], self.clicks[1][0]),
                 max(self.clicks[0][1], self.clicks[1][1])))
            self.follow_the_mouse = self.canvas.bind(
                '<Motion>', lambda e: self.follow_mouse(e, self.vline, self.hline, self.text))
            self.clicks = []
            self.on_off[self.i] = 1
            ## if Ground mode is ON, needs an extra click
            if self.ground_mode:
                self.master.unbind('<Control-z>')
                self.master.unbind('<Escape>')
                self.ground_mode_follow = True
                for line in [self.vline, self.vline1, self.hline, self.hline1]:
                    self.canvas.delete(line)
                self.rect_dash.append(self.canvas.create_rectangle(self.boxes[self.i], dash=(3, 3), outline="gray"))
                self.hline = self.canvas.create_line(0, 0, 6000, 0, dash=(2, 4), fill="red")
                self.canvas.bind('<Button-1>', lambda e: self.on_click_ground_mode(e))
                self.master.unbind('<g>')
                self.canvas.itemconfig(self.text, text='Ground mode: \n click slightly above the ground')
            else:
                for line in [self.vline, self.vline1, self.hline, self.hline1]:
                    self.canvas.delete(line)
                self.new_cross(1)
                self.cropbot.append(CropSizeBot(self, self.boxes[self.i], self.ground_mode, 150))
                if self.mask_mode:
                    self.mask = Masker(self, self.cropbot[-1])
                if self.contrast_mode:
                    self.contraster = ContrastAdjuster(self, self.cropbot[-1])
                self.i = self.i + 1
                self.update_text(self.i)
        if (self.i == 4 and self.main_window.box_settings_var.get() == 0)\
                or (self.i == 6 and self.main_window.box_settings_var.get() == 1):
            self.master.unbind('<Escape>')
            if len(self.clicks) == 1:
                self.autoscale_finish()

    def autoscale_finish(self):
        try:
            autoScaler = AutoScaler(self.main_window.images_unscaled, self.main_window.img_dir,
                                    self.main_window.img_name,
                                    self.on_off)
            messagebox.showinfo(title="Success!",
                                message="The following images are saved in\n" + self.main_window.img_dir
                                        + ":\n\n" + autoScaler.get_views())
            self.main_window.frame_buttons.destroy()
            self.main_window.canvas.destroy()
            self.main_window.root.geometry("400x430")
            self.main_window.__init__(self.main_window.root)
        except Exception as e:
            # print(e)
            messagebox.showwarning(title="WARNING", message="Something went wrong")
            self.main_window.frame_buttons.destroy()
            self.main_window.canvas.destroy()
            self.main_window.root.geometry("400x430")
            self.main_window.__init__(self.main_window.root)

    def on_click_ground_mode(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.clicks_ground_mode.append([wx0, wy0])
        self.canvas.unbind('<Motion>', self.follow_the_mouse)
        self.boxes_ground_mode.append((self.clicks_ground_mode[0][0], self.clicks_ground_mode[0][1], 0, 0))
        self.canvas.delete(self.hline)
        self.new_cross(1)
        self.follow_the_mouse = self.canvas.bind(
            '<Motion>', lambda e: self.follow_mouse(e, self.vline, self.hline, self.text))
        self.clicks_ground_mode = []
        self.cropbot.append(CropSizeBot(self, self.boxes[self.i], self.ground_mode, 128))
        self.boxes_ground_mode = []
        self.on_off[self.i] = 1
        self.i += 1
        self.ground_mode_text = "<G> - Ground mode ON\n"
        self.update_text(self.i)
        self.canvas.bind(
            '<Button-1>', lambda e: self.on_click(e))
        self.master.bind('<Control-z>', lambda e: self.control_z())
        self.master.bind('<Escape>', lambda e: self.skip())
        self.master.bind(
            '<g>', lambda e: self.ground_mode_switch())
        self.ground_mode_follow = False
        self.canvas.delete(self.rect_dash[-1])
        if self.i == 4:
            if len(self.clicks) == 1:
                self.autoscale_finish()

    def new_cross(self, i):
        if i == 1:
            self.vline = self.canvas.create_line(0, 0, 0, 6000, dash=(3, 3), fill="gray")
            self.hline = self.canvas.create_line(0, 0, 6000, 0, dash=(3, 3), fill="gray")
        if i == 0:
            self.vline1 = self.canvas.create_line(0, 0, 0, 6000, dash=(3, 3), fill="gray")
            self.hline1 = self.canvas.create_line(0, 0, 6000, 0, dash=(3, 3), fill="gray")

    def control_z(self):
        if self.i != 0:
            if self.i == 4:
                self.master.bind('<Escape>', lambda e: self.skip())
            self.i = self.i - 1
            del self.main_window.images_unscaled[-1]
            # for line in [self.vline, self.vline1, self.hline, self.hline1]:
            #    self.canvas.delete(line)
            try:
                self.cropbot[-1].remove_rectangle()
                del self.cropbot[-1]
            # not sure about this block
            except:
                try:
                    del self.cropbot[-1]
                except:
                    pass
            # self.canvas.delete(self.rect_dash[-1])
            # del self.rect_dash[-1]
            del self.boxes[-1]
            if self.mask_mode:
                self.mask.confirm(True)
                del self.mask
            if self.contrast_mode:
                self.contraster.confirm(True)
                del self.contraster
            self.update_text(self.i)


class CropSizeBot:
    def __init__(self, lines, boxes, ground_mode, threshold, *box):
        self.lines = lines
        self.img_size = (self.lines.main_window.img_x, self.lines.main_window.img_y)
        self.crop_coord = []
        self.cropped_image_unscaled = None
        self.cropped_images_size = None
        self.boxes = boxes
        self.ground_mode = ground_mode
        self.threshold = threshold
        # try:
        if not box or "contrast" in str(box):
            self.to_BW = self.toBW(self.lines.main_window.img_path)
        self.bgd_color = self.get_bgd_color(self.to_BW)
        if box and "contrast" not in str(box):
            self.to_BW = self.convert_pixels(self.to_BW, box, self.bgd_color)
        if ground_mode:
            self.boxes = self.adjust_box_ground(boxes, self.lines.boxes_ground_mode[0])
            self.crop_coord.append(self.first_pixel_L(self.to_BW, self.bgd_color))
            self.boxes = boxes
        else:
            self.crop_coord.append(self.first_pixel_L(self.to_BW, self.bgd_color))
        self.crop_coord.append(self.first_pixel_T(self.to_BW, self.bgd_color))
        if ground_mode:
            self.boxes = self.adjust_box_ground(boxes, self.lines.boxes_ground_mode[0])
            self.crop_coord.append(self.first_pixel_R(self.to_BW, self.bgd_color))
            self.boxes = boxes
        else:
            self.crop_coord.append(self.first_pixel_R(self.to_BW, self.bgd_color))
        self.crop_coord.append(self.first_pixel_B(self.to_BW, self.bgd_color))
        newbox = self.new_cropbox(self.crop_coord, self.boxes)
        self.rectangle = self.lines.canvas.create_rectangle(list(i + 2 for i in newbox), outline="RED")
        # im = Image.open(self.lines.main_window.img_path).crop(self.scale_newbox(newbox))
        if box:
            del self.lines.main_window.images_unscaled[-1]
        self.lines.main_window.images_unscaled.append(
            Image.open(self.lines.main_window.img_path).crop(box=self.scale_newbox(newbox)))
        # self.lines.main_window.images_unscaled[-1].show()
        # except Exception as e:
        #    messagebox.showerror("ERROR", "Something went wrong!\n"
        #                                  "Continuing to next view")
        #    self.lines.main_window.images_unscaled.append(Image.open(self.lines.main_window.img_path))

    def scale_newbox(self, newbox):
        if self.lines.main_window.scale_factor != 1:
            x1 = 1 / self.lines.main_window.scale_factor * newbox[0] - 5
            y1 = 1 / self.lines.main_window.scale_factor * newbox[1] - 5
            x2 = 1 / self.lines.main_window.scale_factor * newbox[2] + 5
            y2 = 1 / self.lines.main_window.scale_factor * newbox[3] + 5
            # return tuple(1/self.lines.main_window.scale_factor * i for i in newbox)
            return x1, y1, x2, y2
        else:
            return newbox

    def toBW(self, img, *img_update):
        if self.lines.contour_mode:
            im = imread(img)
            im1 = Image.fromarray(ndi.gaussian_filter(im, 6))
            enhancer = ImageEnhance.Contrast(im1)
            im3 = asanyarray(enhancer.enhance(4))
            im = Image.fromarray(feature.canny(im3, sigma=4)).convert("RGBA")
            # Image.fromarray(im3).show()
        else:
            im = Image.open(img).convert("RGBA")
        im.thumbnail(self.img_size)
        bgd = Image.new("RGBA", im.size, (255, 255, 255))
        alpha_composite = Image.alpha_composite(bgd, im)
        gray = alpha_composite.convert("L")
        bw = gray.point(lambda x: 0 if x < self.threshold else 255, '1')
        # bw.show()
        return bw

    def adjust_box_ground(self, boxes, boxes_ground_mode):
        a = list((boxes[i] for i in (0, 1, 2)))
        a.append(min(boxes[3], boxes_ground_mode[1]))
        return a

    def new_cropbox(self, crop_coord, box):
        try:
            if self.lines.manual_mode:
                x1 = box[0]
                y1 = box[1]
                x2 = box[2]
                y2 = box[3]
            else:
                x1 = box[0] + crop_coord[0][0]
                y1 = box[1] + crop_coord[1][1]
                x2 = box[0] + crop_coord[2][0]
                y2 = box[1] + crop_coord[3][1]
            return x1, y1, x2, y2
        except:
            return box

    def shift_rectangle(self, box, offset_x, offset_y):
        return box[0] + offset_x, box[1] + offset_y, box[2] + offset_x, box[3] + offset_y

    def get_bgd_color(self, img):
        im = img.crop(box=self.boxes)
        return im.load()[0, 0]

    def first_pixel_L(self, img, bgcolor):
        im = img.crop(box=self.boxes)
        w, h = im.size
        for x in range(w):
            for y in range(h):
                if im.getpixel((x, y)) != bgcolor:
                    return x, y

    def first_pixel_T(self, img, bgcolor):
        im = img.crop(box=self.boxes)
        w, h = im.size
        for y in range(h):
            for x in range(w):
                if im.getpixel((x, y)) != bgcolor:
                    return x, y

    def first_pixel_R(self, img, bgcolor):
        im = img.crop(box=self.boxes)
        w, h = im.size
        for x in reversed(range(w)):
            for y in reversed(range(h)):
                if im.getpixel((x, y)) != bgcolor:
                    return x+1, y

    def first_pixel_B(self, img, bgcolor):
        im = img.crop(box=self.boxes)
        w, h = im.size
        for y in reversed(range(h)):
            for x in reversed(range(w)):
                if im.getpixel((x, y)) != bgcolor:
                    return x, y+1

    def convert_pixels(self, toBW, box, bgd_color):
        for x in range(int(box[0][0]), min(int(box[0][2]) + 1, int(toBW.width))):
            for y in range(int(box[0][1]), min(int(box[0][3]) + 1, int(toBW.height))):
                toBW.putpixel((x, y), bgd_color)
        return toBW

    def remove_rectangle(self):
        self.lines.canvas.delete(self.rectangle)


class Masker:
    def __init__(self, lines, cropbot):
        self.delta_x = 70
        self.delta_y = 55
        self.lines = lines
        self.canvas = lines.canvas
        self.master = lines.master
        self.cropbot = cropbot
        self.mask_box = []
        self.size = 25
        self.master.unbind('<Escape>')
        self.master.bind('1', lambda e: self.change_size_1(e))
        self.master.bind('2', lambda e: self.change_size_2(e))
        self.master.bind('3', lambda e: self.change_size_3(e))
        self.master.bind('<space>', lambda e: self.confirm(e))
        self.canvas.bind('<Button-1>', lambda e: self.on_click(e))
        self.mask_box.append(self.canvas.create_rectangle(0, 0, 0, 0, fill="Grey", outline="Grey"))
        self.canvas.bind('<Motion>', lambda e: self.follow_mouse(e))

    def on_click(self, event):
        self.mask_box.append(self.canvas.create_rectangle(0, 0, 0, 0, fill="Grey", outline="Grey"))
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        box = (wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)
        # self.__init__(self.lines, self.boxes, self.ground_mode, box)
        self.cropbot.remove_rectangle()
        self.cropbot.__init__(self.cropbot.lines, self.cropbot.boxes, self.cropbot.ground_mode, 150, box)
        self.follow_mouse(event)

    def follow_mouse(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.canvas.coords(self.mask_box[-1], wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)
        self.canvas.itemconfig(self.lines.text, text='Mask mode: click on areas to ignore\n'
                                                     '<1>/<2>/<3> - Change mask size\n'
                                                     '<Space Bar> - Confirm\n'
                                                     '<Ctrl-Z> - Cancel')
        self.canvas.coords(self.lines.text, wx0 + self.delta_x, wy0 + self.delta_y)

    def change_size_1(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.delta_y = 55
        self.size = 25
        self.canvas.coords(self.lines.text, wx0 + self.delta_x, wy0 + self.delta_y)
        self.canvas.coords(self.mask_box[-1], wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)

    def change_size_2(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.delta_y = 80
        self.size = 50
        self.canvas.coords(self.lines.text, wx0 + self.delta_x, wy0 + self.delta_y)
        self.canvas.coords(self.mask_box[-1], wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)

    def change_size_3(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        self.delta_y = 130
        self.size = 100
        self.canvas.coords(self.lines.text, wx0 + self.delta_x, wy0 + self.delta_y)
        self.canvas.coords(self.mask_box[-1], wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)

    def confirm(self, event, *quit):
        if quit:
            self.cropbot.__init__(self.cropbot.lines, self.cropbot.boxes, self.cropbot.ground_mode)
        else:
            self.master.unbind('1')
            self.master.unbind('2')
            self.master.unbind('3')
            self.master.unbind('<space>')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<Motion>')
            self.lines.rebind("all_off")
            self.lines.refresh_text()
        for i in self.mask_box:
            self.canvas.delete(i)


class ContrastAdjuster:
    def __init__(self, lines, cropbot):
        self.threshold = 128
        self.delta_x = 70
        self.delta_y = 55
        self.lines = lines
        self.canvas = lines.canvas
        self.master = lines.master
        self.cropbot = cropbot
        self.mask_box = []
        self.size = 25
        self.master.unbind('<Escape>')
        self.master.bind('-', lambda e: self.reduce_threshold(e))
        self.master.bind('+', lambda e: self.increase_threshold(e))
        self.master.bind('<space>', lambda e: self.confirm(e))
        self.canvas.bind('<Button-1>', lambda e: self.on_click(e))
        self.canvas.bind('<Motion>', lambda e: self.follow_mouse(e))

    def confirm(self, event, *quit):
        if quit:
            self.cropbot.__init__(self.cropbot.lines, self.cropbot.boxes, self.cropbot.ground_mode)
        else:
            self.master.unbind('-')
            self.master.unbind('+')
            self.master.unbind('<space>')
            self.canvas.unbind('<Button-1>')
            self.lines.refresh_text()
            self.lines.rebind("all_off")

    def on_click(self, event):
        pass

    def follow_mouse(self, event):
        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        wx0, wy0 = event.x + x0, event.y + y0
        # self.canvas.coords(self.mask_box[-1], wx0 - self.size, wy0 - self.size, wx0 + self.size, wy0 + self.size)
        self.canvas.itemconfig(self.lines.text, text='Contrast mode: adjust the edge detection threshold with\n'
                                                     '<+> - Increase (includes more bright colors)\n'
                                                     '<-> - Reduce (includes less bright colors)\n'
                                                     'Threshold = ' + str(self.threshold) + '\n'
                                                                                            '<Space Bar> - Confirm')
        self.canvas.coords(self.lines.text, wx0 + self.delta_x, wy0 + self.delta_y)

    def reduce_threshold(self, event):
        self.threshold -= 20
        if self.threshold < 0:
            self.threshold = 0
        self.cropbot.remove_rectangle()
        self.cropbot.__init__(self.cropbot.lines, self.cropbot.boxes, self.cropbot.ground_mode, self.threshold,
                              "contrast")
        self.follow_mouse(event)

    def increase_threshold(self, event):
        self.threshold += 20
        if self.threshold > 255:
            self.threshold = 255
        self.cropbot.remove_rectangle()
        self.cropbot.__init__(self.cropbot.lines, self.cropbot.boxes, self.cropbot.ground_mode, self.threshold,
                              "contrast")
        self.follow_mouse(event)


class AutoScaler:
    def __init__(self, images_unscaled, img_dir, img_name, on_off):
        self.views = ["", "", "", "", "", ""]
        self.on_off = on_off
        ## order is Side - Front - Top -Rear
        # self.get_shortest_length(images_unscaled)
        maxsize_a = min(images_unscaled[0].size[1], images_unscaled[1].size[1], images_unscaled[3].size[1])
        maxsize_b = min(images_unscaled[0].size[0], images_unscaled[2].size[0])
        maxsize_c = min(images_unscaled[1].size[0], images_unscaled[3].size[0], images_unscaled[2].size[1])
        # print(maxsize_a, maxsize_b, maxsize_c)

        if on_off[0] == 1:
            #images_unscaled[0].thumbnail((maxsize_b, maxsize_a))
            a = images_unscaled[0].resize((maxsize_b, maxsize_a))
            #images_unscaled[0].save(img_dir + img_name + "_side.png", "PNG")
            a.save(img_dir + img_name + "_side.png", "PNG")
            self.views[0] = img_name + "_side.png"

        if on_off[1] == 1:
            #images_unscaled[1].thumbnail((maxsize_c, maxsize_a))
            a = images_unscaled[1].resize((maxsize_c, maxsize_a))
            a.save(img_dir + img_name + "_front.png", "PNG")
            self.views[1] = img_name + "_front.png"

        if on_off[2] == 1:
            #images_unscaled[2].thumbnail((maxsize_b, maxsize_c))
            a = images_unscaled[2].resize((maxsize_b, maxsize_c))
            a.save(img_dir + img_name + "_top.png", "PNG")
            self.views[2] = img_name + "_top.png"

        if on_off[3] == 1:
            #images_unscaled[3].thumbnail((maxsize_c, maxsize_a))
            a = images_unscaled[3].resize((maxsize_c, maxsize_a))
            a.save(img_dir + img_name + "_rear.png", "PNG")
            self.views[3] = img_name + "_rear.png"

    def get_views(self):
        a = "\n".join(list(i for i in self.views if i is not ""))
        return a


def main():
    root = Tk()
    icon = ImageTk.PhotoImage(Image.open(resource_path("CROPR_logo.png")))
    root.wm_title("CROPR 0.9.6-beta")
    root.iconphoto(False, icon)
    root.protocol("WM_DELETE_WINDOW")
    main_window = MainWindow(root)
    root.mainloop()


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)


main()
