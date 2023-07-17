import tkinter as ttk
import tkinter.messagebox
import customtkinter
from PIL import Image, ImageTk
from utils.WRLML import *
import cv2
import os
import numpy as np
import argparse
import subprocess


#Create the parser
parser = argparse.ArgumentParser()
# Add an argument
parser.add_argument('--cod', type=str, required=True)
parser.add_argument('--usi', type=str, required=True)
parser.add_argument('--vida', type=str, required=True)
parser.add_argument('--site', type=str, required=True)
parser.add_argument('--pais', type=str, required=True)
parser.add_argument('--tipo', type=str, required=True)

# Parse the argument
args = parser.parse_args()

codigo = args.cod
usina = args.usi
vida = args.vida
site = args.site
pais = args.pais
tipo = args.tipo

# codigo = 'args.cod'
# usina = 'args.usi'
# vida = 'args.vida'
# site = 'args.site'
# pais = 'args.pais'
# tipo = 'args.tipo'

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("dark-blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Janela de mensagem
        self.toplevel_window = None

        # configure window
        self.title("WRL Segmentação de Bico")
        self.geometry(f"{1280}x{768}")
        self.attributes('-fullscreen', True)

        self.label_size = 250

        # configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        # self.sidebar_frame.grid_rowconfigure(5, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="WRL", font=customtkinter.CTkFont(
            size=100, weight="bold"), width=self.label_size)
        self.logo_label.grid(row=0, column=0, padx=20,
                             pady=(20, 0), sticky="ew")

        # Botão iniciar segmentação
        self.sidebar_button_1 = customtkinter.CTkButton(
            self.sidebar_frame, command=self.segStart, text="Iniciar Segmentação")
        self.sidebar_button_1.grid(
            row=1, column=0, padx=20, pady=10, sticky="ew")
        self.segStatus = False

        # Campos
        self.grupo = usina
        self.codigo = codigo
        self.vida = vida
        self.site = site

        # root
        self.root = '/home/hewerton/Documentos/WRL_BETA/'
        # Configure gif
        self.path = self.root+"db_images/load.gif"
        self.gifImg = Image.open(self.path)
        self.frames = self.gifImg.n_frames
        self.gifImgFrames = [ttk.PhotoImage(
            file=self.path, format=f"gif -index {i}") for i in range(self.frames)]
        self.count = 0

        # Frame de informações da inspeção
        self.info_frame = customtkinter.CTkFrame(self.sidebar_frame)
        self.info_frame.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.info_label = customtkinter.CTkLabel(self.info_frame, text="Informações Gerais", font=customtkinter.CTkFont(size=20, weight="bold"), width=self.label_size)
        self.info_label.grid(row=0, column=0, padx=10,pady=(20, 10), sticky="ew")
        self.info_desc = customtkinter.CTkLabel(self.info_frame, text=f"Grupo:{self.grupo}\nCódigo: {self.codigo}\nVida: {self.vida}\nSite: {self.site}", font=customtkinter.CTkFont(size=15, weight="normal"), justify="left")
        self.info_desc.grid(row=1, column=0, padx=(0, 0), pady=(0, 20))

        # Frame de Acompanhamento das medições
        self.med_label = customtkinter.CTkLabel(self.info_frame, text="Medições", font=customtkinter.CTkFont(
            size=20, weight="bold"), width=self.label_size)
        self.med_label.grid(row=2, column=0, padx=10,
                            pady=(0, 10), sticky="ew")
        self.med_desc = customtkinter.CTkLabel(self.info_frame, text="Externo: 400.00 mm\nD1: 60.00 mm\nD2: 60.00 mm\nD3: 60.00 mm\nD4: 60.00 mm\nD5: 60.00 mm\nD6: 60.00 mm",font=customtkinter.CTkFont(size=15, weight="normal"), justify="left")
        self.med_desc.grid(row=3, column=0, padx=(0, 0), pady=(0, 20))

        # Botões
        self.sidebar_button_2 = customtkinter.CTkButton(
            self.sidebar_frame, command=self.save_diameters, text="Salvar Diâmetros")
        self.sidebar_button_2.grid(
            row=4, column=0, padx=20, pady=10, sticky="ew")
        self.sidebar_button_3 = customtkinter.CTkButton(
            self.sidebar_frame, command=self.exit, text="Sair")
        self.sidebar_button_3.grid(
            row=5, column=0, padx=20, pady=10, sticky="ew")
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(
            row=7, column=0, padx=20, pady=(10, 10), sticky="ew")
        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20,
                                pady=(10, 0), sticky="ew")
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(
            row=9, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Criação das guias de visualização
        self.tabview = customtkinter.CTkTabview(self, corner_radius=20)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Câmera")
        self.tabview.add("Imagem Segmentada")
        self.tabview.add("Imagem Original")

        self.tabview.tab("Câmera").grid_columnconfigure(
            0, weight=1)  # configure grid of individual tabs
        self.tabview.tab(
            "Imagem Segmentada").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Imagem Original").grid_columnconfigure(0, weight=1)

        # Guia Imagem Segmentada
        self.segImage = ImageTk.PhotoImage(file=self.root+"/test.png")
        self.segImg = customtkinter.CTkLabel(
            self.tabview.tab("Imagem Segmentada"), image=self.segImage, text="")
        # self.segImg.grid(row=0, column=0, padx=0, pady=0, sticky="nswe")
        self.segImg.grid(row=0, column=0, sticky="nswe")

        # Guia Imagem Original
        self.origImage = ImageTk.PhotoImage(file=self.root+"/test.png")
        self.origImg = customtkinter.CTkLabel(
            self.tabview.tab("Imagem Original"), image=self.origImage, text="")
        self.origImg.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        # Streaming Camera
        self.cameraFrame = customtkinter.CTkFrame(
            master=self.tabview.tab("Câmera"))
        self.cameraFrame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        self.camera = customtkinter.CTkLabel(self.cameraFrame, text="",)
        self.camera.grid(row=0, column=0, sticky="nswe")

        # start da câmera
        self.cap = cv2.VideoCapture(0)

        self.onCamera = True
        self.showAnimation = False

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def streaming(self):
        if self.onCamera:
            self.cv2image = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB)
            self.imgRef = np.copy(self.cv2image)
            #self.cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
            #self.cap.set(cv2.CAP_PROP_FPS,60)

            # Inversão da imagem e adição das marcações de alvo
            shapeInvert = (self.cv2image.shape[1], self.cv2image.shape[0])
            centroImag = (int(shapeInvert[0]/2), int(shapeInvert[1]/2))
            cor = (31, 83, 141)
            raio = 200
            y0 = abs(centroImag[1]-raio)
            y1 = centroImag[1]+raio
            x0 = abs(centroImag[0]-raio)
            x1 = centroImag[0]+raio
            cv2.circle(self.cv2image, centroImag, raio, cor, 3)
            cv2.line(self.cv2image, (centroImag[0], y0),
                    (centroImag[0], y1), cor, 3)
            cv2.line(self.cv2image, (x0, centroImag[1]),
                    (x1, centroImag[1]), cor, 3)

            # Redimensionamento para visualização
            self.img = self.resizeImg(self.cv2image)

            self.ImgTks = ImageTk.PhotoImage(image=self.img)
            self.camera.configure(image=self.ImgTks)
            self.camera.grid(row=0, column=0, sticky="nswe")
        self.after(20, self.streaming)

    def getSize(self, img):
        wx = self.winfo_width()
        wx = abs(wx - (self.label_size+160))
        wy = self.winfo_height()
        wy = abs(wy - 130)
        return (wx, wy)

    def playGif(self):
        if self.showAnimation == True:
            if self.count == self.frames-1:
                self.count = 0
            else:
                self.count += 1
            self.gif = self.gifImgFrames[self.count]
            self.camera.configure(image=self.gif)
            self.camera.place(relx=0.5, rely=0.5, anchor='center')
            self.after(30, self.playGif)

    def segStart(self):
        self.onCamera = False
        self.showAnimation = True
        #imageName = self.grupo+'_'+self.codigo+'_'+str(self.vida)+'.jpg'
        # cv2.imwrite(imageName, self.imgRef)
        self.playGif()
        self.segImage= cv2.imread(self.root+"/test.png")
        self.imgRef,diameter, signal = segment(self.segImage)
        self.imgRef = Image.fromarray(self.imgRef)
        self.imgRef = ImageTk.PhotoImage(image=self.imgRef)
        self.segImg.configure(image=self.imgRef)
        self.origImg.configure(image=self.imgRef)
        if signal:
            self.tabview.set("Imagem Segmentada")

    def exit(self):
        app.destroy()
        #process = subprocess.Popen(['python3', 'main.py'], stdout=None, stderr=None)
    
    def save_diameters(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
        else:
            self.toplevel_window.focus()
        self.toplevel_window.grab_set()

    def checkTabs(self):
        if (self.tabview.get() == "Câmera" and self.onCamera == False and self.showAnimation == False):
            self.cap = cv2.VideoCapture(0)
            self.onCamera = True
            self.showAnimation = False

        elif (self.tabview.get() != "Câmera"):
            self.cap.release()
            self.onCamera = False
            self.showAnimation = False
        self.after(10, self.checkTabs)

    def resizeImg(self, img):
        self.size = self.getSize(img)
        img = cv2.resize(
            img, self.size, interpolation=cv2.INTER_LINEAR)
        img = Image.fromarray(img)
        return img

    def responsive(self):
        if self.tabview.get() == "Imagem Segmentada":
            print(self.getSize(self.imgRef))

            try:
                self.imgRef = self.resizeImg(self.imgRef)
            except:
                pass
            self.tab1 = ImageTk.PhotoImage(image=self.imgRef)
            self.segImg.configure(image=self.tab1)
            self.segImg.grid(row=0, column=0, sticky="nswe")
        self.after(15, self.responsive)


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        width = app.winfo_width()//2
        height = app.winfo_height()//2
        self.geometry(f"400x170+{width-50}+{height-100}")
        self.resizable(False,False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=0)
        self.title("")
        self.wm_attributes("-topmost", True) 

        self.msg_frame = customtkinter.CTkFrame(self)
        self.msg_frame.pack(fill=ttk.BOTH, expand=True)
        self.msg_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.msg_label = customtkinter.CTkLabel(self.msg_frame, text="Dados salvos com sucesso!", font=customtkinter.CTkFont(size=20, weight="bold"),width=300)
        self.msg_label.grid(row=0, column=0,padx=20, pady=20, sticky="nsew")

        self.button_1 = customtkinter.CTkButton(self.msg_frame, text="OK", command=self.exit)
        self.button_1.grid(row=1, column=0,padx=20, pady=(0,20), sticky="nsew")


    def exit(self):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.checkTabs()
    app.responsive()
    app.streaming()
    app.mainloop()
