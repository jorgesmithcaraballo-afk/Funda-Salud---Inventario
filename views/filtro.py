<<<<<<< HEAD
=======
from conexion import obtener_conexion
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
from colors import PRIMARY_BLUE
import customtkinter as ctk
import openpyxl
from openpyxl.styles import Font
from tkinter import filedialog
from services.inventory_queries import InventoryQueries

# datos = self.obtener_datos_inventario()[::-1]
class FiltroView(ctk.CTkFrame):
    def restaurar_tabla(self):
        for widget in self.tabla_scroll.winfo_children():
            widget.destroy()
        
        # IMPORTANTE: Resetear flag cuando se destruyen los widgets
        self.encabezado_creado = False
        
        self.crear_encabezado()  # ← encabezado solo una vez
        datos = self.obtener_datos_inventario()[::-1]
        self.mostrar_resultados(datos)
    
    def exportar_excel(self):
        """
        Exporta el inventario a Excel con diálogo de guardado y feedback
        """
        try:
            import openpyxl
            from openpyxl.styles import Font
            from tkinter import messagebox
            
            # Primero solicitar dónde guardar el archivo
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Guardar inventario como...",
                initialfile="inventario_exportado.xlsx"
            )
            
            # Si el usuario canceló, salir
            if not ruta_archivo:
                return
            
            # Obtener datos del inventario
            datos = self.obtener_datos_inventario()
            
            if not datos:
                messagebox.showwarning("Sin datos", "No hay datos de inventario para exportar.")
                return

            # Crear workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Inventario"

            # Encabezados
            encabezado = [
                "Código", "Descripción",
                "E. Inicial Cant", "E. Inicial Costo", "E. Inicial Monto",
                "Entradas Cant", "Entradas Costo", "Entradas Monto",
                "Salidas Cant", "Salidas Costo", "Salidas Monto",
                "E. Final Cant", "E. Final Costo", "E. Final Monto"
            ]
            ws.append(encabezado)

            # Formatear encabezados en negrita
            for col in ws.iter_cols(min_row=1, max_row=1):
                for cell in col:
                    cell.font = Font(bold=True)

            # Procesar cada item del inventario
            for item in datos:
                codigo = f"C-{item.get('id', '')}"
                descripcion = item.get("descripcion_insumo", "")
                costo_unitario = item.get("costo_unitario") or 0

                # Existencia inicial
                cant_inicial = item.get("ei_cant") or 0
                costo_inicial = item.get("ei_costo") or 0
                monto_inicial = cant_inicial * costo_inicial

                # Entradas
                cant_entrada = item.get("e_cant") or 0
                costo_entrada = item.get("e_costo") or 0
                monto_entrada = cant_entrada * costo_entrada

                # Salidas
                cant_salida = item.get("s_cant") or 0
                costo_salida = item.get("s_costo") or 0
                monto_salida = cant_salida * costo_salida

                # Existencia final (según especificaciones)
                # Columna M: cantidad final = inicial + entradas - salidas
                existencia_final = cant_inicial + cant_entrada - cant_salida
                
                # Columna Q: monto final = monto inicial + monto entradas - monto salidas
                monto_final = monto_inicial + monto_entrada - monto_salida

                # Crear fila de datos
                fila = [
                    codigo, descripcion,
                    cant_inicial, costo_inicial, monto_inicial,
                    cant_entrada, costo_entrada, monto_entrada,
                    cant_salida, costo_salida, monto_salida,
                    existencia_final, costo_unitario, monto_final
                ]
                ws.append(fila)

            # Guardar archivo
            wb.save(ruta_archivo)
            
            # Feedback de éxito
            messagebox.showinfo(
                "Exportación exitosa", 
                f"✅ Inventario exportado correctamente!\n\n"
                f"Archivo guardado en:\n{ruta_archivo}\n\n"
                f"Total de productos: {len(datos)}"
            )
            
        except PermissionError:
            messagebox.showerror(
                "Error de permisos", 
                "❌ No se puede guardar el archivo.\n\n"
                "El archivo podría estar abierto en Excel o no tienes permisos para escribir en esa ubicación."
            )
        except Exception as e:
            messagebox.showerror(
                "Error de exportación", 
                f"❌ Error al exportar a Excel:\n\n{str(e)}\n\n"
                "Intenta de nuevo o contacta al administrador."
            )

    
    def mostrar_resultados(self, datos):
        if not datos:
            mensaje = ctk.CTkLabel(self.tabla_scroll, text="No se encontraron coincidencias.", font=ctk.CTkFont(size=16))
            mensaje.pack(pady=20)
            return

        # self.crear_encabezado()
        
        for item in datos:
            fila = ctk.CTkFrame(self.tabla_scroll, fg_color="#f9f9f9", corner_radius=4)
            fila.pack(pady=4, padx=10, fill="x")

            codigo = f"C-{item.get('id', '')}"
            descripcion = item.get("descripcion_insumo", "")
            costo_unitario = item.get("costo_unitario") or 0

            cant_inicial = item.get("ei_cant") or 0
            cant_entrada = item.get("e_cant") or 0
            cant_salida = item.get("s_cant") or 0

            costo_inicial = item.get("ei_costo") or 0
            costo_entrada = item.get("e_costo") or 0
            costo_salida = item.get("s_costo") or 0

            monto_inicial = cant_inicial * costo_inicial
            monto_entrada = cant_entrada * costo_entrada
            monto_salida = cant_salida * costo_salida
            existencia_final = cant_inicial + cant_entrada - cant_salida
            monto_final = existencia_final * costo_unitario

            bloques = [
                (cant_inicial, costo_inicial, monto_inicial),
                (cant_entrada, costo_entrada, monto_entrada),
                (cant_salida, costo_salida, monto_salida),
                (existencia_final, costo_unitario, monto_final),
            ]

            ctk.CTkLabel(fila, text=codigo, font=ctk.CTkFont(size=14), width=100).pack(side="left")
            ctk.CTkLabel(fila, text=descripcion, font=ctk.CTkFont(size=14), width=180).pack(side="left")

            for cant, costo, monto in bloques:
                bloque_datos = ctk.CTkFrame(fila, fg_color="transparent")
                bloque_datos.pack(side="left", padx=10)

                ctk.CTkLabel(bloque_datos, text=str(cant), font=ctk.CTkFont(size=14), width=60).pack(side="left", padx=2)
                ctk.CTkLabel(bloque_datos, text=f"${costo:.2f}", font=ctk.CTkFont(size=14), width=60).pack(side="left", padx=2)
                ctk.CTkLabel(bloque_datos, text=f"${monto:.2f}", font=ctk.CTkFont(size=14), width=70).pack(side="left", padx=2)

    def crear_encabezado(self):
        if self.encabezado_creado:
            return
        self.encabezado_creado = True
        
        encabezado = ctk.CTkFrame(self.tabla_scroll, fg_color="transparent")
        encabezado.pack(fill="x", pady=10)

        ctk.CTkLabel(
            encabezado,
            text="Código",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100,
        ).pack(side="left")
        ctk.CTkLabel(
            encabezado,
            text="Descripción",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=180,
        ).pack(side="left")

        for bloque in ["E. Inicial", "Entradas", "Salidas", "E. final"]:
            bloque_frame = ctk.CTkFrame(encabezado, fg_color="transparent")
            bloque_frame.pack(side="left", padx=10)
            ctk.CTkLabel(
                bloque_frame, text=bloque, font=ctk.CTkFont(size=14, weight="bold")
            ).pack()
            sub_cols = ctk.CTkFrame(bloque_frame, fg_color="transparent")
            sub_cols.pack()
            ctk.CTkLabel(sub_cols, text="Cant", font=ctk.CTkFont(size=14), width=60).pack(side="left", padx=4)
            ctk.CTkLabel(sub_cols, text="Costo", font=ctk.CTkFont(size=14), width=60).pack(side="left", padx=4)
            ctk.CTkLabel(sub_cols, text="Monto", font=ctk.CTkFont(size=14), width=70).pack(side="left", padx=4)


    def aplicar_filtro(self, texto_busqueda):
        if not texto_busqueda.strip():
            resultados = self.obtener_datos_inventario()
        else:    
            texto_busqueda = texto_busqueda.lower()
            terminos = [t.strip() for t in texto_busqueda.split(";") if t.strip()]
            
            # Obtener todos los datos
            datos = self.obtener_datos_inventario()

            # Filtrar
            resultados = []
            for item in datos:
                cadena = f"{item.get('id', '')} {item.get('descripcion_insumo', '')}".lower()
                if any(termino in cadena for termino in terminos):
                    resultados.append(item)

            # Limpiar tabla y mostrar resultados filtrados
            for widget in self.tabla_scroll.winfo_children():
                widget.destroy()
            self.mostrar_resultados(resultados)

    
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color="white")
        self.encabezado_creado = False

        # Encabezado azul
        encabezado = ctk.CTkFrame(self, fg_color=PRIMARY_BLUE)
        encabezado.place(relx=0.5, rely=0.0, relwidth=1, relheight=0.15, anchor="n")

        btn_subir = ctk.CTkButton(
            encabezado,
            text="⬆️",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color="white",
            text_color="black",
            hover_color="#cccccc",
            command=lambda: self.controlador.mostrar_vista("subir"),
        )
        btn_subir.place(relx=0.02, rely=0.5, anchor="w")

        btn_chat = ctk.CTkButton(
            encabezado,
            text="💬",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color="white",
            text_color="black",
            hover_color="#cccccc",
            command=lambda: self.controlador.mostrar_vista("chat_ai", vista_anterior="filtro"),
        )
        btn_chat.place(relx=0.98, rely=0.5, anchor="e")

        # para poner la vista de herramientas   
        btn_herramientas = ctk.CTkButton(
            encabezado,
            text="🛠️",  # ícono de herramientas
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color="white",
            text_color="black",
            hover_color="#cccccc",
            command=lambda: self.controlador.mostrar_vista("configuracion")
        )
        btn_herramientas.place(relx=0.08, rely=0.5, anchor="w")


        title = ctk.CTkLabel(
            encabezado,
            text="FILTRO Y BÚSQUEDA",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white",
        )
        title.place(relx=0.5, rely=0.5, anchor="center")

        # Encabezado blanco - Zona de filtro
        filtro_panel = ctk.CTkFrame(self, fg_color="white")
        filtro_panel.place(
            relx=0.5, rely=0.16, relwidth=0.9, relheight=0.12, anchor="n"
        )

        filtro_content = ctk.CTkFrame(filtro_panel, fg_color="transparent")
        filtro_content.pack(pady=10)

        filtro_entry = ctk.CTkEntry(
            filtro_content,
            placeholder_text="Buscar...",
            width=400,
            font=ctk.CTkFont(size=22),
        )
        filtro_entry.pack(side="left", padx=10)

        filtro_entry.bind(
            "<Return>", 
            lambda event: self.aplicar_filtro(filtro_entry.get())
        )

        self.select_space = ctk.CTkOptionMenu(
            filtro_content,
            values=["E. Inicial", "Entradas", "Salidas", "E. final"],
            font=ctk.CTkFont(size=20),
            width=280,
            fg_color=PRIMARY_BLUE,
            button_color=PRIMARY_BLUE,
        )
        self.select_space.pack(side="left", padx=10)

        btn_mostrar_todo = ctk.CTkButton(
            filtro_content,
            text="Restaurar tabla",
            font=ctk.CTkFont(size=18),
            width=140,
            fg_color=PRIMARY_BLUE,
            text_color="white",
            hover_color="#0055aa",
            command=self.restaurar_tabla
        )
        btn_mostrar_todo.pack(side="left", padx=10)

        btn_exportar_excel = ctk.CTkButton(
            filtro_content,
            text="Exportar a Excel",
            font=ctk.CTkFont(size=18),
            width=160,
            fg_color="#4CAF50",
            text_color="white",
            hover_color="#45a049",
            command=self.exportar_excel
        )
        btn_exportar_excel.pack(side="left", padx=10)

        # Tabla completa
        # Scrollable tabla
        canvas_frame = ctk.CTkFrame(self, fg_color="white")
        canvas_frame.place(relx=0.5, rely=0.30, relwidth=0.98, relheight=0.68, anchor="n")

        canvas = ctk.CTkCanvas(canvas_frame, bg="white", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Actualizar scroll cuando se agregan elementos
        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_y = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")

        scroll_x = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        # Frame dentro del canvas
        self.tabla_scroll = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=self.tabla_scroll, anchor="nw")

        # Expandir canvas_frame
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.tabla_scroll.bind("<Configure>", actualizar_scroll)

        # mostrar tabla 
        self.restaurar_tabla()

    def obtener_datos_inventario(self):
        """Get base inventory data using centralized queries"""
        return InventoryQueries.get_base_inventory_data()
