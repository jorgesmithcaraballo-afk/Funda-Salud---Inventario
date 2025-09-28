from resource.colors import (
    PRIMARY_BLUE,
    WHITE,
    TABLE_ROW_ALT_BG,
    SUCCESS_GREEN,
    SUCCESS_GREEN_HOVER,
    get_content_button_style,
)
from services.application.filtro_service import FiltroService
import customtkinter as ctk
from tkinter import filedialog
import threading
from resource.sizes import ENTRY_HEIGHT, CONTENT_SELECT_HEIGHT, CONTENT_SELECT_WIDTH
from views.toolbar import Toolbar
from resource.strings import (
    FILTRO_TITLE,
    BUSCAR_PLACEHOLDER,
    EXCEL_EXPORT_TITLE,
    CODIGO,
    DESCRIPCION,
    E_INICIAL,
    ENTRADAS,
    SALIDAS,
    E_FINAL,
    CARGANDO,
    FILTRO_NO_RESULTS,
)

# Column width configuration (centralized to align header and rows)
WIDTH_CODE = 100
WIDTH_DESCRIPTION = 250
WIDTH_SUB_CANT = 60
WIDTH_SUB_COSTO = 60
WIDTH_SUB_MONTO = 70


class FiltroView(ctk.CTkFrame):

    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color="white")
        # Root grid weights for dynamic resizing
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.encabezado_creado = False
        # Estado de renderizado
        self._current_data = []
        self._render_index = 0
        self._batch_size = 100
        self._load_more_btn = None  # deprecado
        self._load_token = 0
        self._last_query_text = ""
        # Auto refresco
        # self._auto_refresh_ms = 10000
        self._auto_job = None

        # Cache de fuentes para evitar crear objetos por fila
        self._font14 = ctk.CTkFont(size=14)
        self._font16 = ctk.CTkFont(size=16)
        self._font16b = ctk.CTkFont(size=16, weight="bold")

        # Encabezado reutilizable
        self.toolbar = Toolbar(
            self,
            title=FILTRO_TITLE,
            on_go_subir=lambda: self.controlador.mostrar_vista("subir"),
            on_go_chat=lambda: self.controlador.mostrar_vista(
                "chat_ai", vista_anterior="filtro"
            ),
            on_go_config=lambda: self.controlador.mostrar_vista("configuracion"),
        )
        self.toolbar.grid(row=0, column=0, sticky="ew")
        # Configuración inicial de botones y título (puede ser modificada por cada vista al mostrarse)
        try:
            self.toolbar.set_title(FILTRO_TITLE)
            self.toolbar.configure_buttons(
                on_go_subir=lambda: self.controlador.mostrar_vista("subir"),
                on_go_chat=lambda: self.controlador.mostrar_vista(
                    "chat_ai", vista_anterior="filtro"
                ),
                on_go_config=lambda: self.controlador.mostrar_vista("configuracion"),
                show_subir=True,
                show_chat=True,
                show_config=True,
            )
        except Exception:
            pass
        # Visibilidad admin según usuario actual
        try:
            self.toolbar.update_admin_visibility(
                getattr(self.controlador, "current_user", None)
            )
        except Exception:
            pass

        # Encabezado blanco - Zona de filtro
        filtro_panel = ctk.CTkFrame(self, fg_color=WHITE)
        filtro_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 0))
        filtro_panel.grid_columnconfigure(0, weight=1)

        filtro_content = ctk.CTkFrame(filtro_panel, fg_color="transparent")
        filtro_content.grid(row=0, column=0, sticky="n", pady=10)
        filtro_content.grid_columnconfigure(0, weight=0)
        filtro_content.grid_columnconfigure(1, weight=0)
        filtro_content.grid_columnconfigure(2, weight=0)

        filtro_entry = ctk.CTkEntry(
            filtro_content,
            placeholder_text=BUSCAR_PLACEHOLDER,
            width=400,
            height=ENTRY_HEIGHT,
            font=ctk.CTkFont(size=22),
        )
        filtro_entry.grid(row=0, column=0, padx=10)

        filtro_entry.bind(
            "<Return>", lambda event: self.aplicar_filtro(filtro_entry.get())
        )

        self.select_space = ctk.CTkOptionMenu(
            filtro_content,
            values=["Cargando..."],  # se reemplaza por categorías reales
            font=ctk.CTkFont(size=20),
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
            fg_color=PRIMARY_BLUE,
            button_color=PRIMARY_BLUE,
        )
        self.select_space.grid(row=0, column=1, padx=10)
        # Cuando cambie la categoría, aplicar filtro combinado
        self.select_space.configure(command=lambda v: self._on_category_changed())

        # Cargar categorías dinámicamente para otro filtro (si se requiere más adelante)
        self._load_categories()

        _btn_style = get_content_button_style()
        _btn_style = {
            **_btn_style,
            "fg_color": SUCCESS_GREEN,
            "hover_color": SUCCESS_GREEN_HOVER,
            "text_color": "white",
            "font": ctk.CTkFont(size=18, weight="bold"),
        }
        btn_exportar_excel = ctk.CTkButton(
            filtro_content,
            text=EXCEL_EXPORT_TITLE,
            command=self.exportar_excel,
            **_btn_style,
        )
        btn_exportar_excel.grid(row=0, column=2, padx=10)

        # Tabla (sin Canvas): contenedor y scroll interno
        table_container = ctk.CTkFrame(self, fg_color=WHITE)
        table_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Usamos CTkScrollableFrame para mantener desplazamiento sin Canvas
        self.tabla_scroll = ctk.CTkScrollableFrame(table_container, fg_color=WHITE)
        self.tabla_scroll.grid(row=0, column=0, sticky="nsew")
        # Permitir que el contenido interno se expanda horizontalmente
        self.tabla_scroll.grid_columnconfigure(0, weight=1)

        # mostrar tabla (no bloqueante)
        self.restaurar_tabla()
        # El auto-refresh está deshabilitado, se eliminan los bindings.

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
        self._load_token = getattr(self, "_load_token", 0) + 1
        self._last_query_text = ""
        self._load_inventory_async(
            query_text=self._last_query_text,
            category=(self.select_space.get() or "Todas").strip(),
            token=self._load_token,
        )

    def exportar_excel(self):
        """
        Exporta el inventario a Excel delegando la lógica al servicio.
        La vista solo maneja diálogos (ruta y mensajes).
        """
        from tkinter import messagebox

        try:
            # Solicitar dónde guardar el archivo
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Guardar inventario como...",
                initialfile="inventario_exportado.xlsx",
            )
            if not ruta_archivo:
                return

            # Obtener datos desde el servicio (sin lógica en la vista)
            datos = FiltroService.prepare_export_data()
            if not datos:
                messagebox.showwarning(
                    "Sin datos", "No hay datos de inventario para exportar."
                )
                return

            # Exportar usando el servicio
            FiltroService.export_inventory_to_excel(datos, ruta_archivo)

            # Feedback de éxito
            messagebox.showinfo(
                "Exportación exitosa",
                (
                    "✅ Inventario exportado correctamente!\n\n"
                    f"Archivo guardado en:\n{ruta_archivo}\n\n"
                    f"Total de productos: {len(datos)}"
                ),
            )
        except PermissionError:
            messagebox.showerror(
                "Error de permisos",
                (
                    "❌ No se puede guardar el archivo.\n\n"
                    "El archivo podría estar abierto en Excel o no tienes permisos para escribir en esa ubicación."
                ),
            )
        except Exception as e:
            messagebox.showerror(
                "Error de exportación",
                (
                    f"❌ Error al exportar a Excel:\n\n{str(e)}\n\n"
                    "Intenta de nuevo o contacta al administrador."
                ),
            )

    def mostrar_resultados(self, datos):
        # Deprecated en favor de renderizado por lotes; mantener compatibilidad si se llama
        self._current_data = list(reversed(datos)) if datos else []
        self._render_index = 0
        self._render_next_batch()

    # --- Helpers to build subcolumns (header and rows) ---
    def _build_triplet_header(self, parent: ctk.CTkFrame) -> None:
        """Builds the three subcolumn headers: Cant, Costo, Monto."""
        sub_cols = ctk.CTkFrame(parent, fg_color="transparent")
        sub_cols.pack()
        ctk.CTkLabel(sub_cols, text="Cant", font=self._font14, width=WIDTH_SUB_CANT).pack(
            side="left", padx=0
        )
        ctk.CTkLabel(sub_cols, text="Costo", font=self._font14, width=WIDTH_SUB_COSTO).pack(
            side="left", padx=0
        )
        ctk.CTkLabel(sub_cols, text="Monto", font=self._font14, width=WIDTH_SUB_MONTO).pack(
            side="left", padx=0
        )

    def _build_triplet_row(
        self, parent: ctk.CTkFrame, cant: int | float, costo: float, monto: float
    ) -> None:
        """Builds the three subcolumn values for a data row."""
        ctk.CTkLabel(
            parent, text=str(cant), font=self._font14, width=WIDTH_SUB_CANT
        ).pack(side="left", padx=0)
        ctk.CTkLabel(
            parent, text=f"${costo:.2f}", font=self._font14, width=WIDTH_SUB_COSTO
        ).pack(side="left", padx=0)
        ctk.CTkLabel(
            parent, text=f"${monto:.2f}", font=self._font14, width=WIDTH_SUB_MONTO
        ).pack(side="left", padx=0)

    def _render_row(self, item, row_index: int):
        # Alternate row background to improve readability
        bg = WHITE if (row_index % 2 == 0) else TABLE_ROW_ALT_BG
        fila = ctk.CTkFrame(
            self.tabla_scroll, fg_color=bg, corner_radius=4
        )
        # Header está en row=0; las filas empiezan en 1
        fila.grid(row=row_index, column=0, pady=0, padx=0, sticky="ew")
        # Configurar mismas columnas que el encabezado
        fila.grid_columnconfigure(0, weight=0, minsize=WIDTH_CODE)
        fila.grid_columnconfigure(1, weight=1, minsize=WIDTH_DESCRIPTION)  # Descripción fija
        fila.grid_columnconfigure(2, weight=0)
        fila.grid_columnconfigure(3, weight=0)
        fila.grid_columnconfigure(4, weight=0)
        fila.grid_columnconfigure(5, weight=0)

        # Prefer business key 'codigo' for display; fallback to 'id' for legacy rows
        codigo = str(item.get("codigo") or item.get("id", ""))
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
        monto_final = monto_inicial + monto_entrada - monto_salida

        bloques = [
            (cant_inicial, costo_inicial, monto_inicial),
            (cant_entrada, costo_entrada, monto_entrada),
            (cant_salida, costo_salida, monto_salida),
            (existencia_final, costo_unitario, monto_final),
        ]

        ctk.CTkLabel(fila, text=codigo, font=self._font14, width=WIDTH_CODE).grid(
            row=0, column=0, sticky="w"
        )
        # Multi-line description with wrap that adapts to available width (without oversized row height)
        desc_label = ctk.CTkLabel(
            fila,
            text=descripcion,
            font=self._font14,
            width=WIDTH_DESCRIPTION,
            height=36,
            anchor="w",
            justify="left",
        )
        desc_label.grid(row=0, column=1, sticky="w")

        # Update wraplength to the current width of the label to wrap nicely
        def _upd_wrap(e, lbl=desc_label):
            try:
                lbl.configure(wraplength=max(e.width - 4, 50))
            except Exception:
                pass

        desc_label.bind("<Configure>", _upd_wrap)

        for idx, (cant, costo, monto) in enumerate(bloques, start=2):
            bloque_datos = ctk.CTkFrame(fila, fg_color="transparent")
            bloque_datos.grid(row=0, column=idx, padx=0, sticky="w")
            self._build_triplet_row(bloque_datos, cant, costo, monto)

    def _render_next_batch(self):
        if not self._current_data:
            # No hay datos: mostrar mensaje debajo del encabezado (row=1)
            mensaje = ctk.CTkLabel(
                self.tabla_scroll, text=FILTRO_NO_RESULTS, font=self._font16
            )
            mensaje.grid(row=1, column=0, pady=20, padx=10, sticky="w")
            return

        # Paginación centralizada desde servicio
        batch, next_index, has_more = FiltroService.paginate(
            self._current_data, self._render_index, self._batch_size
        )
        # Las filas de datos comienzan en 1 (0 es encabezado)
        row_base = 1
        for offset, item in enumerate(batch):
            row_index = row_base + (self._render_index + offset)
            self._render_row(item, row_index)
        self._render_index = next_index

        if has_more:
            # Continuar automáticamente en el siguiente ciclo para no bloquear
            self.after(1, self._render_next_batch)

    def crear_encabezado(self):
        if self.encabezado_creado:
            return
        self.encabezado_creado = True

        encabezado = ctk.CTkFrame(self.tabla_scroll, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew")
        # Guardar referencia al encabezado para preservarlo en refrescos
        self._header_frame = encabezado

        # Configurar columnas para expansión horizontal (alineadas con filas)
        encabezado.grid_columnconfigure(0, weight=0, minsize=WIDTH_CODE)  # Código
        encabezado.grid_columnconfigure(1, weight=1, minsize=WIDTH_DESCRIPTION)  # Descripción
        encabezado.grid_columnconfigure(2, weight=0)
        encabezado.grid_columnconfigure(3, weight=0)
        encabezado.grid_columnconfigure(4, weight=0)
        encabezado.grid_columnconfigure(5, weight=0)

        encabezadoCodigo = ctk.CTkLabel(
            encabezado, text=CODIGO, font=self._font16b, width=WIDTH_CODE
        )
        encabezadoCodigo.grid(row=0, column=0, sticky="w")
        encabezadoDescrpcion = ctk.CTkLabel(
            encabezado, 
            text=DESCRIPCION, 
            font=self._font16b, width=WIDTH_DESCRIPTION
        )
        encabezadoDescrpcion.grid(row=0, column=1, sticky="w")

        for idx, bloque in enumerate([E_INICIAL, ENTRADAS, SALIDAS, E_FINAL], start=2):
            bloque_frame = ctk.CTkFrame(encabezado, fg_color="transparent")
            bloque_frame.grid(row=0, column=idx, padx=0, sticky="w")
            ctk.CTkLabel(
                bloque_frame, text=bloque, font=ctk.CTkFont(size=14, weight="bold")
            ).pack()
            self._build_triplet_header(bloque_frame)

    def aplicar_filtro(self, texto_busqueda):
        # Limpiar solo filas (preservar encabezado) y mostrar "cargando"
        try:
            for w in self.tabla_scroll.winfo_children():
                if w is getattr(self, "_header_frame", None):
                    continue
                w.destroy()
        except Exception:
            pass
        self._show_loading()

        # Cargar y filtrar en background
        categoria_sel = (self.select_space.get() or "Todas").strip()
        # Incrementar token para cancelar cargas previas
        self._load_token = getattr(self, "_load_token", 0) + 1
        self._last_query_text = texto_busqueda or ""
        self._load_inventory_async(
            query_text=self._last_query_text,
            category=categoria_sel,
            token=self._load_token,
        )

    # ------------------------
    # Carga y filtrado en background
    # ------------------------
    def _show_loading(self) -> None:
        try:
            lbl = ctk.CTkLabel(self.tabla_scroll, text=CARGANDO, font=self._font16)
            lbl.grid(pady=12)
            self._loading_label = lbl
        except Exception:
            self._loading_label = None

    def _hide_loading(self) -> None:
        try:
            if getattr(self, "_loading_label", None) is not None:
                self._loading_label.destroy()
                self._loading_label = None
        except Exception:
            pass

    def _load_inventory_async(self, query_text: str, category: str, token: int) -> None:
        """Carga datos y aplica filtros en un hilo, luego renderiza por lotes."""

        def _worker():
            try:
                datos = FiltroService.get_filtered_inventory(query_text, category)
            except Exception as e:
                datos = []

            def _apply():
                # Ignorar si hay un token más reciente
                if token != getattr(self, "_load_token", 0):
                    return
                # Quitar loading y limpiar filas previas para evitar duplicados (preservar encabezado)
                try:
                    self._hide_loading()
                    for w in self.tabla_scroll.winfo_children():
                        if w is getattr(self, "_header_frame", None):
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

    # --- Control de visibilidad de admin ---
    def update_admin_visibility(self) -> None:
        """Delegates admin visibility to Toolbar."""
        try:
            self.toolbar.update_admin_visibility(
                getattr(self.controlador, "current_user", None)
            )
        except Exception:
            pass

    def reset_view_state(self) -> None:
        """Método llamado por App.mostrar_vista para refrescar estado de la vista."""
        # Configurar título y callbacks específicos de esta vista
        try:
            self.toolbar.set_title("FILTRO Y BÚSQUEDA")
            self.toolbar.configure_buttons(
                on_go_subir=lambda: self.controlador.mostrar_vista("subir"),
                on_go_chat=lambda: self.controlador.mostrar_vista(
                    "chat_ai", vista_anterior="filtro"
                ),
                on_go_config=lambda: self.controlador.mostrar_vista("configuracion"),
                show_subir=True,
                show_chat=True,
                show_config=True,
            )
        except Exception:
            pass
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
            if hasattr(self, "select_space") and self.select_space is not None:
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
