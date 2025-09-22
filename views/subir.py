import customtkinter as ctk
from conexion import obtener_conexion
from colors import (HEADER_BG, VIEW_BACKGROUND, LIGHT_GRAY, WHITE)
from icons import *
from tkinter import messagebox

class SubirView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.configure(fg_color="white")

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
        campos = [("Código", "codigo"), ("Descripción", "descripcion"),
                ("Cantidad", "cantidad"), ("Costo", "costo")]

        for label_text, key in campos:
            ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=18)).pack(anchor="w", pady=(10, 0))
            entry = ctk.CTkEntry(form_frame, width=400, font=ctk.CTkFont(size=16))
            entry.pack(anchor="w", pady=(0, 10))
            self.inputs[key] = entry

        # ✅ Botón guardar fuera del scroll, centrado
        btn_guardar = ctk.CTkButton(self, text="Guardar", font=ctk.CTkFont(size=18),
            width=200, fg_color="#4CAF50", text_color="white",
            hover_color="#45a049", command=self.guardar_en_db)
        btn_guardar.place(relx=0.5, rely=0.88, anchor="center")

    
    def guardar_en_db(self, auto=False):
        codigo = self.inputs["codigo"].get().strip()
        descripcion = self.inputs["descripcion"].get().strip()
        cantidad = self.inputs["cantidad"].get().strip()
        costo = self.inputs["costo"].get().strip()
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
                cursor.execute("""
                    INSERT INTO Inventario (id, descripcion_insumo, costo_unitario)
                    VALUES (%s, %s, %s)
                """, (codigo, descripcion, costo))
            else:
                if not auto:
                    confirmar = messagebox.askyesno("Código existente", "Este código ya existe. ¿Deseas modificarlo?")
                    if not confirmar:
                        conn.close()
                        return
                cursor.execute("""
                    UPDATE Inventario SET descripcion_insumo = %s, costo_unitario = %s WHERE id = %s
                """, (descripcion, costo, codigo))

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
        descripcion = self.inputs["descripcion"].get().strip()
        cantidad = self.inputs["cantidad"].get().strip()
        costo = self.inputs["costo"].get().strip()

        if all([codigo, descripcion, cantidad, costo]):
            self.guardar_en_db(auto=True)
