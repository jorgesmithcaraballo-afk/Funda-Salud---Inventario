from resource.colors import PRIMARY_BLUE
from conexion import obtener_conexion
from services.category_service import CategoryService
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
                codigo = str(item.get('id', ''))
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

            codigo = str(item.get('id', ''))
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
        texto_busqueda = (texto_busqueda or '').strip().lower()
        terminos = [t.strip() for t in texto_busqueda.split(";") if t.strip()]
        categoria_sel = (self.select_space.get() or 'Todas').strip()

        # Obtener todos los datos
        datos = self.obtener_datos_inventario()

        # Filtrar por texto
        if terminos:
            filtrados = []
            for item in datos:
                cadena = f"{item.get('id', '')} {item.get('descripcion_insumo', '')}".lower()
                if any(termino in cadena for termino in terminos):
                    filtrados.append(item)
        else:
            filtrados = datos

        # Filtrar por categoría si no es 'Todas'
        if categoria_sel and categoria_sel.lower() != 'todas':
            filtrados = [it for it in filtrados if (it.get('categoria') or 'General') == categoria_sel]

        # Limpiar tabla y mostrar resultados filtrados conservando encabezado
        for widget in self.tabla_scroll.winfo_children():
            widget.destroy()
        # Reiniciar flag y recrear encabezado
        self.encabezado_creado = False
        self.crear_encabezado()
        self.mostrar_resultados(filtrados)

    
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
        # Botón de configuraciones (visible solo para admin)
        self.btn_herramientas = ctk.CTkButton(
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
        # Guardar posición para reubicar cuando sea necesario
        self._config_btn_place = {"relx": 0.08, "rely": 0.5, "anchor": "w"}
        self.btn_herramientas.place(**self._config_btn_place)

        # Actualizar visibilidad según rol
        self.update_admin_visibility()


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
            values=["Cargando..."],  # se reemplaza por categorías reales
            font=ctk.CTkFont(size=20),
            width=280,
            fg_color=PRIMARY_BLUE,
            button_color=PRIMARY_BLUE,
        )
        self.select_space.pack(side="left", padx=10)
        # Cuando cambie la categoría, aplicar filtro combinado
        self.select_space.configure(command=lambda v: self._on_category_changed())

        # Cargar categorías dinámicamente para otro filtro (si se requiere más adelante)
        self._load_categories()

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

    # --- Control de visibilidad de admin ---
    def update_admin_visibility(self) -> None:
        """Muestra/oculta el botón de configuraciones según el rol del usuario actual."""
        try:
            user = getattr(self.controlador, 'current_user', None) or {}
            es_admin = (user.get('tipo') or 'user') == 'admin'
            if es_admin:
                # Mostrar si está oculto
                if not self.btn_herramientas.winfo_ismapped():
                    self.btn_herramientas.place(**self._config_btn_place)
            else:
                # Ocultar si no es admin
                if self.btn_herramientas.winfo_ismapped():
                    self.btn_herramientas.place_forget()
        except Exception:
            # En caso de error, por seguridad ocultar
            try:
                self.btn_herramientas.place_forget()
            except Exception:
                pass

    def reset_view_state(self) -> None:
        """Método llamado por App.mostrar_vista para refrescar estado de la vista."""
        self.update_admin_visibility()
        # Refrescar categorías al entrar
        try:
            self._load_categories()
        except Exception:
            pass
        # Restaurar la tabla respetando el filtro actual
        try:
            self.aplicar_filtro("")
        except Exception:
            pass

    # ------------------------
    # Carga de categorías desde Inventario
    # ------------------------
    def _load_categories(self) -> None:
        """Carga categorías distintas desde Inventario y actualiza OptionMenu si existe."""
        try:
            categorias = CategoryService.get_all() or ["General"]
        except Exception:
            categorias = ["General"]

        # Si en el futuro usamos select_space para categorías, aquí ya está disponible
        # Por ahora dejamos el control preparado
        try:
            if hasattr(self, 'select_space') and self.select_space is not None:
                opciones = ["Todas"] + categorias
                current = self.select_space.get()
                self.select_space.configure(values=opciones)
                # Mantener selección si sigue existiendo; si no, 'Todas'
                if current in opciones:
                    self.select_space.set(current)
                else:
                    self.select_space.set("Todas")
        except Exception:
            pass

    def _on_category_changed(self) -> None:
        """Handler para cuando cambia la categoría en el OptionMenu: aplica filtro combinado"""
        try:
            # Leer el contenido del entry de búsqueda (si existe)
            # Busco el entry dentro del panel de filtro cercano si lo necesitamos en el futuro.
            self.aplicar_filtro("")
        except Exception:
            self.restaurar_tabla()
