import tkinter as tk
import random

class EditorCursograma:
    def __init__(self,root):
        self.root = root
        self.root.title("Editor de Cursogramas")
        self.root.geometry("1000x600")  # Ancho x Alto

        # Sidebar (izquierda)
        self.sidebar = tk.Frame(root, width=200, bg="#f0f0f0")
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="Elementos", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)
        tk.Button(self.sidebar, text="Agregar Proceso", command=self.crear_proceso).pack(pady=5)
        tk.Button(self.sidebar, text='Agregar Decision', command=self.crear_decision).pack(pady=5)
        tk.Button(self.sidebar, text="Conectar Figuras", command=self.activar_conexion).pack(pady=5)
        tk.Button(self.sidebar, text="Cancelar Conexión", command=self.cancelar_conexion).pack(pady=5)
        tk.Button(self.sidebar, text="Limpiar Canvas", command=self.limpiar_canvas).pack(pady=5)


        # -- Canvas Principal -- 
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(side='right',fill='both', expand=True)

        # Drag and drop
        self.drag_data = {'tag': None, 'x': 0, 'y': 0}
        self.element_counter = 0

        # Conexion
        self.modo_conectar = False
        self.punto_origen = None

        # Asociar eventos generales al canvas
        self.canvas.bind("<ButtonPress-1>", self.inicio_drag)
        self.canvas.bind("<B1-Motion>", self.mover_drag)
        self.canvas.bind("<ButtonRelease-1>", self.fin_drag)


    def crear_proceso(self):
        x, y = random.randint(50, 800), random.randint(50, 500)
        tag = f'elemento_{self.element_counter}'
        rect = self.canvas.create_rectangle(x,y,x+120, y+50, fill='#4caf50', tags=('proceso', tag))
        texto = self.canvas.create_text(x + 60,y + 25,text='Proceso', fill='white',tags=('proceso', tag))
        self.element_counter += 1

    def crear_decision(self):
        x, y = random.randint(50, 400), random.randint(50, 300)
        size = 60
        tag = f'elemento_{self.element_counter}'
        points = [
            x, y - size // 2,
            x + size // 2,y,
            x, y + size // 2,
            x - size // 2, y
        ]
        rombo = self.canvas.create_polygon(points, fill='#ff9800', outline='black', tags=('decision', tag))
        texto = self.canvas.create_text(x, y, text='?', fill='white', tags=('decision', tag))
        self.element_counter += 1


    def inicio_drag(self, event):
        items = self.canvas.find_withtag("current")
        if not items:
            return
        tags = self.canvas.gettags(items[0])
        # Busca el tag único del elemento
        tag_unico = next((t for t in tags if t.startswith('elemento_')), None)

        # Si estamos en modo conexion
        if self.modo_conectar:
            if not tag_unico:
                return  # Solo conecta si es una figura válida
            bbox = self.canvas.bbox(tag_unico)
            x = (bbox[0] + bbox[2]) // 2
            y = (bbox[1] + bbox[3]) // 2

            if not self.punto_origen:
                self.punto_origen = (x, y, tag_unico)
            else:
                if self.punto_origen[2] != tag_unico:
                    self.canvas.create_line(
                        self.punto_origen[0], self.punto_origen[1], x, y, arrow=tk.LAST, fill='black', width=2, tags='conexion')
                    self.punto_origen = None
                    self.modo_conectar = False
                    self.canvas.config(cursor="")
        

        if tag_unico:
            self.drag_data['tag'] = tag_unico
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

    def mover_drag(self, event):
        tag = self.drag_data['tag']
        if tag:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            self.canvas.move(tag, dx, dy)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

    def activar_conexion(self):
        self.modo_conectar = True
        self.punto_origen = None
        self.canvas.config(cursor="crosshair")

    def cancelar_conexion(self):
        self.modo_conectar = False
        self.punto_origen = None
        self.canvas.config(cursor="")

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.element_counter = 0
        self.modo_conectar = False
        self.punto_origen = None
        self.canvas.config(cursor="")

    def fin_drag(self, event):
        self.drag_data['tag'] = None
        if not self.modo_conectar:
            self.canvas.config(cursor="")
    
# Ejecutar la app
root = tk.Tk()
app = EditorCursograma(root)
root.mainloop()
