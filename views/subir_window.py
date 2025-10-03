import customtkinter as ctk
from services.application.subir_service import SubirService
from resource.colors import (HEADER_BG, VIEW_BACKGROUND, LIGHT_GRAY, WHITE)
from resource.icons import *
from tkinter import messagebox
from typing import Dict, Any, Optional, List
import threading

class SubirView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color="white")

        # Mapa de inventario en memoria: codigo -> {descripcion_insumo, costo_unitario}
        self._inventario_map: Dict[str, Dict[str, Any]] = {}
        # Mapas para descripción como ComboBox
        self._desc_label_to_code: Dict[str, str] = {}
        self._code_to_desc_label: Dict[str, str] = {}
        # Copias completas para filtrar rápidamente
        self._all_code_values: List[str] = []
        self._all_desc_values: List[str] = []
        self._all_cat_values: List[str] = []

        # Debounce handlers ids
        self._debounce_ids: Dict[str, Optional[str]] = {"codigo": None, "descripcion": None}

        # 🔷 Encabezado con colores unificados
        header = ctk.CTkFrame(self, fg_color=HEADER_BG)
        header.place(relx=0.5, rely=0.0, relwidth=1, relheight=0.15, anchor="n")

        ctk.CTkLabel(header, text="Gestion de Inventarios", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        btn_home = ctk.CTkButton(header, text=ICON_HOME, width=45, height=45, font=ctk.CTkFont(size=22),
            corner_radius=25, fg_color="white", text_color="black", hover_color="#cccccc",
            command=lambda: self.controlador.mostrar_vista("filtro"))
        btn_home.place(relx=0.02, rely=0.5, anchor="w")

        btn_chat = ctk.CTkButton(header, text=ICON_CHAT, width=45, height=45, font=ctk.CTkFont(size=22),
            corner_radius=25, fg_color="white", text_color="black", hover_color="#cccccc",
            command=lambda: self.controlador.mostrar_vista("chat_ai", vista_anterior="subir"))
        btn_chat.place(relx=0.98, rely=0.5, anchor="e")

        # Scrollable formulario
        form_scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        form_scroll.place(relx=0.5, rely=0.18, relwidth=0.9, relheight=0.65, anchor="n")

        form_frame = form_scroll

        # aqui empieza el cambio
        self.categoria_var = ctk.StringVar(value="E. Inicial")
        self.categoria_var.trace_add("write", self.cambio_categoria)

        self.categoria = ctk.CTkOptionMenu(
            form_frame,
            variable=self.categoria_var,
            values=["E. Inicial", "Entradas", "Salidas", "E. Final"],
            font=ctk.CTkFont(size=16),
            width=400,
            fg_color="#00367d",
            button_color="#00367d",
            text_color="white"
        )

        self.categoria.pack(anchor="w", pady=(0, 20))

        # Campos de entrada
        self.inputs = {}
        ctk.CTkLabel(form_frame, text="Código", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
        # Combobox para código: permite escribir y elegir
        self.codigo_var = ctk.StringVar()
        self.codigo_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.codigo_var,
            values=[],  # se llenará desde BD
            width=400,
            font=ctk.CTkFont(size=16),
            command=lambda _: self._on_codigo_selected()
        )
        self.codigo_cb.pack(anchor="w", pady=(0, 10))
        # Permitir Enter para autofill cuando se escribe manualmente
        self.codigo_cb.bind('<Return>', lambda _: self._on_codigo_selected())
        self.inputs["codigo"] = self.codigo_cb

        # Bind para autocompletado en vivo
        # Preferimos enganchar el Entry interno para capturar la escritura
        try:
            (getattr(self.codigo_cb, "_entry")).bind('<KeyRelease>', lambda _: self._on_codigo_typed())
        except Exception:
            self.codigo_cb.bind('<KeyRelease>', lambda _: self._on_codigo_typed())

        # Descripción (ComboBox con escritura y selección)
        ctk.CTkLabel(form_frame, text="Descripción", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
        self.desc_var = ctk.StringVar()
        self.desc_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.desc_var,
            values=[],
            width=400,
            font=ctk.CTkFont(size=16),
            command=lambda _: self._on_descripcion_selected()
        )
        self.desc_cb.pack(anchor="w", pady=(0, 10))
        # Enter para aplicar selección si se escribió manualmente
        self.desc_cb.bind('<Return>', lambda _: self._on_descripcion_selected())
        # Bind para autocompletado en vivo (sobre el Entry interno)
        try:
            (getattr(self.desc_cb, "_entry")).bind('<KeyRelease>', lambda _: self._on_descripcion_typed())
        except Exception:
            self.desc_cb.bind('<KeyRelease>', lambda _: self._on_descripcion_typed())
        self.inputs["descripcion"] = self.desc_cb

        # Categoría (ComboBox con escritura y selección)
        ctk.CTkLabel(form_frame, text="Categoría", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
        self.cat_var = ctk.StringVar()
        self.cat_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.cat_var,
            values=[],
            width=400,
            font=ctk.CTkFont(size=16),
            state="readonly",
            command=lambda _: self._on_categoria_selected()
        )
        self.cat_cb.pack(anchor="w", pady=(0, 10))
        # En modo readonly no permitimos escritura, por lo que no hay binds de tipeo

        # Cantidad
        ctk.CTkLabel(form_frame, text="Cantidad", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
        cant_entry = ctk.CTkEntry(form_frame, width=400, font=ctk.CTkFont(size=16))
        cant_entry.pack(anchor="w", pady=(0, 10))
        self.inputs["cantidad"] = cant_entry

        # Costo
        ctk.CTkLabel(form_frame, text="Costo", font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
        costo_entry = ctk.CTkEntry(form_frame, width=400, font=ctk.CTkFont(size=16))
        costo_entry.pack(anchor="w", pady=(0, 10))
        self.inputs["costo"] = costo_entry

        # ✅ Botón guardar fuera del scroll, centrado
        btn_guardar = ctk.CTkButton(self, text="Guardar", font=ctk.CTkFont(size=18),
            width=200, fg_color="#4CAF50", text_color="white",
            hover_color="#45a049", command=self.guardar_en_db)
        btn_guardar.place(relx=0.5, rely=0.88, anchor="center")

        # Cargar códigos de inventario al iniciar (en hilo para no bloquear UI)
        self._load_inventario_codes_async()

    def reset_view_state(self) -> None:
        """Llamado al mostrar la vista: recarga inventario y limpia campos si es necesario."""
        self._load_inventario_codes_async()
        # Limpiar todos los inputs/vars para iniciar en blanco
        try:
            self.codigo_var.set("")
            self.desc_var.set("")
            self.cat_var.set("")
        except Exception:
            pass

    # Debounce helper
    def _debounced_filter(self, key: str, func) -> None:
        try:
            if self._debounce_ids.get(key) is not None:
                self.after_cancel(self._debounce_ids[key])
        except Exception:
            pass
        self._debounce_ids[key] = self.after(200, func)
        try:
            self.inputs["cantidad"].delete(0, 'end')
            self.inputs["costo"].delete(0, 'end')
        except Exception:
            pass

    
    def guardar_en_db(self, auto=False):
        # Para el combobox usamos get() sobre su variable
        codigo = (self.codigo_var.get() or "").strip()
        # Extraer descripción limpia desde el label del ComboBox (sin sufijo de ID)
        descripcion = self._extract_desc_from_label((self.desc_var.get() or "").strip())
        cantidad = self.inputs["cantidad"].get().strip()
        costo = self.inputs["costo"].get().strip()
        categoria_sel = (self.cat_var.get() or "").strip() or "General"
        categoria = self.categoria_var.get()

        if not all([codigo, descripcion, cantidad, costo, categoria]):
            if not auto:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            cantidad = float(cantidad)
            costo = float(costo)
            if cantidad < 0 or costo < 0:
                raise ValueError
        except ValueError:
            if not auto:
                messagebox.showerror("Error", "Cantidad y costo deben ser números positivos.")
            return

        def _do_save():
            try:
                ok = SubirService.save_inventory_and_movement(
                    code=codigo,
                    descripcion=descripcion,
                    costo_unitario=float(costo),
                    categoria_catalogo=categoria_sel,
                    categoria_movimiento=categoria,
                    cantidad=float(cantidad),
                    costo_mov=float(costo),
                )
                if not auto:
                    # Devolver al hilo UI
                    self.after(0, lambda: (
                        messagebox.showinfo("Éxito", f"Datos guardados en '{categoria}' correctamente.")
                        if ok else messagebox.showwarning("Atención", "No se realizaron cambios.")
                    ))
            except Exception as e:
                if not auto:
                    self.after(0, lambda: messagebox.showerror("Error", f"No se pudo guardar: {e}"))

        # Ejecutar en background cuando es autoguardado; manual puede ir directo o también en hilo
        if auto:
            threading.Thread(target=_do_save, daemon=True).start()
        else:
            threading.Thread(target=_do_save, daemon=True).start()


    def cambio_categoria(self, *args):
        # Verifica si los campos están llenos
        codigo = self.inputs["codigo"].get().strip()
        descripcion = self._extract_desc_from_label((self.desc_var.get() or "").strip())
        cantidad = self.inputs["cantidad"].get().strip()
        costo = self.inputs["costo"].get().strip()

        if all([codigo, descripcion, cantidad, costo]):
            self.guardar_en_db(auto=True)

    # ------------------------
    # Carga y autofill de inventario
    # ------------------------
    def _load_inventario_codes_async(self) -> None:
        """Carga los códigos del Inventario en background y actualiza UI al finalizar."""
        def _worker():
            try:
                values, desc_values, inv_map, label_to_code, code_to_label = SubirService.load_inventario_codes_map()
                try:
                    cats = SubirService.get_categories() or ["General"]
                except Exception:
                    cats = ["General"]

                def _apply():
                    self._inventario_map[:] if isinstance(self._inventario_map, list) else None
                    self._inventario_map = inv_map
                    self._desc_label_to_code = label_to_code
                    self._code_to_desc_label = code_to_label
                    self._all_code_values = list(values)
                    self._all_desc_values = list(desc_values)
                    self._all_cat_values = cats
                    self.codigo_cb.configure(values=self._all_code_values)
                    self.desc_cb.configure(values=self._all_desc_values)
                    self.cat_cb.configure(values=self._all_cat_values)

                self.after(0, _apply)
            except Exception as e:
                self.after(0, lambda: messagebox.showwarning("Inventario", f"No se pudieron cargar códigos: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_codigo_selected(self) -> None:
        """Autocompletar al elegir o ingresar un código y presionar Enter."""
        code = (self.codigo_var.get() or "").strip()
        if not code:
            return
        # Si lo tenemos en cache, usarlo; si no, intentar consultarlo
        data = self._inventario_map.get(code)
        if data is None:
            data = self._fetch_inventory_by_code(code)
        if data:
            self._apply_inventory_to_fields(code, data)

    def _on_descripcion_selected(self) -> None:
        """Cuando se elige una descripción, sincroniza el código y autocompleta."""
        label = (self.desc_var.get() or "").strip()
        if not label:
            return
        code = self._desc_label_to_code.get(label)
        if not code:
            # Si el usuario escribió manualmente una desc que no existe, no sincronizamos código
            return
        self.codigo_var.set(code)
        self._on_codigo_selected()

    def _fetch_inventory_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        try:
            data = SubirService.fetch_inventory_by_code(code)
            if data:
                # cachear
                self._inventario_map[str(code)] = data
            return data
        except Exception:
            return None

    def _apply_inventory_to_fields(self, code: str, data: Dict[str, Any]) -> None:
        """Aplica la descripción/costo del inventario y, si existe registro en la categoría seleccionada, toma cantidad/costo de allí."""
        try:
            # Siempre completar con datos base de Inventario
            # Sincronizar el ComboBox de descripción
            label = self._code_to_desc_label.get(code)
            if label is None:
                # En caso de no tener label (p.ej. código recién escrito), usar la descripción base
                base_desc = data.get("descripcion_insumo") or ""
                label = base_desc
            self.desc_var.set(label)
            base_cost = data.get("costo_unitario")
            if base_cost not in (None, ""):
                self.inputs["costo"].delete(0, 'end')
                self.inputs["costo"].insert(0, str(base_cost))
            # Sincronizar categoría
            cat_val = data.get("categoria") or "General"
            self.cat_var.set(cat_val)

            # Intentar completar cantidad/costo desde la categoría actual vía servicio
            categoria = self.categoria_var.get()
            r = SubirService.get_movement_by_category(code, categoria)
            if r:
                cant, costo = r
                if cant is not None:
                    self.inputs["cantidad"].delete(0, 'end')
                    self.inputs["cantidad"].insert(0, str(cant))
                if costo is not None:
                    self.inputs["costo"].delete(0, 'end')
                    self.inputs["costo"].insert(0, str(costo))
        except Exception:
            # Silencioso para no molestar al usuario si algún SELECT falla
            pass

    # Helpers
    def _extract_desc_from_label(self, label: str) -> str:
        """Devuelve la descripción pura eliminando sufijo ' (ID:xxx)' si existe."""
        if label.endswith(')') and ' (ID:' in label:
            try:
                return label[:label.rfind(' (ID:')]
            except Exception:
                return label
        return label

    def _on_codigo_typed(self) -> None:
        """Filtra dinámicamente los códigos en el ComboBox según lo escrito."""
        # Debounce para evitar filtrar en cada tecla
        self._debounced_filter("codigo", self._apply_codigo_filter)

    def _apply_codigo_filter(self) -> None:
        text = (self.codigo_var.get() or '').strip().lower()
        if not self._all_code_values:
            return
        values = self._all_code_values
        if text:
            values = [v for v in values if text in v.lower()]
        # Limitar tamaño para rendimiento
        limited = values[:500]
        if len(values) > 500:
            limited.append(f"(+{len(values)-500} más…)")
        self.codigo_cb.configure(values=limited)
        self._ensure_dropdown_open(self.codigo_cb)

    def _on_descripcion_typed(self) -> None:
        """Filtra dinámicamente las descripciones en el ComboBox según lo escrito."""
        self._debounced_filter("descripcion", self._apply_descripcion_filter)

    def _apply_descripcion_filter(self) -> None:
        text = (self.desc_var.get() or '').strip().lower()
        if not self._all_desc_values:
            return
        values = self._all_desc_values
        if text:
            values = [v for v in values if text in v.lower()]
        limited = values[:500]
        if len(values) > 500:
            limited.append(f"(+{len(values)-500} más…)")
        self.desc_cb.configure(values=limited)
        self._ensure_dropdown_open(self.desc_cb)

    def _on_categoria_selected(self) -> None:
        # No-op por ahora; la categoría se usa al guardar y al autocompletar desde Inventario
        pass

    def _ensure_dropdown_open(self, cb: ctk.CTkComboBox) -> None:
        """Abre el menú desplegable del ComboBox si está cerrado (best-effort, API interna)."""
        try:
            # CTk 5.x: existe _dropdown_menu con open()/close()
            dm = getattr(cb, "_dropdown_menu", None)
            if dm is not None:
                # Si no está abierto, abrirlo
                if not getattr(dm, "_is_open", False):
                    dm.open()
                return
            # Fallback: usar el toggle interno si existe
            if hasattr(cb, "_open_dropdown_menu"):
                cb._open_dropdown_menu()
                return
            if hasattr(cb, "open_dropdown_menu"):
                cb.open_dropdown_menu()
                return
            if hasattr(cb, "_toggle_dropdown_menu"):
                cb._toggle_dropdown_menu()
        except Exception:
            pass
