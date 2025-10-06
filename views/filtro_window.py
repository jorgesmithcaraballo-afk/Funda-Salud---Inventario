from resource.colors import PRIMARY_BLUE
from services.application.filtro_service import FiltroService
import customtkinter as ctk
from tkinter import filedialog
import threading

class FiltroView(ctk.CTkFrame):
    def restaurar_tabla(self):
        # Limpiar UI y estados
        for widget in self.tabla_scroll.winfo_children():
            widget.destroy()
        self.encabezado_creado = False
        self._current_data = []
        self._render_index = 0
        # Encabezado una sola vez
        self.crear_encabezado()
        # Mostrar indicador de carga y cargar en background
        self._show_loading()
        # Incrementar token de carga para invalidar trabajos anteriores
        self._load_token = getattr(self, '_load_token', 0) + 1
        self._last_query_text = ""
        self._load_inventory_async(query_text=self._last_query_text, category=(self.select_space.get() or 'Todas').strip(), token=self._load_token)
    
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
            
            # Obtener datos del inventario desde el servicio
            datos = self.obtener_datos_inventario()
            
            if not datos:
                messagebox.showwarning("Sin datos", "No hay datos de inventario para exportar.")
                return

            # Delegar exportación al servicio
            from services.application.filtro_service import FiltroService as _FS
            _FS.export_inventory_to_excel(datos, ruta_archivo)
            
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
        # Deprecated en favor de renderizado por lotes; mantener compatibilidad si se llama
        self._current_data = list(reversed(datos)) if datos else []
        self._render_index = 0
        self._render_next_batch()

    def _render_row(self, item):
        fila = ctk.CTkFrame(self.tabla_scroll, fg_color="#f9f9f9", corner_radius=4)
        fila.pack(pady=4, padx=10, anchor="w")

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

        ctk.CTkLabel(fila, text=codigo, font=self._font14, width=100).pack(side="left")
        ctk.CTkLabel(fila, text=descripcion, font=self._font14, width=180).pack(side="left")

        for cant, costo, monto in bloques:
            bloque_datos = ctk.CTkFrame(fila, fg_color="transparent")
            bloque_datos.pack(side="left", padx=10)

            ctk.CTkLabel(bloque_datos, text=str(cant), font=self._font14, width=60).pack(side="left", padx=2)
            ctk.CTkLabel(bloque_datos, text=f"${costo:.2f}", font=self._font14, width=60).pack(side="left", padx=2)
            ctk.CTkLabel(bloque_datos, text=f"${monto:.2f}", font=self._font14, width=70).pack(side="left", padx=2)

    def _render_next_batch(self):
        if not self._current_data:
            # No hay datos
            mensaje = ctk.CTkLabel(self.tabla_scroll, text="No se encontraron coincidencias.", font=self._font16)
            mensaje.pack(pady=20)
            return

        end = min(self._render_index + self._batch_size, len(self._current_data))
        for i in range(self._render_index, end):
            self._render_row(self._current_data[i])
        self._render_index = end

        if self._render_index < len(self._current_data):
            # Continuar automáticamente en el siguiente ciclo para no bloquear
            self.after(1, self._render_next_batch)

    def crear_encabezado(self):
        if self.encabezado_creado:
            return
        self.encabezado_creado = True
        
        encabezado = ctk.CTkFrame(self.tabla_scroll, fg_color="transparent")
        encabezado.pack(anchor="w", pady=10, padx=10)
        # Guardar referencia al encabezado para preservarlo en refrescos
        self._header_frame = encabezado

        ctk.CTkLabel(encabezado, text="Código", font=self._font16b, width=100).pack(side="left")
        ctk.CTkLabel(encabezado, text="Descripción", font=self._font16b, width=180).pack(side="left")

        for bloque in ["E. Inicial", "Entradas", "Salidas", "E. final"]:
            bloque_frame = ctk.CTkFrame(encabezado, fg_color="transparent")
            bloque_frame.pack(side="left", padx=10)
            ctk.CTkLabel(
                bloque_frame, text=bloque, font=ctk.CTkFont(size=14, weight="bold")
            ).pack()
            sub_cols = ctk.CTkFrame(bloque_frame, fg_color="transparent")
            sub_cols.pack()
            ctk.CTkLabel(sub_cols, text="Cant", font=self._font14, width=60).pack(side="left", padx=4)
            ctk.CTkLabel(sub_cols, text="Costo", font=self._font14, width=60).pack(side="left", padx=4)
            ctk.CTkLabel(sub_cols, text="Monto", font=self._font14, width=70).pack(side="left", padx=4)


    def aplicar_filtro(self, texto_busqueda):
        # Limpiar solo filas (preservar encabezado) y mostrar "cargando"
        try:
            for w in self.tabla_scroll.winfo_children():
                if w is getattr(self, '_header_frame', None):
                    continue
                w.destroy()
        except Exception:
            pass
        self._show_loading()

        # Cargar y filtrar en background
        categoria_sel = (self.select_space.get() or 'Todas').strip()
        # Incrementar token para cancelar cargas previas
        self._load_token = getattr(self, '_load_token', 0) + 1
        self._last_query_text = (texto_busqueda or '')
        self._load_inventory_async(query_text=self._last_query_text, category=categoria_sel, token=self._load_token)

    
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color="white")
        self.encabezado_creado = False
        # Estado de renderizado
        self._current_data = []
        self._render_index = 0
        self._batch_size = 100
        self._load_more_btn = None  # deprecado
        self._load_token = 0
        self._last_query_text = ""
        # Auto refresco
        self._auto_refresh_ms = 10000
        self._auto_job = None

        # Cache de fuentes para evitar crear objetos por fila
        self._font14 = ctk.CTkFont(size=14)
        self._font16 = ctk.CTkFont(size=16)
        self._font16b = ctk.CTkFont(size=16, weight="bold")

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
        # Scrollable tabla (scroll vertical único, contenido encapsulado)
        canvas_frame = ctk.CTkFrame(self, fg_color="white")
        canvas_frame.place(relx=0.5, rely=0.30, relwidth=0.98, relheight=0.68, anchor="n")

        canvas = ctk.CTkCanvas(canvas_frame, bg="white", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar vertical
        scroll_y = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        # Scrollbar horizontal
        scroll_x = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Frame dentro del canvas
        self.tabla_scroll = ctk.CTkFrame(canvas, fg_color="white")
        self._tabla_window_id = canvas.create_window((0, 0), window=self.tabla_scroll, anchor="nw")

        # Expandir canvas_frame
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # No forzamos el ancho del contenido al canvas para permitir scroll horizontal real

        # Actualizar región de scroll cuando cambia el contenido
        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.tabla_scroll.bind("<Configure>", actualizar_scroll)

        # Permitir scroll con la rueda del mouse estando sobre cualquier parte de la tabla
        def _on_mousewheel(event):
            try:
                # macOS y Windows usan <MouseWheel> con delta; Linux puede usar Button-4/5
                delta = 0
                if hasattr(event, 'delta') and event.delta:
                    # Escalar delta para una velocidad agradable
                    delta = -int(event.delta/120)
                elif getattr(event, 'num', None) in (4, 5):
                    delta = -1 if event.num == 4 else 1
                if delta:
                    canvas.yview_scroll(delta, 'units')
                return 'break'
            except Exception:
                return 'break'

        # Helper para verificar si el widget origen está dentro de la tabla/canvas
        def _event_within_table(widget) -> bool:
            try:
                w = widget
                while w is not None:
                    if w is self.tabla_scroll or w is canvas:
                        return True
                    w = getattr(w, 'master', None)
            except Exception:
                return False
            return False

        # Bindings de rueda (bind_all con verificación de contención)
        def _wheel_router(event):
            if _event_within_table(event.widget):
                return _on_mousewheel(event)
            return None
        canvas.bind_all('<MouseWheel>', _wheel_router)
        canvas.bind_all('<Button-4>', _wheel_router)
        canvas.bind_all('<Button-5>', _wheel_router)

        # Scroll horizontal con Shift + rueda
        def _on_shift_wheel(event):
            try:
                if hasattr(event, 'delta') and event.delta:
                    delta = -int(event.delta/120)
                else:
                    return 'break'
                if delta:
                    canvas.xview_scroll(delta, 'units')
                return 'break'
            except Exception:
                return 'break'
        def _shift_wheel_router(event):
            if _event_within_table(event.widget):
                return _on_shift_wheel(event)
            return None
        canvas.bind_all('<Shift-MouseWheel>', _shift_wheel_router)

        # Asegurar que el click da el foco al canvas para que la rueda funcione de inmediato
        def _focus_canvas(_):
            try:
                canvas.focus_set()
            except Exception:
                pass
        self.tabla_scroll.bind('<Button-1>', _focus_canvas)
        canvas.bind('<Button-1>', _focus_canvas)

        # --- Scroll por arrastre (click & drag) ---
        def _start_drag_on_canvas(event):
            try:
                canvas.scan_mark(event.x, event.y)
            except Exception:
                pass

        def _drag_on_canvas(event):
            try:
                canvas.scan_dragto(event.x, event.y, gain=1)
            except Exception:
                pass

        def _start_drag_on_inner(event):
            try:
                # Convertir coords del frame interno a coords del canvas
                x = event.x_root - canvas.winfo_rootx()
                y = event.y_root - canvas.winfo_rooty()
                canvas.scan_mark(int(x), int(y))
            except Exception:
                pass

        def _drag_on_inner(event):
            try:
                x = event.x_root - canvas.winfo_rootx()
                y = event.y_root - canvas.winfo_rooty()
                canvas.scan_dragto(int(x), int(y), gain=1)
            except Exception:
                pass

        # Bind arrastre en ambos contenedores
        # Enlazar por defecto y enrutar globalmente para hijos
        canvas.bind('<ButtonPress-1>', _start_drag_on_canvas, add=True)
        canvas.bind('<B1-Motion>', _drag_on_canvas, add=True)
        self.tabla_scroll.bind('<ButtonPress-1>', _start_drag_on_inner, add=True)
        self.tabla_scroll.bind('<B1-Motion>', _drag_on_inner, add=True)

        def _drag_router_press(event):
            if _event_within_table(event.widget):
                return _start_drag_on_inner(event)
            return None
        def _drag_router_motion(event):
            if _event_within_table(event.widget):
                return _drag_on_inner(event)
            return None
        canvas.bind_all('<ButtonPress-1>', _drag_router_press)
        canvas.bind_all('<B1-Motion>', _drag_router_motion)

        # mostrar tabla (no bloqueante)
        self.restaurar_tabla()
        # Iniciar auto-refresh cuando la vista está visible
        try:
            self.bind("<FocusIn>", lambda e: self._restart_auto_refresh())
            self.bind("<Map>", lambda e: self._restart_auto_refresh())
            self.bind("<Unmap>", lambda e: self._cancel_auto_refresh())
        except Exception:
            pass

    def obtener_datos_inventario(self):
        """Get base inventory data using centralized queries"""
        return FiltroService.get_base_inventory_data()

    # ------------------------
    # Carga y filtrado en background
    # ------------------------
    def _show_loading(self) -> None:
        try:
            lbl = ctk.CTkLabel(self.tabla_scroll, text="Cargando...", font=self._font16)
            lbl.pack(pady=12)
            self._loading_label = lbl
        except Exception:
            self._loading_label = None

    def _hide_loading(self) -> None:
        try:
            if getattr(self, '_loading_label', None) is not None:
                self._loading_label.destroy()
                self._loading_label = None
        except Exception:
            pass

    def _load_inventory_async(self, query_text: str, category: str, token: int) -> None:
        """Carga datos y aplica filtros en un hilo, luego renderiza por lotes."""
        def _worker():
            try:
                datos = FiltroService.get_base_inventory_data() or []
                q = (query_text or '').strip().lower()
                terminos = [t.strip() for t in q.split(';') if t.strip()]
                # Filtrado por texto en background
                if terminos:
                    tmp = []
                    for item in datos:
                        cadena = f"{item.get('id', '')} {item.get('descripcion_insumo', '')}".lower()
                        if any(termino in cadena for termino in terminos):
                            tmp.append(item)
                    datos = tmp
                # Filtrado por categoría
                if category and category.lower() != 'todas':
                    datos = [it for it in datos if (it.get('categoria') or 'General') == category]
                # Orden alfabético por descripción
                try:
                    datos.sort(key=lambda r: (r.get('descripcion_insumo') or '').casefold())
                except Exception:
                    pass
            except Exception as e:
                datos = []

            def _apply():
                # Ignorar si hay un token más reciente
                if token != getattr(self, '_load_token', 0):
                    return
                # Quitar loading y limpiar filas previas para evitar duplicados (preservar encabezado)
                try:
                    self._hide_loading()
                    for w in self.tabla_scroll.winfo_children():
                        if w is getattr(self, '_header_frame', None):
                            continue
                        w.destroy()
                except Exception:
                    pass
                # Setear data y renderizar primer lote
                self._current_data = datos
                self._render_index = 0
                self._render_next_batch()

            self.after(0, _apply)

        threading.Thread(target=_worker, daemon=True).start()

    # -------- Auto refresh helpers --------
    def _restart_auto_refresh(self) -> None:
        self._cancel_auto_refresh()
        self._schedule_auto_refresh(delay=1000)

    def _schedule_auto_refresh(self, delay: int = None) -> None:
        try:
            d = self._auto_refresh_ms if delay is None else delay
            self._auto_job = self.after(d, self._auto_refresh_tick)
        except Exception:
            self._auto_job = None

    def _cancel_auto_refresh(self) -> None:
        try:
            if self._auto_job is not None:
                self.after_cancel(self._auto_job)
        except Exception:
            pass
        self._auto_job = None

    def _auto_refresh_tick(self) -> None:
        try:
            # Si la vista no está visible, reprogramar sin recargar
            if not self.winfo_ismapped():
                self._schedule_auto_refresh()
                return
            # Relanzar carga con el último filtro y categoría actual
            self._show_loading()
            self._load_token = getattr(self, '_load_token', 0) + 1
            categoria_sel = (self.select_space.get() or 'Todas').strip()
            self._load_inventory_async(
                query_text=self._last_query_text,
                category=categoria_sel,
                token=self._load_token,
            )
        finally:
            # Programar próximo ciclo
            self._schedule_auto_refresh()

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
            categorias = FiltroService.get_categories() or ["General"]
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
