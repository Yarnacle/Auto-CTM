import tkinter as tk
import tkinter.filedialog
from tkinter.constants import BOTH, CENTER, HORIZONTAL, LEFT, NSEW, X
from tkinter import ttk
from tkinter import colorchooser
from PIL import Image,ImageTk,ImageDraw,ImageChops
import tempfile
import math
import os
import sys
import shutil

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.iconbitmap(default = resource_path("icon.ico"))
root.title('Minecraft Auto-CTM Texture Tool')
#root.state('zoomed')

overlayWidth = 0
overlayAlpha = 255
color = (0,0,0)

imgFrame = tk.LabelFrame(root,text = 'Block Texture')
outlineFrame = tk.LabelFrame(root,text = 'Outline Editor')

imgLabel = tk.Label(imgFrame)
widthLabel = tk.Label(outlineFrame,text = 'Border Width').grid(row = 0,column = 0)
customWidthLabel = tk.Label(outlineFrame,text = 'Border Width')
customWidthLabel.grid(row = 8,column = 0)
alphaLabel = tk.Label(outlineFrame,text = 'Alpha').grid(row = 1,column = 0)

spacing1 = tk.Label(outlineFrame).grid(row = 3,column = 0,columnspan = 2,sticky = 'NESW')
spacing2 = tk.Label(outlineFrame,text = 'or').grid(row = 5,column = 0,columnspan = 2,sticky = 'NESW')
spacing3 = tk.Label(outlineFrame).grid(row = 6,column = 0,columnspan = 2,sticky = 'NESW')
spacing4 = tk.Label(outlineFrame).grid(row = 9,column = 0,columnspan = 2,sticky = 'NESW')
spacing5 = tk.Label(outlineFrame).grid(row = 10,column = 0,columnspan = 2,sticky = 'NESW')
spacing6 = tk.Label(outlineFrame).grid(row = 11,column = 0,columnspan = 2,sticky = 'NESW')

widthSlider = tk.Scale(outlineFrame,from_ = 0,to = 255,orient = HORIZONTAL)
widthSlider.bind('<ButtonRelease-1>',lambda x:updateWidth())
widthSlider.grid(row = 0,column = 1)
alphaSlider = tk.Scale(outlineFrame,from_ = 0,to = 255,orient = HORIZONTAL)
alphaSlider.bind('<ButtonRelease-1>',lambda x:updateAlpha())
alphaSlider.grid(row = 1,column = 1)
alphaSlider.set(255)
colorButton = tk.Button(outlineFrame,text = 'Custom Color',command = lambda:updateColor()).grid(row = 2,column = 0,columnspan = 2)
generateButton = tk.Button(outlineFrame,text = 'Generate CTM Textures',command = lambda:generate())
generateButton.grid(row = 12,column = 0,columnspan = 2)
uploadCustom = tk.Button(outlineFrame,text = 'Upload Custom Outline',command = lambda:uploadCustom()).grid(row = 7,column = 0,columnspan = 2)
customWidthSlider = tk.Scale(outlineFrame,from_ = 0,to = 255,orient = HORIZONTAL)
customWidthSlider.bind('<ButtonRelease-1>',lambda x:updateCustomWidth())
customWidthSlider.grid(row = 8,column = 1)

bg = Image.new('RGBA',(50,50),'white')
pixels = bg.load()

for i in range(50):
    for j in range(50):
        if (i + j) % 2:
            pixels[i,j] = (200,200,200)
bg = bg.resize((500,500),Image.Resampling.NEAREST)
bgPhotoImage = ImageTk.PhotoImage(bg)
bgLabel = tk.Label(imgFrame,image = bgPhotoImage).grid(row = 0,column = 0)
uploadButton = tk.Button(imgFrame,text = 'Upload',command = lambda:upload()).grid(row = 0,column = 0)

def setSize():
    width,height,X_POS,Y_POS = root.winfo_width(),root.winfo_height(),root.winfo_x(),root.winfo_y() + 7
    root.state('normal')
    root.resizable(0,0)
    root.geometry('%dx%d+%d+%d' % (width,height,X_POS,Y_POS))

def upload():
    global img
    global openImg
    global imgName
    imgName = tk.filedialog.askopenfilename(filetypes = [('PNG','*.png')])
    try:
        openImg = Image.open(imgName)
        img = openImg
        widthSlider.config(to = math.floor(openImg.size[0] / 2))
        customWidthSlider.config(to = math.floor(openImg.size[0] / 2))
    except:
        return None
    display()

def display():
    global img
    factor = min([float(500 / openImg.size[0]),float(500 / openImg.size[1])])
    width = int(openImg.size[0] * factor)
    height = int(openImg.size[1] * factor)
    img = Image.alpha_composite(bg,img.resize((width,height),Image.Resampling.NEAREST).convert('RGBA'))
    img = ImageTk.PhotoImage(img)
    imgLabel = tk.Label(imgFrame,image = img).grid(row = 0,column = 0)
    enable(outlineFrame)

def disable(parent):
    for child in parent.winfo_children():
        if child.winfo_class() != 'Frame':
            child.config(state = 'disabled')
        else:
            disable(child)

def enable(parent):
    for child in parent.winfo_children():
        if child.winfo_class() != 'Frame':
            if child != customWidthSlider and child != customWidthLabel and child != generateButton:
                    child.config(state = 'active')
        elif child.winfo_class() == 'Frame':
            enable(child)

def uploadCustom():
    global outlineImg
    global overlayWidth
    global overlayAlpha
    global img
    widthSlider.set(0)
    alphaSlider.set(255)
    overlayWidth = 0
    overlayAlpha = 255
    color = (0,0,0)
    outlineName = tk.filedialog.askopenfilename(filetypes = [('PNG','*.png')])
    if outlineName:
        if Image.open(outlineName).size[0] == openImg.size[0]:
            try:
                outlineImg = Image.open(outlineName).convert('RGBA')
                generateButton.config(state = 'disabled')
                customWidthSlider.config(state = 'active')
                customWidthLabel.config(state = 'active')
                updateCustomWidth()
                img = openImg
                display()
            except:
                return None
        else:
            tk.messagebox.showinfo(title = 'Alert',message = 'Sizes do not match')

def updateCustomWidth():
    global outline
    global img
    global overlayWidth
    global overlayAlpha
    global color
    global customOverlayWidth
    widthSlider.set(0)
    alphaSlider.set(255)
    overlayWidth = 0
    overlayAlpha = 255
    color = (0,0,0)
    width = openImg.size[0]
    customOverlayWidth = customWidthSlider.get()
    if customWidthSlider.cget('state') == 'normal' or customWidthSlider.cget('state') == 'active':
        try:
            outline = Image.new('RGBA',openImg.size,(0,0,0,0))
            outline.paste(outlineImg.crop((0,0,width,customOverlayWidth)),(0,0,width,customOverlayWidth))
            outline.paste(outlineImg.crop((0,width - customOverlayWidth,width,width)),(0,width - customOverlayWidth,width,width))
            outline.paste(outlineImg.crop((0,customOverlayWidth,customOverlayWidth,width - customOverlayWidth)),(0,customOverlayWidth,customOverlayWidth,width - customOverlayWidth))
            outline.paste(outlineImg.crop((width - customOverlayWidth,customOverlayWidth,width,width - customOverlayWidth)),(width - customOverlayWidth,customOverlayWidth,width,width - customOverlayWidth))
            img = Image.alpha_composite(openImg.convert('RGBA'),outline)
        except:
            pass
        display()
        generateButton.config(state = 'active')

def updateColor():
    global color
    global img
    global outline
    global customOverlayWidth
    customWidthSlider.set(0)
    customOverlayWidth = 0
    generateButton.config(state = 'active')
    color = tk.colorchooser.askcolor(color = 'black',title = 'Choose Color')
    color = color[0]
    try:
        outline = Image.new('RGBA',openImg.size,(0,0,0,0))
        draw = ImageDraw.Draw(outline)
        n = openImg.size[0] - 1
        draw.rectangle((0,0,n,n),outline = (color[0],color[1],color[2],int(overlayAlpha)),width = int(overlayWidth))
        img = Image.alpha_composite(openImg.convert('RGBA'),outline)
        display()
    except:
        pass

def updateWidth():
    global outline
    global overlayWidth
    global img
    global customOverlayWidth
    customWidthSlider.set(0)
    customOverlayWidth = 0
    overlayWidth = widthSlider.get()
    try:
        outline = Image.new('RGBA',openImg.size,(0,0,0,0))
        draw = ImageDraw.Draw(outline)
        n = openImg.size[0] - 1
        draw.rectangle((0,0,n,n),outline = (color[0],color[1],color[2],int(overlayAlpha)),width = int(overlayWidth))
        img = Image.alpha_composite(openImg.convert('RGBA'),outline)
        display()
    except:
        pass
    generateButton.config(state = 'active')

def updateAlpha():
    global outline
    global img
    global overlayAlpha
    global customOverlayWidth
    customWidthSlider.set(0)
    customOverlayWidth = 0
    overlayAlpha = alphaSlider.get()
    try:
        outline = Image.new('RGBA',openImg.size,(0,0,0,0))
        draw = ImageDraw.Draw(outline)
        n = openImg.size[0] - 1
        draw.rectangle((0,0,n,n),outline = (color[0],color[1],color[2],int(overlayAlpha)),width = int(overlayWidth))
        img = Image.alpha_composite(openImg.convert('RGBA'),outline)
        display()
    except:
        pass
    generateButton.config(state = 'active')

def autoEdit(corner00,corner10,corner01,corner11,lengthN,lengthE,lengthS,lengthW,num,isCustom):
    LCLbg = openImg.convert('RGBA')
    width = LCLbg.size[0]
    fg = Image.new('RGBA',(width,width),(0,0,0,0))
    if(isCustom):
        if corner00:
            corner00 = outline.crop((0,0,customOverlayWidth,customOverlayWidth))
            fg.paste(corner00,(0,0,customOverlayWidth,customOverlayWidth))
        if corner10:
            corner10 = outline.crop((width - customOverlayWidth,0,width,customOverlayWidth))
            fg.paste(corner10,(width - customOverlayWidth,0,width,customOverlayWidth))
        if corner01:
            corner01 = outline.crop((0,width - customOverlayWidth,customOverlayWidth,width))
            fg.paste(corner01,(0,width - customOverlayWidth,customOverlayWidth,width))
        if corner11:
            corner11 = outline.crop((width - customOverlayWidth,width - customOverlayWidth,width,width))
            fg.paste(corner11,(width - customOverlayWidth,width - customOverlayWidth,width,width))
        if lengthN:
            lengthN = outline.crop((customOverlayWidth,0,width - customOverlayWidth,customOverlayWidth))
            fg.paste(lengthN,(customOverlayWidth,0,width - customOverlayWidth,customOverlayWidth))
        if lengthE:
            lengthE = outline.crop((width - customOverlayWidth,customOverlayWidth,width,width - customOverlayWidth))
            fg.paste(lengthE,(width - customOverlayWidth,customOverlayWidth,width,width - customOverlayWidth))
        if lengthS:
            lengthS = outline.crop((customOverlayWidth,width - customOverlayWidth,width - customOverlayWidth,width))
            fg.paste(lengthS,(customOverlayWidth,width - customOverlayWidth,width - customOverlayWidth,width))
        if lengthW:
            lengthW = outline.crop((0,customOverlayWidth,customOverlayWidth,width - customOverlayWidth))
            fg.paste(lengthW,(0,customOverlayWidth,customOverlayWidth,width - customOverlayWidth))
    else:
        if corner00:
            corner00 = outline.crop((0,0,overlayWidth,overlayWidth))
            fg.paste(corner00,(0,0,overlayWidth,overlayWidth))
        if corner10:
            corner10 = outline.crop((width - overlayWidth,0,width,overlayWidth))
            fg.paste(corner10,(width - overlayWidth,0,width,overlayWidth))
        if corner01:
            corner01 = outline.crop((0,width - overlayWidth,overlayWidth,width))
            fg.paste(corner01,(0,width - overlayWidth,overlayWidth,width))
        if corner11:
            corner11 = outline.crop((width - overlayWidth,width - overlayWidth,width,width))
            fg.paste(corner11,(width - overlayWidth,width - overlayWidth,width,width))
        if lengthN:
            lengthN = outline.crop((overlayWidth,0,width - overlayWidth,overlayWidth))
            fg.paste(lengthN,(overlayWidth,0,width - overlayWidth,overlayWidth))
        if lengthE:
            lengthE = outline.crop((width - overlayWidth,overlayWidth,width,width - overlayWidth))
            fg.paste(lengthE,(width - overlayWidth,overlayWidth,width,width - overlayWidth))
        if lengthS:
            lengthS = outline.crop((overlayWidth,width - overlayWidth,width - overlayWidth,width))
            fg.paste(lengthS,(overlayWidth,width - overlayWidth,width - overlayWidth,width))
        if lengthW:
            lengthW = outline.crop((0,overlayWidth,overlayWidth,width - overlayWidth))
            fg.paste(lengthW,(0,overlayWidth,overlayWidth,width - overlayWidth))
    LCLbg = Image.alpha_composite(LCLbg,fg)
    LCLbg.save(dir + '/' + os.path.basename(imgName[:len(imgName) - 4]) + '/' + str(num) + '.png',format = 'PNG')

def generate():
    global dir
    dir = tk.filedialog.askdirectory()
    if(bool(dir)):
        try:
            os.mkdir(dir + '/' + os.path.basename(imgName[:len(imgName) - 4]))
        except:
            shutil.rmtree(dir + '/' + os.path.basename(imgName[:len(imgName) - 4]))
        if(overlayWidth == 0):
            autoEdit(True,True,True,True,True,True,True,True,0,True)
            autoEdit(True,True,True,True,True,False,True,True,1,True)
            autoEdit(True,True,True,True,True,False,True,False,2,True)
            autoEdit(True,True,True,True,True,True,True,False,3,True)
            autoEdit(True,True,True,True,True,False,False,True,4,True)
            autoEdit(True,True,True,True,True,True,False,False,5,True)
            autoEdit(True,True,True,True,False,False,False,True,6,True)
            autoEdit(True,True,True,True,True,False,False,False,7,True)
            autoEdit(True,False,True,True,False,False,False,False,8,True)
            autoEdit(True,True,True,False,False,False,False,False,9,True)
            autoEdit(False,True,False,True,False,False,False,False,10,True)
            autoEdit(False,False,True,True,False,False,False,False,11,True)
            autoEdit(True,True,True,True,True,True,False,True,12,True)
            autoEdit(True,True,True,False,True,False,False,True,13,True)
            autoEdit(True,True,False,False,True,False,False,False,14,True)
            autoEdit(True,True,False,True,True,True,False,False,15,True)
            autoEdit(True,True,True,True,False,False,True,True,16,True)
            autoEdit(True,True,True,True,False,True,True,False,17,True)
            autoEdit(True,True,True,True,False,False,True,False,18,True)
            autoEdit(True,True,True,True,False,True,False,False,19,True)
            autoEdit(False,True,True,True,False,False,False,False,20,True)
            autoEdit(True,True,False,True,False,False,False,False,21,True)
            autoEdit(True,True,False,False,False,False,False,False,22,True)
            autoEdit(True,False,True,False,False,False,False,False,23,True)
            autoEdit(True,True,True,True,False,True,False,True,24,True)
            autoEdit(True,False,True,False,False,False,False,True,25,True)
            autoEdit(False,False,False,False,False,False,False,False,26,True)
            autoEdit(False,True,False,True,False,True,False,False,27,True)
            autoEdit(True,True,True,False,False,False,False,True,28,True)
            autoEdit(True,True,False,True,True,False,False,False,29,True)
            autoEdit(True,False,True,True,False,False,False,True,30,True)
            autoEdit(True,True,True,False,True,False,False,False,31,True)
            autoEdit(False,False,False,True,False,False,False,False,32,True)
            autoEdit(False,False,True,False,False,False,False,False,33,True)
            autoEdit(True,False,False,True,False,False,False,False,34,True)
            autoEdit(False,True,True,False,False,False,False,False,35,True)
            autoEdit(True,True,True,True,False,True,True,True,36,True)
            autoEdit(True,False,True,True,False,False,True,True,37,True)
            autoEdit(False,False,True,True,False,False,True,False,38,True)
            autoEdit(False,True,True,True,False,True,True,False,39,True)
            autoEdit(True,False,True,True,False,False,True,False,40,True)
            autoEdit(False,True,True,True,False,True,False,False,41,True)
            autoEdit(False,True,True,True,False,False,True,False,42,True)
            autoEdit(True,True,False,True,False,True,False,False,43,True)
            autoEdit(False,True,False,False,False,False,False,False,44,True)
            autoEdit(True,False,False,False,False,False,False,False,45,True)
            autoEdit(True,True,True,True,False,False,False,False,46,True)
        else:
            autoEdit(True,True,True,True,True,True,True,True,0,False)
            autoEdit(True,True,True,True,True,False,True,True,1,False)
            autoEdit(True,True,True,True,True,False,True,False,2,False)
            autoEdit(True,True,True,True,True,True,True,False,3,False)
            autoEdit(True,True,True,True,True,False,False,True,4,False)
            autoEdit(True,True,True,True,True,True,False,False,5,False)
            autoEdit(True,True,True,True,False,False,False,True,6,False)
            autoEdit(True,True,True,True,True,False,False,False,7,False)
            autoEdit(True,False,True,True,False,False,False,False,8,False)
            autoEdit(True,True,True,False,False,False,False,False,9,False)
            autoEdit(False,True,False,True,False,False,False,False,10,False)
            autoEdit(False,False,True,True,False,False,False,False,11,False)
            autoEdit(True,True,True,True,True,True,False,True,12,False)
            autoEdit(True,True,True,False,True,False,False,True,13,False)
            autoEdit(True,True,False,False,True,False,False,False,14,False)
            autoEdit(True,True,False,True,True,True,False,False,15,False)
            autoEdit(True,True,True,True,False,False,True,True,16,False)
            autoEdit(True,True,True,True,False,True,True,False,17,False)
            autoEdit(True,True,True,True,False,False,True,False,18,False)
            autoEdit(True,True,True,True,False,True,False,False,19,False)
            autoEdit(False,True,True,True,False,False,False,False,20,False)
            autoEdit(True,True,False,True,False,False,False,False,21,False)
            autoEdit(True,True,False,False,False,False,False,False,22,False)
            autoEdit(True,False,True,False,False,False,False,False,23,False)
            autoEdit(True,True,True,True,False,True,False,True,24,False)
            autoEdit(True,False,True,False,False,False,False,True,25,False)
            autoEdit(False,False,False,False,False,False,False,False,26,False)
            autoEdit(False,True,False,True,False,True,False,False,27,False)
            autoEdit(True,True,True,False,False,False,False,True,28,False)
            autoEdit(True,True,False,True,True,False,False,False,29,False)
            autoEdit(True,False,True,True,False,False,False,True,30,False)
            autoEdit(True,True,True,False,True,False,False,False,31,False)
            autoEdit(False,False,False,True,False,False,False,False,32,False)
            autoEdit(False,False,True,False,False,False,False,False,33,False)
            autoEdit(True,False,False,True,False,False,False,False,34,False)
            autoEdit(False,True,True,False,False,False,False,False,35,False)
            autoEdit(True,True,True,True,False,True,True,True,36,False)
            autoEdit(True,False,True,True,False,False,True,True,37,False)
            autoEdit(False,False,True,True,False,False,True,False,38,False)
            autoEdit(False,True,True,True,False,True,True,False,39,False)
            autoEdit(True,False,True,True,False,False,True,False,40,False)
            autoEdit(False,True,True,True,False,True,False,False,41,False)
            autoEdit(False,True,True,True,False,False,True,False,42,False)
            autoEdit(True,True,False,True,False,True,False,False,43,False)
            autoEdit(False,True,False,False,False,False,False,False,44,False)
            autoEdit(True,False,False,False,False,False,False,False,45,False)
            autoEdit(True,True,True,True,False,False,False,False,46,False)
        tk.messagebox.showinfo(title = 'Alert',message = 'Texture generation complete.\n(saved to ' + dir + ')')

imgFrame.grid(row = 1,column = 0,sticky = 'ns')
outlineFrame.grid(row = 1,column = 2,sticky = 'ns')

disable(outlineFrame)

root.after(100,setSize)
tk.mainloop()