import customtkinter as ctk
from conexion import obtener_conexion
from services.category_service import CategoryService
from resource.colors import (HEADER_BG, VIEW_BACKGROUND, LIGHT_GRAY, WHITE)
from resource.icons import *
from tkinter import messagebox
from typing import Dict, Any, Optional, List

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

        # 🔷 Encabezado con colores unificados
        header = ctk.CTkFrame(self, fg_color=HEADER_BG)
        header.place(relx=0.5, rely=0.0, relwidth=1, relheight=0.15, anchor="n")

        ctk.CTkLabel(header, text="AGREGAR TRABAJO", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

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

        # Cargar códigos de inventario al iniciar
        self._load_inventario_codes()

    def reset_view_state(self) -> None:
        """Llamado al mostrar la vista: recarga inventario y limpia campos si es necesario."""
        self._load_inventario_codes()
        # Limpiar todos los inputs/vars para iniciar en blanco
        try:
            self.codigo_var.set("")
            self.desc_var.set("")
            self.cat_var.set("")
        except Exception:
            pass
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

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Inventario WHERE id = %s", (codigo,))
            existe = cursor.fetchone()[0] > 0

            if not existe:
                cursor.execute(
                    """
                    INSERT INTO Inventario (id, descripcion_insumo, costo_unitario, categoria)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (codigo, descripcion, costo, categoria_sel)
                )
            else:
                if not auto:
                    confirmar = messagebox.askyesno("Código existente", "Este código ya existe. ¿Deseas modificarlo?")
                    if not confirmar:
                        conn.close()
                        return
                cursor.execute(
                    """
                    UPDATE Inventario
                    SET descripcion_insumo = %s, costo_unitario = %s, categoria = %s
                    WHERE id = %s
                    """,
                    (descripcion, costo, categoria_sel, codigo)
                )

            tabla = {
                "E. Inicial": "existencia_inicial",
                "Entradas": "entradas",
                "Salidas": "salidas",
                "E. Final": None
            }.get(categoria)

            if tabla:
                # Verificar si ya existe una fila para ese inventario_id
                cursor.execute(f"SELECT id FROM {tabla} WHERE inventario_id = %s", (codigo,))
                resultado = cursor.fetchone()

                if resultado:
                    # Ya existe → actualizar
                    cursor.execute(f"""
                        UPDATE {tabla}
                        SET cantidad = %s, costo = %s
                        WHERE inventario_id = %s
                    """, (cantidad, costo, codigo))
                else:
                    # No existe → insertar
                    cursor.execute(f"""
                        INSERT INTO {tabla} (inventario_id, cantidad, costo)
                        VALUES (%s, %s, %s)
                    """, (codigo, cantidad, costo))


            conn.commit()
            conn.close()

            if not auto:
                messagebox.showinfo("Éxito", f"Datos guardados en '{categoria}' correctamente.")

        except Exception as e:
            if not auto:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")


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
    def _load_inventario_codes(self) -> None:
        """Carga los códigos del Inventario en el combobox y los guarda en mapa local."""
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT id, descripcion_insumo, costo_unitario, categoria FROM Inventario ORDER BY id ASC")
            rows = cursor.fetchall() or []

            # Construir mapa y valores
            self._inventario_map = {}
            self._desc_label_to_code = {}
            self._code_to_desc_label = {}
            values: List[str] = []
            desc_values: List[str] = []
            seen_desc: Dict[str, int] = {}
            for row in rows:
                # cursor sin dictionary=True devuelve tuplas
                code = str(row[0])
                desc = row[1] if len(row) > 1 else None
                cost = row[2] if len(row) > 2 else None
                cat = row[3] if len(row) > 3 else None
                self._inventario_map[code] = {
                    "descripcion_insumo": desc or "",
                    "costo_unitario": cost if (cost is not None) else "",
                    "categoria": (cat or "General")
                }
                values.append(code)
                # Construir label de descripción manejando duplicados
                base_desc = (desc or "").strip()
                if not base_desc:
                    label = f"(sin descripción) (ID:{code})"
                else:
                    if base_desc in seen_desc:
                        seen_desc[base_desc] += 1
                        label = f"{base_desc} (ID:{code})"
                    else:
                        seen_desc[base_desc] = 1
                        label = base_desc
                self._desc_label_to_code[label] = code
                self._code_to_desc_label[code] = label
                desc_values.append(label)
                # La categoría del registro no determina el catálogo; el ComboBox se llena desde CategoryService

            # Cerrar conexión
            conn.close()

            self._all_code_values = values[:]
            self._all_desc_values = desc_values[:]
            # Categorías exclusivamente desde el catálogo
            try:
                self._all_cat_values = CategoryService.get_all() or ["General"]
            except Exception:
                self._all_cat_values = ["General"]
            self.codigo_cb.configure(values=values)
            self.desc_cb.configure(values=desc_values)
            self.cat_cb.configure(values=self._all_cat_values)
        except Exception as e:
            # No bloquear la UI si falla; el usuario aún puede escribir manualmente
            messagebox.showwarning("Inventario", f"No se pudieron cargar códigos: {e}")

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
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, descripcion_insumo, costo_unitario, categoria FROM Inventario WHERE id = %s",
                (code,)
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            data = {
                "descripcion_insumo": row[1] if len(row) > 1 else "",
                "costo_unitario": row[2] if len(row) > 2 else "",
                "categoria": row[3] if len(row) > 3 else "General",
            }
            # cachear
            self._inventario_map[str(row[0])] = data
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

            # Intentar completar cantidad/costo desde la tabla de la categoría actual
            categoria = self.categoria_var.get()
            tabla = {
                "E. Inicial": "existencia_inicial",
                "Entradas": "entradas",
                "Salidas": "salidas",
                "E. Final": None
            }.get(categoria)
            if tabla:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(f"SELECT cantidad, costo FROM {tabla} WHERE inventario_id = %s", (code,))
                r = cursor.fetchone()
                conn.close()
                if r:
                    cant, costo = r[0], r[1]
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
        text = (self.codigo_var.get() or '').strip().lower()
        if not self._all_code_values:
            return
        if not text:
            self.codigo_cb.configure(values=self._all_code_values)
            self._ensure_dropdown_open(self.codigo_cb)
            return
        filtered = [v for v in self._all_code_values if text in v.lower()]
        self.codigo_cb.configure(values=filtered or self._all_code_values)
        self._ensure_dropdown_open(self.codigo_cb)

    def _on_descripcion_typed(self) -> None:
        """Filtra dinámicamente las descripciones en el ComboBox según lo escrito."""
        text = (self.desc_var.get() or '').strip().lower()
        if not self._all_desc_values:
            return
        if not text:
            self.desc_cb.configure(values=self._all_desc_values)
            self._ensure_dropdown_open(self.desc_cb)
            return
        filtered = [v for v in self._all_desc_values if text in v.lower()]
        self.desc_cb.configure(values=filtered or self._all_desc_values)
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
