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
        self.modo_conectar = False
        self.punto_origen = None
        self.conexiones = []

        # Asociar eventos generales al canvas
        self.canvas.bind("<ButtonPress-1>", self.inicio_drag)
        self.canvas.bind("<B1-Motion>", self.mover_drag)
        self.canvas.bind("<ButtonRelease-1>", self.fin_drag)


    def crear_proceso(self):
        x, y = random.randint(50, 400), random.randint(50, 300)
        tag = f'elemento_{self.element_counter}'
        radio = 40  # Radio del círculo
        # Crear círculo usando create_oval
        circulo = self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, 
                                        fill='#4caf50', outline='black', tags=('proceso', tag))
        texto = self.canvas.create_text(x, y, text='Proceso', fill='white', tags=('proceso', tag))
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
            if self.modo_conectar:
                self.cancelar_conexion()
            return
        tags = self.canvas.gettags(items[0])
        tag_unico = next((t for t in tags if t.startswith('elemento_')), None)

        # Si estamos en modo conexion
        if self.modo_conectar:
            if not tag_unico:
                self.cancelar_conexion()
                return
            
            punto_conexion = self.obtener_punto_conexion(tag_unico, event.x, event.y)

            if not punto_conexion:
                self.cancelar_conexion()
                return

            if not self.punto_origen:
                self.punto_origen = (*punto_conexion, tag_unico)
                print(f"Punto origen establecido: {tag_unico}")
            else:
                if self.punto_origen[2] != tag_unico:
                    linea = self.canvas.create_line(
                        self.punto_origen[0], self.punto_origen[1], punto_conexion[0],punto_conexion[1], 
                        arrow=tk.LAST,
                        fill='black', width=2, 
                        tags='conexion'
                    )

                    origen_lado = self.determinar_lado(self.punto_origen[2], self.punto_origen[0])
                    destino_lado = self.determinar_lado(tag_unico, punto_conexion[0], punto_conexion[1])
                    
                    conexion = {
                        'linea': linea,
                        'origen_tag': self.punto_origen[2],
                        'destino_tag': tag_unico,
                        'origen_lado': self.determinar_lado(self.punto_origen[2], self.punto_origen[0]),
                        'destino_lado': self.determinar_lado(tag_unico, punto_conexion[0], punto_conexion[1])
                    }
                    self.conexiones.append(conexion)
                    print(f'Conexion creada: {self.punto_origen[2]} -> {tag_unico}')

                self.punto_origen = None
                self.modo_conectar = False
                self.canvas.config(cursor="")
                print('Modo conexion desactivado')
            return
        
        if tag_unico:
            self.drag_data['tag'] = tag_unico
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

    def determinar_lado(self, tag, punto_x,punto_y=None):
        """Determina el lado de conexión según el tag y la posición X"""
        centro = self.obtener_centro(tag)
        tags = self.canvas.gettags(tag)

        if 'decision' in tags:
            if not self.punto_origen:
                return 'izquierda' if punto_x < centro[0] else 'derecha'
            else:
                if punto_y is not None:
                    return 'arriba' if punto_y < centro[1] else 'abajo'
                else:
                    return 'arriba'
        return 'centro'


    def mover_drag(self, event):
        tag = self.drag_data['tag']
        if tag:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            self.canvas.move(tag, dx, dy)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y
            self.actualizar_conexiones(tag)

    def actualizar_conexiones(self, tag_movido):
        for conexion in self.conexiones:
            if conexion['origen_tag'] == tag_movido or conexion['destino_tag'] == tag_movido:
                origen_punto = self.calcular_punto_conexion(conexion['origen_tag'], conexion['origen_lado'])
                destino_punto = self.calcular_punto_conexion(conexion['destino_tag'], conexion['destino_lado'])
                self.canvas.coords(conexion['linea'], 
                                origen_punto[0], origen_punto[1], 
                                destino_punto[0], destino_punto[1])
                
    def calcular_punto_conexion(self, tag, lado):
        bbox = self.canvas.bbox(tag)
        centro_x = (bbox[0] + bbox[2]) / 2
        centro_y = (bbox[1] + bbox[3]) / 2

        tags = self.canvas.gettags(tag)

        if 'decision' in tags:
            size = 60
            if lado == 'izquierda':
                return (centro_x - size // 2, centro_y)
            elif lado == 'derecha':
                return (centro_x + size // 2, centro_y)
            elif lado == 'arriba':
                return (centro_x, centro_y - size // 2)
            elif lado == 'abajo':
                return (centro_x, centro_y + size // 2)
        return (centro_x, centro_y)
        
    def obtener_centro(self, tag):
        bbox = self.canvas.bbox(tag)
        return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) / 2)
    
    def obtener_punto_conexion(self,tag,click_x, click_y):
        bbox = self.canvas.bbox(tag)
        if not bbox:
            return None
        
        centro_x = (bbox[0] + bbox[2]) // 2
        centro_y = (bbox[1] + bbox[3]) // 2

        item_con_tag = self.canvas.find_withtag(tag)

        if not item_con_tag:
            return (centro_x, centro_y)

        tags = self.canvas.gettags(item_con_tag[0])

        if 'decision' in tags:
            size = 60
            if not self.punto_origen:
                if click_x < centro_x:
                    return (centro_x - size // 2, centro_y) 
                else:
                    return (centro_x + size // 2, centro_y)
            else:
                if click_y < centro_y:
                    return (centro_x, centro_y - size // 2)
                else:
                    return (centro_x, centro_y + size // 2)
        else:
            return (centro_x, centro_y)

    def limpiar_canvas(self):
        self.canvas.delete("all")
        self.element_counter = 0
        self.modo_conectar = False
        self.punto_origen = None
        self.conexiones = []
        self.canvas.config(cursor="")

    def activar_conexion(self):
        self.modo_conectar = True
        self.punto_origen = None
        self.canvas.config(cursor="crosshair")

    def cancelar_conexion(self):
        self.modo_conectar = False
        self.punto_origen = None
        self.canvas.config(cursor="")
        print('Conexion cancelada')

    def fin_drag(self, event):
        self.drag_data['tag'] = None
        if not self.modo_conectar:
            self.canvas.config(cursor="")
    
# Ejecutar la app
root = tk.Tk()
app = EditorCursograma(root)
root.mainloop()
