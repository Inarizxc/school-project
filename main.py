import tkinter as tk
from tkinter import filedialog
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def clear_canvas():
    for widget in root.winfo_children():
        if widget != button:
            widget.destroy()

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)

            key_var = tk.StringVar(value='')
            key_label = tk.Label(root, text="Ключ:")
            key_entry = tk.Entry(root, textvariable=key_var)
            key_label.pack()
            key_entry.pack()

            def extract_and_plot():
                key = key_var.get()
                if key:
                    extracted_data = data.get(key, [])
                    df = pd.DataFrame(extracted_data)
                else:
                    df = pd.DataFrame(data)

                clear_canvas()

                x_column = tk.StringVar(value='x')
                y_column = tk.StringVar(value='y')

                def plot_data():
                    x_col = x_column.get()
                    y_col = y_column.get()

                    if x_col not in df.columns or y_col not in df.columns:
                        print(f"'{x_col}' и/или '{y_col}' отсутствуют в файле.")
                        return

                    fig, ax = plt.subplots(figsize=(6, 4))

                    ax.plot(df[x_col], df[y_col])

                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'График из файла ({x_col}, {y_col})')

                    canvas = FigureCanvasTkAgg(fig, master=root)
                    canvas.draw()
                    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

                    label_x.destroy()
                    entry_x.destroy()
                    label_y.destroy()
                    entry_y.destroy()
                    button_plot.destroy()

                label_x = tk.Label(root, text="Выберите столбец 1:")
                entry_x = tk.Entry(root, textvariable=x_column)
                label_y = tk.Label(root, text="Выберите столбец 2:")
                entry_y = tk.Entry(root, textvariable=y_column)
                button_plot = tk.Button(root, text="Построить график", command=plot_data)

                label_x.pack()
                entry_x.pack()
                label_y.pack()
                entry_y.pack()
                button_plot.pack()

                key_label.destroy()
                key_entry.destroy()

            extract_button = tk.Button(root, text="Получить данные", command=extract_and_plot)
            extract_button.pack()

        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)

            clear_canvas()

            x_column = tk.StringVar(value='x')
            y_column = tk.StringVar(value='y')

            def plot_data():
                x_col = x_column.get()
                y_col = y_column.get()

                if x_col not in df.columns or y_col not in df.columns:
                    print(f"'{x_col}' и/или '{y_col}' отсутствуют в данных.")
                    return

                fig, ax = plt.subplots(figsize=(6, 4))

                ax.plot(df[x_col], df[y_col])

                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f'График из файла ({x_col}, {y_col})')

                canvas = FigureCanvasTkAgg(fig, master=root)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

                label_x.destroy()
                entry_x.destroy()
                label_y.destroy()
                entry_y.destroy()
                button_plot.destroy()

            label_x = tk.Label(root, text="Выберите столбец 1:")
            entry_x = tk.Entry(root, textvariable=x_column)
            label_y = tk.Label(root, text="Выберите столбец 2:")
            entry_y = tk.Entry(root, textvariable=y_column)
            button_plot = tk.Button(root, text="Построить график", command=plot_data)

            label_x.pack()
            entry_x.pack()
            label_y.pack()
            entry_y.pack()
            button_plot.pack()

        else:
            ValueError("Неподдерживаемый формат файла.")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

root = tk.Tk()
root.title("Вывод больших данных")

button = tk.Button(root, text="Загрузить файл", command=open_file)
button.pack(pady=10)

root.mainloop()
