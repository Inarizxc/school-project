import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
from matplotlib.colors import is_color_like
import matplotlib.pyplot as plt
import threading


class DataVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор данных")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        self.df = None
        self.current_plots = []
        self.progress = None
        self.progress_window = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_top_controls(main_frame)
        self.setup_data_preview(main_frame)
        self.setup_plots_container(main_frame)
        self.setup_plot_controls(main_frame)

    def setup_top_controls(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=5)

        # Левая часть управления
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT)

        ttk.Button(left_frame, text="Загрузить файл", command=self.open_file).pack(
            side=tk.LEFT, padx=5
        )

        self.graph_mode = tk.StringVar(value="replace")
        ttk.Radiobutton(
            left_frame, text="Перестроить", variable=self.graph_mode, value="replace"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            left_frame, text="Новый график", variable=self.graph_mode, value="new"
        ).pack(side=tk.LEFT, padx=5)

        # Правая часть управления с измененным порядком кнопок
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT)

        ttk.Button(right_frame, text="?", command=self.show_help, width=3).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(right_frame, text="Очистить всё", command=self.clear_all).pack(
            side=tk.RIGHT, padx=5
        )

    def setup_data_preview(self, parent):
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(preview_frame, show="headings")
        vsb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_plots_container(self, parent):
        self.plots_container = ttk.Frame(parent)
        self.plots_container.pack(fill=tk.BOTH, expand=True)

    def setup_plot_controls(self, parent):
        self.controls_frame = ttk.Frame(parent)
        self.controls_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.controls_frame, text="Ось X:").pack(side=tk.LEFT, padx=5)
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(
            self.controls_frame, textvariable=self.x_var, width=15
        )
        self.x_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.controls_frame, text="Ось Y:").pack(side=tk.LEFT, padx=5)
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(
            self.controls_frame, textvariable=self.y_var, width=15
        )
        self.y_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.controls_frame, text="Толщина:").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(
            self.controls_frame,
            from_=0.1,
            to=10,
            increment=0.5,
            textvariable=self.size_var,
            width=5,
        ).pack(side=tk.LEFT, padx=5)

        self.color_var = tk.StringVar(value="blue")
        ttk.Button(self.controls_frame, text="Цвет", command=self.choose_color).pack(
            side=tk.LEFT, padx=5
        )

        self.plot_type = tk.StringVar(value="line")
        plot_types = [("Линия", "line"), ("Точки", "scatter"), ("Столбцы", "bar")]
        for text, value in plot_types:
            ttk.Radiobutton(
                self.controls_frame, text=text, variable=self.plot_type, value=value
            ).pack(side=tk.LEFT, padx=2)

        ttk.Label(self.controls_frame, text="Стиль:").pack(side=tk.LEFT, padx=5)
        self.style_var = tk.StringVar(value="default")
        style_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.style_var,
            values=["default"] + plt.style.available,
            width=12,
        )
        style_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.controls_frame, text="Построить", command=self.create_plot
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.controls_frame, text="Сохранить", command=self.save_plot).pack(
            side=tk.LEFT, padx=5
        )

    def show_progress(self):
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Загрузка...")
        self.progress = ttk.Progressbar(self.progress_window, mode="indeterminate")
        self.progress.pack(padx=20, pady=10)
        self.progress.start()

    def hide_progress(self):
        if self.progress_window:
            self.progress.stop()
            self.progress_window.destroy()
            self.progress_window = None

    def create_plot(self):
        def plot_thread():
            try:
                self.show_progress()

                if self.df is None:
                    raise ValueError("Сначала загрузите файл с данными!")

                x_col = self.x_var.get()
                y_col = self.y_var.get()
                color = self.color_var.get()
                size = self.size_var.get()

                if not x_col or (self.plot_type.get() != "bar" and not y_col):
                    raise ValueError("Выберите необходимые столбцы!")
                if (x_col not in self.df.columns) or (
                    y_col and y_col not in self.df.columns
                ):
                    raise ValueError("Выбранные столбцы отсутствуют в данных!")
                if not is_color_like(color):
                    raise ValueError("Некорректный цвет!")
                if size <= 0:
                    raise ValueError("Толщина должна быть больше нуля!")

                if self.graph_mode.get() == "replace":
                    self.clear_plots()

                plt.style.use(
                    self.style_var.get()
                    if self.style_var.get() != "default"
                    else "classic"
                )

                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)

                plot_type = self.plot_type.get()
                if plot_type == "line":
                    ax.plot(self.df[x_col], self.df[y_col], color=color, linewidth=size)
                elif plot_type == "scatter":
                    ax.scatter(
                        self.df[x_col],
                        self.df[y_col],
                        color=color,
                        s=size * 10,
                        alpha=0.7,
                    )
                elif plot_type == "bar":
                    ax.bar(
                        self.df[x_col],
                        self.df[y_col],
                        color=color,
                        alpha=0.7,
                        width=size / 5,
                    )

                ax.set_xlabel(x_col)
                if y_col:
                    ax.set_ylabel(y_col)
                ax.grid(True)

                self.root.after(0, self.add_plot_to_ui, fig)

            except Exception as e:
                self.root.after(0, self.show_error, str(e))
            finally:
                self.root.after(0, self.hide_progress)

        threading.Thread(target=plot_thread, daemon=True).start()

    def add_plot_to_ui(self, fig):
        plot_frame = ttk.Frame(self.plots_container)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
        toolbar.update()

        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_plots.append((fig, canvas, toolbar, plot_frame))

    def clear_plots(self):
        for fig, canvas, toolbar, frame in self.current_plots:
            fig.clf()
            plt.close(fig)
            canvas.get_tk_widget().destroy()
            toolbar.destroy()
            frame.destroy()
        self.current_plots.clear()

    def clear_all(self):
        self.clear_plots()
        self.df = None
        self.tree.delete(*self.tree.get_children())
        self.x_combo["values"] = []
        self.y_combo["values"] = []
        self.x_var.set("")
        self.y_var.set("")

    def update_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)

        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for _, row in self.df.head(50).iterrows():
            self.tree.insert("", tk.END, values=list(row))

        self.x_combo["values"] = list(self.df.columns)
        self.y_combo["values"] = list(self.df.columns)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color_var.set(color)

    def save_plot(self):
        if not self.current_plots:
            self.show_error("Нет активных графиков!")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("Все файлы", "*.*")],
            )
            if file_path:
                self.current_plots[-1][0].savefig(
                    file_path, bbox_inches="tight", dpi=300, facecolor="white"
                )
                messagebox.showinfo("Успех", "График сохранён!")
        except Exception as e:
            self.show_error(f"Ошибка сохранения: {str(e)}")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx;*.xls"),
                ("Все файлы", "*.*"),
            ]
        )
        if not file_path:
            return

        def load_thread():
            try:
                self.show_progress()

                if file_path.endswith(".json"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.handle_json(data)
                elif file_path.endswith(".csv"):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith((".xlsx", ".xls")):
                    self.df = pd.read_excel(file_path)

                self.root.after(0, self.update_preview)
            except Exception as e:
                self.root.after(0, self.show_error, f"Ошибка загрузки: {str(e)}")
            finally:
                self.root.after(0, self.hide_progress)

        threading.Thread(target=load_thread, daemon=True).start()

    def handle_json(self, data):
        window = tk.Toplevel(self.root)
        window.title("Выбор ключа")

        ttk.Label(
            window, text="Ключ данных (оставьте пустым для всего документа):"
        ).pack(pady=5)
        key_var = tk.StringVar()
        entry = ttk.Entry(window, textvariable=key_var)
        entry.pack(pady=5)

        def apply_key():
            try:
                key = key_var.get()
                selected_data = data[key] if key else data

                if isinstance(selected_data, dict):
                    self.df = pd.json_normalize(selected_data)
                elif isinstance(selected_data, list):
                    self.df = pd.DataFrame(selected_data)
                else:
                    raise ValueError("Неподдерживаемый формат данных в JSON")

                window.destroy()
                self.update_preview()
            except Exception as e:
                self.show_error(f"Ошибка ключа: {str(e)}")

        ttk.Button(window, text="Применить", command=apply_key).pack(pady=10)

    def show_help(self):
        help_text = """Инструкция:
1. Загрузите файл данных (JSON/CSV/XLSX)
2. Выберите столбцы для осей X и Y
3. Настройте параметры графика:
   - Тип (линия/точки/столбцы)
   - Цвет и толщина элементов
   - Стиль оформления
4. Нажмите 'Построить'
5. Используйте панель инструментов для масштабирования
6. Сохраняйте графики через кнопку 'Сохранить'"""
        messagebox.showinfo("Справка", help_text)

    def show_error(self, message):
        messagebox.showerror("Ошибка", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizer(root)
    root.mainloop()
