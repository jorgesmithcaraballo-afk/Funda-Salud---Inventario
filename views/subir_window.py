import customtkinter as ctk
import re

from services.application.subir_service import SubirService
from resource.colors import (
    LIGHT_GRAY,
    WHITE,
    PRIMARY_BLUE,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    get_content_button_style,
)
from resource.strings import (
    SUBIR_TITLE,
    CODIGO,
    DESCRIPCION,
    CATEGORIA,
    CANTIDAD,
    COSTO,
    GUARDAR,
    SELECCIONAR,
    NUEVO_CODIGO_SUFFIX,
)
from tkinter import messagebox
from typing import Dict, Any, Optional, List
import threading
from resource.sizes import ENTRY_HEIGHT, CONTENT_SELECT_HEIGHT, CONTENT_SELECT_WIDTH
from views.toolbar import Toolbar


class SubirView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color=WHITE)

        # --- State Management ---
        self.inputs = {}
        self._inventario_map: Dict[str, Dict[str, Any]] = {}
        self._desc_label_to_code: Dict[str, str] = {}
        self._code_to_desc_label: Dict[str, str] = {}
        self._all_code_values: List[str] = []
        self._all_desc_values: List[str] = []
        self._all_cat_values: List[str] = []
        self._debounce_ids: Dict[str, Optional[str]] = {
            "codigo": None,
            "descripcion": None,
        }

        # --- Layout Configuration ---
        self.grid_rowconfigure(1, weight=1)  # Main content row expands
        self.grid_columnconfigure(0, weight=1)  # Main column expands

        # --- Build UI Components ---
        self._build_header()
        self._build_form_container()
        self._build_save_button()

        # --- Initial Data Load and Binds ---
        self._load_inventario_codes_async()
        try:
            self.bind("<Visibility>", lambda e: self.reset_view_state())
        except Exception:
            pass

    def _build_header(self):
        # Use reusable Toolbar for header with title centered
        toolbar = Toolbar(
            self,
            title=SUBIR_TITLE,
            on_go_subir=lambda: self.controlador.mostrar_vista("filtro"),
            on_go_chat=lambda: self.controlador.mostrar_vista(
                "chat_ai", vista_anterior="subir"
            ),
            on_go_config=None,
        )
        toolbar.grid(row=0, column=0, sticky="ew")
        # Hide config button for this view
        try:
            toolbar.configure_buttons(show_config=False)
        except Exception:
            pass

    def _build_form_container(self):
        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        form_scroll.grid_columnconfigure(0, weight=1)

        # This frame will hold the form widgets and will be centered
        self.form_content_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        self.form_content_frame.grid(row=0, column=0, sticky="")  # Center the frame

        # Center the content frame within the scrollable area
        form_scroll.grid_rowconfigure(0, weight=1)

        # --- Form Widgets ---
        self._build_form_widgets()

    def _build_form_widgets(self):
        form_frame = self.form_content_frame

        self.categoria_var = ctk.StringVar(value="E. Inicial")
        self.categoria_var.trace_add("write", self.cambio_categoria)

        self.categoria = ctk.CTkOptionMenu(
            form_frame,
            variable=self.categoria_var,
            values=["E. Inicial", "Entradas", "Salidas"],
            font=ctk.CTkFont(size=16),
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
            fg_color=PRIMARY_BLUE,
            button_color=PRIMARY_BLUE,
            text_color=WHITE,
        )
        self.categoria.pack(fill="x", expand=True, pady=(0, 20))

        # --- Form Fields ---
        ctk.CTkLabel(form_frame, text=CODIGO, font=ctk.CTkFont(size=18)).pack(
            anchor="w", pady=(10, 0)
        )
        self.codigo_var = ctk.StringVar()
        self.codigo_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.codigo_var,
            values=[],
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
            dropdown_font=ctk.CTkFont(size=16),
            font=ctk.CTkFont(size=16),
            state="readonly",
            command=lambda _: self._on_codigo_selected(),
        )
        self.codigo_cb.pack(fill="x", expand=True, pady=(0, 10))
        self.inputs["codigo"] = self.codigo_cb

        ctk.CTkLabel(form_frame, text=DESCRIPCION, font=ctk.CTkFont(size=18)).pack(
            anchor="w", pady=(10, 0)
        )
        self.desc_var = ctk.StringVar()
        self.desc_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.desc_var,
            values=[],
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
            dropdown_font=ctk.CTkFont(size=16),
            font=ctk.CTkFont(size=16),
            command=lambda _: self._on_descripcion_selected(),
        )
        self.desc_cb.pack(fill="x", expand=True, pady=(0, 10))
        self.desc_cb.bind("<Return>", lambda _: self._on_descripcion_selected())
        try:
            (getattr(self.desc_cb, "_entry")).bind(
                "<KeyRelease>", lambda _: self._on_descripcion_typed()
            )
        except Exception:
            self.desc_cb.bind("<KeyRelease>", lambda _: self._on_descripcion_typed())
        self.inputs["descripcion"] = self.desc_cb

        ctk.CTkLabel(form_frame, text=CATEGORIA, font=ctk.CTkFont(size=18)).pack(
            anchor="w", pady=(10, 0)
        )
        self.cat_var = ctk.StringVar()
        self.cat_cb = ctk.CTkComboBox(
            form_frame,
            variable=self.cat_var,
            values=[],
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
            dropdown_font=ctk.CTkFont(size=16),
            font=ctk.CTkFont(size=16),
            state="readonly",
            command=lambda _: self._on_categoria_selected(),
        )
        self.cat_cb.pack(fill="x", expand=True, pady=(0, 10))
        self.inputs["categoria_catalogo"] = self.cat_cb  # Renamed for clarity

        ctk.CTkLabel(form_frame, text=CANTIDAD, font=ctk.CTkFont(size=18)).pack(
            anchor="w", pady=(10, 0)
        )
        cant_entry = ctk.CTkEntry(
            form_frame,
            width=400,
            height=ENTRY_HEIGHT,
            font=ctk.CTkFont(size=16),
            placeholder_text="0",
        )
        cant_entry.pack(fill="x", expand=True, pady=(0, 10))
        try:
            cant_entry.bind("<KeyPress>", lambda e: self._on_cantidad_keypress(e))
            cant_entry.bind("<<Paste>>", lambda e: self._on_cantidad_paste())
        except Exception:
            pass
        self.inputs["cantidad"] = cant_entry

        ctk.CTkLabel(form_frame, text=COSTO, font=ctk.CTkFont(size=18)).pack(
            anchor="w", pady=(10, 0)
        )
        costo_entry = ctk.CTkEntry(
            form_frame,
            width=400,
            height=ENTRY_HEIGHT,
            font=ctk.CTkFont(size=16),
            placeholder_text="0,00",
        )
        costo_entry.pack(fill="x", expand=True, pady=(0, 10))
        try:
            costo_entry.bind("<KeyPress>", lambda e: self._on_costo_append_keypress(e))
            costo_entry.bind("<<Paste>>", lambda e: self._on_costo_paste())
            costo_entry.bind("<FocusOut>", lambda e: self._on_costo_focus_out())
        except Exception:
            pass
        self.inputs["costo"] = costo_entry

    def _build_save_button(self):
        _btn_style = get_content_button_style()
        # Keep green semantic for save while unifying size
        _btn_style = {
            **_btn_style,
            "fg_color": SECONDARY_BLUE,
            "hover_color": SECONDARY_BLUE_HOVER,
            "text_color": "white",
            "font": ctk.CTkFont(size=18, weight="bold"),
        }
        btn_guardar = ctk.CTkButton(
            self,
            text=GUARDAR,
            command=self.guardar_en_db,
            **_btn_style,
        )
        btn_guardar.grid(row=2, column=0, pady=20, sticky="s")

    def _on_costo_append_keypress(self, event) -> str | None:
        """Costo: entrada controlada tipo 'append-right'. Solo dígitos, Backspace/Delete.
        Para longitudes >= 3, usa los últimos 2 dígitos como decimales y agrupa miles en la parte entera.
        """
        try:
            keysym = getattr(event, "keysym", "")
            ch = event.char
            entry = self.inputs["costo"]
            # Extraer solo dígitos del valor visible (quita puntos y comas)
            raw = re.sub(r"\D", "", entry.get())
            if keysym in {"BackSpace", "Delete"}:
                raw = raw[:-1]
            elif ch.isdigit():
                raw = (raw or "") + ch
            elif keysym in {"Tab"}:
                return None
            else:
                return "break"
            entry.delete(0, "end")
            entry.insert(0, self._format_price_from_digits(raw))
            entry.icursor("end")
            return "break"
        except Exception:
            return None

        # Cargar códigos de inventario al iniciar (en hilo para no bloquear UI)
        self._load_inventario_codes_async()

    def reset_view_state(self) -> None:
        """Llamado al mostrar la vista: recarga inventario y limpia campos para nuevo registro."""
        try:
            # Limpiar entradas numéricas
            if "cantidad" in self.inputs:
                self.inputs["cantidad"].delete(0, "end")
            if "costo" in self.inputs:
                self.inputs["costo"].delete(0, "end")
            # Restablecer placeholders en combos
            self.desc_var.set(SELECCIONAR)
            self.cat_var.set(SELECCIONAR)
            # Seleccionar el primer valor de código si existe (Nuevo Codigo)
            code_values = []
            try:
                code_values = list(self.codigo_cb.cget("values") or [])
            except Exception:
                pass
            if code_values:
                self.codigo_var.set(code_values[0])
            else:
                self.codigo_var.set("")
        except Exception:
            pass
        # Refrescar datos asíncronos
        self._load_inventario_codes_async()

    # Debounce helper
    def _debounced_filter(self, key: str, func) -> None:
        try:
            if self._debounce_ids.get(key) is not None:
                self.after_cancel(self._debounce_ids[key])
        except Exception:
            pass
        self._debounce_ids[key] = self.after(200, func)

    def guardar_en_db(self, auto=False):
        # Para el combobox usamos get() sobre su variable
        codigo = self._extract_numeric_code((self.codigo_var.get() or "").strip())
        # Extraer descripción limpia desde el label del ComboBox (sin sufijo de ID)
        raw_desc = (self.desc_var.get() or "").strip()
        if raw_desc.lower() == "seleccionar":
            descripcion = ""
        else:
            descripcion = self._extract_desc_from_label(raw_desc)
        cantidad = self.inputs["cantidad"].get().strip()
        costo = self.inputs["costo"].get().strip()
        cat_raw = (self.cat_var.get() or "").strip()
        categoria_sel = (
            "" if cat_raw.lower() == "seleccionar" else cat_raw
        ) or "General"
        categoria = self.categoria_var.get()

        if not all([codigo, descripcion, cantidad, costo, categoria]):
            if not auto:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            # Sanitizar cantidad (entero) y costo (decimal con coma)
            cantidad_val = self._parse_int_thousands(cantidad)
            costo_val = self._parse_decimal_comma(costo)
            cantidad = int(cantidad_val)
            costo = float(costo_val)
            if cantidad < 0 or costo < 0:
                raise ValueError
        except ValueError:
            if not auto:
                messagebox.showerror(
                    "Error", "Cantidad y costo deben ser números positivos."
                )
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
                    self.after(
                        0,
                        lambda: (
                            messagebox.showinfo(
                                "Éxito",
                                f"Datos guardados en '{categoria}' correctamente.",
                            )
                            if ok
                            else messagebox.showwarning(
                                "Atención", "No se realizaron cambios."
                            )
                        ),
                    )
            except Exception as e:
                if not auto:
                    self.after(
                        0,
                        lambda: messagebox.showerror(
                            "Error", f"No se pudo guardar: {e}"
                        ),
                    )

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
                values, desc_values, inv_map, label_to_code, code_to_label = (
                    SubirService.load_inventario_codes_map()
                )
                try:
                    cats = SubirService.get_categories() or ["General"]
                except Exception:
                    cats = ["General"]

                def _apply():
                    (
                        self._inventario_map[:]
                        if isinstance(self._inventario_map, list)
                        else None
                    )
                    # Asegurar claves string para acceso consistente
                    try:
                        self._inventario_map = {
                            str(k): v for k, v in (inv_map or {}).items()
                        }
                    except Exception:
                        self._inventario_map = inv_map
                    self._desc_label_to_code = label_to_code
                    self._code_to_desc_label = code_to_label
                    # Ordenar listas: códigos numéricos, descripciones y categorías alfabéticamente
                    self._all_code_values = self._sort_codes_numeric(list(values))
                    self._all_desc_values = [SELECCIONAR] + sorted(
                        list(desc_values), key=lambda s: (s or "").casefold()
                    )
                    self._all_cat_values = [SELECCIONAR] + sorted(
                        cats, key=lambda s: (s or "").casefold()
                    )
                    # Calcular siguiente código numérico y construir primer opción "(Nuevo Codigo)"
                    next_label = self._compute_next_code_label(self._all_code_values)
                    # Armar lista final: Primero nuevo código, luego existentes como solo número
                    final_code_values = [next_label] + [
                        str(v) for v in self._all_code_values
                    ]
                    self.codigo_cb.configure(values=final_code_values)
                    # Usar lista final y preseleccionar el nuevo código
                    self.codigo_var.set(next_label)
                    self.desc_cb.configure(values=self._all_desc_values)
                    self.cat_cb.configure(values=self._all_cat_values)
                    # Establecer placeholders emulados en variables
                    self.desc_var.set(SELECCIONAR)
                    self.cat_var.set(SELECCIONAR)
                    # Hacer readonly el combobox de código
                    self.codigo_cb.configure(state="readonly")

                self.after(0, _apply)
            except Exception as e:
                self.after(
                    0,
                    lambda: messagebox.showwarning(
                        "Inventario", f"No se pudieron cargar códigos: {str(e)}"
                    ),
                )

        threading.Thread(target=_worker, daemon=True).start()

    def _on_codigo_selected(self) -> None:
        """Autocompletar al elegir o ingresar un código y presionar Enter."""
        code = self._extract_numeric_code((self.codigo_var.get() or "").strip())
        if not code:
            return
        # Si lo tenemos en cache, usarlo; si no, intentar consultarlo
        data = self._inventario_map.get(str(code))
        if data is None:
            data = self._fetch_inventory_by_code(code)
        if data:
            self._apply_inventory_to_fields(code, data)
        else:
            # Código nuevo o inexistente: limpiar campos dependientes
            try:
                self.desc_var.set("Seleccionar")
                self.cat_var.set("Seleccionar")
                self.inputs["cantidad"].delete(0, "end")
                self.inputs["costo"].delete(0, "end")
            except Exception:
                pass

    def _on_descripcion_selected(self) -> None:
        """Cuando se elige una descripción, sincroniza el código y autocompleta."""
        label = (self.desc_var.get() or "").strip()
        if not label:
            return
        if label.lower() == SELECCIONAR.lower():
            return
        code = self._desc_label_to_code.get(label)
        if not code:
            # Si el usuario escribió manualmente una desc que no existe, no sincronizamos código
            return
        # Establecer selección de código; respetar prefijo "(Nuevo Codigo)" solo para el primero
        self.codigo_var.set(str(code))
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
                self.inputs["costo"].delete(0, "end")
                # Mostrar con miles '.' y decimales ','
                self.inputs["costo"].insert(
                    0, self._format_decimal_comma(str(base_cost))
                )
            # Sincronizar categoría
            cat_val = data.get("categoria") or "General"
            self.cat_var.set(cat_val)

            # Intentar completar cantidad/costo desde la categoría actual vía servicio
            categoria = self.categoria_var.get()
            r = SubirService.get_movement_by_category(code, categoria)
            # Limpiar siempre el campo de cantidad antes de decidir qué poner
            self.inputs["cantidad"].delete(0, "end")

            if r and r[0] is not None and int(r[0]) > 0:
                # Caso 1: Hay movimiento en la categoría con cantidad > 0
                cant, costo = r
                self.inputs["cantidad"].insert(0, self._format_thousands(str(cant)))
                if costo is not None:
                    self.inputs["costo"].delete(0, "end")
                    self.inputs["costo"].insert(
                        0, self._format_decimal_comma(str(costo))
                    )
            else:
                # Caso 2: No hay movimiento o la cantidad es 0/None. Usar cantidad base del inventario.
                base_qty = data.get("cantidad")
                if base_qty is not None and int(base_qty) > 0:
                    self.inputs["cantidad"].insert(
                        0, self._format_thousands(str(base_qty))
                    )
                else:
                    # Caso 3: Ni el movimiento ni el inventario base tienen cantidad. Poner '0'.
                    self.inputs["cantidad"].insert(0, "0")
        except Exception:
            # Silencioso para no molestar al usuario si algún SELECT falla
            pass

    # Helpers
    def _extract_desc_from_label(self, label: str) -> str:
        """Devuelve la descripción pura eliminando sufijo ' (ID:xxx)' si existe."""
        if label.endswith(")") and " (ID:" in label:
            try:
                return label[: label.rfind(" (ID:")]
            except Exception:
                return label
        return label

    def _on_codigo_typed(self) -> None:
        """Deprecated: código es readonly, no se filtra por tipeo."""
        return

    def _apply_codigo_filter(self) -> None:
        """Deprecated: código es readonly, sin filtro dinámico."""
        return

    def _on_descripcion_typed(self) -> None:
        """Filtra dinámicamente las descripciones en el ComboBox según lo escrito."""
        self._debounced_filter("descripcion", self._apply_descripcion_filter)

    def _apply_descripcion_filter(self) -> None:
        text = (self.desc_var.get() or "").strip().lower()
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

    # --- Utilidades para manejar el nuevo comportamiento de Código ---
    def _extract_numeric_code(self, value: str) -> str:
        """Devuelve solo el número del código, removiendo sufijo ' (Nuevo Codigo)' si existe."""
        if not value:
            return value
        # Si trae el sufijo, el número va antes del primer espacio
        try:
            return value.split(" ")[0]
        except Exception:
            return value

    def _compute_next_code_label(self, codes: List[str]) -> str:
        """Calcula el próximo código numérico a partir de la lista de códigos existentes y devuelve el label 'N (Nuevo Codigo)'."""
        max_num = 0
        for c in codes:
            try:
                n = int(str(c).strip())
                if n > max_num:
                    max_num = n
            except Exception:
                # Ignorar códigos no numéricos
                continue
        next_code = str(max_num + 1)
        return f"{next_code} {NUEVO_CODIGO_SUFFIX}"

    # --- Utilidades de ordenamiento y números ---
    def _sort_codes_numeric(self, codes: List[str]) -> List[str]:
        def _to_int(s: str) -> int:
            try:
                return int(str(s).strip())
            except Exception:
                return 0

        return sorted([str(c) for c in codes], key=_to_int)

    def _format_thousands(self, value: str) -> str:
        """Formatea un entero con separador de miles '.'"""
        if not value:
            return ""
        int_part = re.sub(r"\D", "", value)
        int_part = int_part.lstrip("0") or "0"
        groups = []
        while len(int_part) > 3:
            groups.insert(0, int_part[-3:])
            int_part = int_part[:-3]
        groups.insert(0, int_part)
        return ".".join(groups)

    def _format_price_from_digits(self, digits: str) -> str:
        """Dado un string de dígitos, formatea como precio ES: miles '.' y decimales ','.
        Regla append-right: si len(digits) <= 2, no hay coma.
        Si len >= 3, últimos 2 dígitos son decimales.
        """
        if not digits:
            return ""
        if len(digits) <= 2:
            # Solo enteros pequeños sin coma
            return self._format_thousands(digits)
        int_part = digits[:-2]
        dec_part = digits[-2:]
        return f"{self._format_thousands(int_part)},{dec_part}"

    def _format_decimal_comma(self, value: str) -> str:
        """Formatea decimal con miles '.' y decimales ',' a partir de string con '.' como separador decimal."""
        if value is None or value == "":
            return ""
        # Normalizar de entrada: permitir ',' o '.' como decimales
        v = str(value).strip()
        v = v.replace(" ", "")
        # Si viene como '12345,67' transformarlo primero a punto para separar int/dec
        if "," in v and "." not in v:
            v = v.replace(",", ".")
        try:
            num = float(v)
        except Exception:
            return value
        # Separar partes
        s = f"{num:.2f}"
        int_part, dec_part = s.split(".")
        int_fmt = self._format_thousands(int_part)
        return f"{int_fmt},{dec_part}"

    def _parse_int_thousands(self, value: str) -> str:
        """Convierte '12.345' -> '12345' (string)."""
        if not value:
            return "0"
        return re.sub(r"\D", "", value) or "0"

    def _parse_decimal_comma(self, value: str) -> str:
        """Convierte '12.345,67' -> '12345.67' (string con punto decimal)."""
        if not value:
            return "0.00"
        v = value.strip()
        # quitar separadores de miles '.' y cambiar coma por punto para decimales
        v = v.replace(".", "").replace(",", ".")
        # mantener solo dígitos y un solo punto
        parts = re.findall(r"\d+|\.", v)
        joined = "".join(parts)
        if joined.count(".") > 1:
            first, rest = joined.split(".", 1)
            rest = rest.replace(".", "")
            joined = first + "." + rest
        return joined if joined else "0.00"

    # --- Eventos de formato ---
    def _on_cantidad_keypress(self, event) -> str | None:
        """Cantidad: entrada controlada tipo 'append-right'. Solo dígitos, Backspace/Delete.
        Cada dígito se agrega al final. Backspace elimina el último. Se formatea con miles.
        """
        try:
            keysym = getattr(event, "keysym", "")
            ch = event.char
            entry = self.inputs["cantidad"]
            raw = re.sub(r"\D", "", entry.get())  # extraer dígitos actuales
            if keysym in {"BackSpace", "Delete"}:
                raw = raw[:-1]
            elif ch.isdigit():
                raw = (raw or "") + ch
            elif keysym in {"Tab"}:
                return None
            else:
                return "break"
            # Formatear miles desde dígitos
            entry.delete(0, "end")
            entry.insert(0, self._format_thousands(raw))
            entry.icursor("end")
            return "break"
        except Exception:
            return None

    def _on_cantidad_paste(self) -> None:
        try:
            entry = self.inputs["cantidad"]
            raw = re.sub(r"\D", "", entry.get())
            entry.delete(0, "end")
            entry.insert(0, self._format_thousands(raw))
            entry.icursor("end")
        except Exception:
            pass

    def _on_costo_paste(self) -> None:
        try:
            entry = self.inputs["costo"]
            raw = re.sub(r"\D", "", entry.get())
            entry.delete(0, "end")
            entry.insert(0, self._format_price_from_digits(raw))
            entry.icursor("end")
        except Exception:
            pass

    def _on_costo_focus_out(self) -> None:
        """Garantiza dos decimales al salir del campo costo."""
        try:
            entry = self.inputs["costo"]
            raw = re.sub(r"\D", "", entry.get())
            entry.delete(0, "end")
            entry.insert(0, self._format_price_from_digits(raw))
        except Exception:
            pass
