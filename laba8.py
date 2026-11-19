import tkinter as tk
from tkinter import filedialog, messagebox
import os

# ---------------------------------------------------------
# Вспомогательная функция для изменения яркости HEX-цвета
# (нужна для создания эффекта 3D: светлая верхняя грань, темная боковая)
# ---------------------------------------------------------
def adjust_color(color, factor):
    """Изменяет яркость HEX-цвета. factor > 1 осветляет, < 1 затемняет."""
    if not color.startswith('#') or len(color) != 7:
        return color  # Если передан именованный цвет, возвращаем как есть
    try:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        return color

# ---------------------------------------------------------
# Основная процедура построения 3D столбиковой диаграммы
# Параметры: canvas, массив дат, кол-во дней, массив значений, код заполнителя
# ---------------------------------------------------------
def draw_3d_bar_chart(canvas, dates, n_days, y_values, fill_code):
    canvas.delete("all")  # Очистка холста
    
    if n_days == 0 or not y_values:
        messagebox.showwarning("Ошибка", "Нет данных для построения диаграммы.")
        return

    # Отступы для осей и подписей
    margin_left = 70
    margin_right = 40
    margin_top = 60
    margin_bottom = 80

    # Получаем актуальные размеры холста
    canvas.update()
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    
    # Если холст еще не отрисован, берем начальные размеры
    if width < 100: width = 800
    if height < 100: height = 600

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    # Масштабирование по оси Y
    max_y = max(y_values) * 1.2  # Добавляем 20% места сверху для красоты
    min_y = 0.0

    # Параметры столбиков
    bar_width = (plot_width / n_days) * 0.6  # Ширина столбика
    gap = (plot_width / n_days) * 0.4        # Расстояние между столбиками
    depth = 15                               # Глубина 3D-эффекта (смещение в пикселях)

    # --- Рисуем заголовок ---
    canvas.create_text(width // 2, 25, text="Курс немецкой марки к рублю", 
                       font=("Arial", 14, "bold"), fill="black")
    canvas.create_text(width // 2, 45, text="(за заданный период)", 
                       font=("Arial", 10), fill="gray")

    # --- Рисуем оси координат ---
    # Ось Y
    canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
    # Ось X
    canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
    
    # Подписи осей
    canvas.create_text(30, height // 2, text="Курс (руб.)", angle=90, font=("Arial", 11, "bold"))
    canvas.create_text(width // 2, height - 20, text="Дата", font=("Arial", 11, "bold"))

    # --- Градация оси Y ---
    num_ticks = 6
    for i in range(num_ticks + 1):
        val = min_y + (max_y - min_y) * (i / num_ticks)
        y_pos = height - margin_bottom - (plot_height * (i / num_ticks))
        
        # Значение
        canvas.create_text(margin_left - 10, y_pos, text=f"{val:.1f}", anchor="e", font=("Arial", 10))
        # Штрих
        canvas.create_line(margin_left - 5, y_pos, margin_left, y_pos, width=1)
        # Сетка (пунктир)
        canvas.create_line(margin_left, y_pos, width - margin_right, y_pos, dash=(3, 3), fill="lightgray")

    # --- Рисуем 3D столбики ---
    for i in range(n_days):
        x_start = margin_left + i * (bar_width + gap) + gap / 2
        x_end = x_start + bar_width

        val = y_values[i]
        bar_height_px = (val / max_y) * plot_height
        y_start = height - margin_bottom - bar_height_px
        y_end = height - margin_bottom

        # Цвета для граней 3D
        color_front = fill_code
        color_top = adjust_color(fill_code, 1.3)    # Светлее
        color_right = adjust_color(fill_code, 0.7)  # Темнее

        # 1. Передняя грань (прямоугольник)
        canvas.create_rectangle(x_start, y_start, x_end, y_end, 
                                fill=color_front, outline="black", width=1)

        # 2. Верхняя грань (параллелограмм)
        top_poly = [
            x_start, y_start,
            x_end, y_start,
            x_end + depth, y_start - depth,
            x_start + depth, y_start - depth
        ]
        canvas.create_polygon(top_poly, fill=color_top, outline="black", width=1)

        # 3. Правая боковая грань (параллелограмм)
        right_poly = [
            x_end, y_start,
            x_end, y_end,
            x_end + depth, y_end - depth,
            x_end + depth, y_start - depth
        ]
        canvas.create_polygon(right_poly, fill=color_right, outline="black", width=1)

        # --- Подписи дат под осью X ---
        # Разворачиваем текст на 45 градусов для лучшей читаемости, если дат много
        canvas.create_text(x_start + bar_width / 2, height - margin_bottom + 15, 
                           text=dates[i], anchor="n", font=("Arial", 9), angle=45)


# ---------------------------------------------------------
# Логика интерфейса (GUI)
# ---------------------------------------------------------
def load_and_draw():
    """Загружает данные из файла и вызывает процедуру рисования"""
    file_path = filedialog.askopenfilename(
        title="Выберите файл с данными",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    if not file_path:
        return

    dates = []
    y_values = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    dates.append(parts[0])
                    y_values.append(float(parts[1]))
        
        n_days = len(dates)
        if n_days > 0:
            # Вызов требуемой процедуры с заданными параметрами
            # Параметры: canvas, массив дат, количество дней, массив значений, код заполнителя
            draw_3d_bar_chart(canvas, dates, n_days, y_values, fill_code="#4A90E2")
            status_label.config(text=f"Загружено: {os.path.basename(file_path)} ({n_days} записей)")
        else:
            messagebox.showerror("Ошибка", "Файл не содержит корректных данных.")
            
    except Exception as e:
        messagebox.showerror("Ошибка чтения файла", f"Не удалось прочитать файл:\n{e}")


def close_app():
    """Завершение работы приложения"""
    if messagebox.askyesno("Выход", "Завершить работу программы?"):
        root.destroy()


# --- Создание главного окна ---
root = tk.Tk()
root.title("Лабораторная работа №8, Вариант 20")
root.geometry("900x700")
root.resizable(True, True)

# Верхняя панель с кнопками
control_frame = tk.Frame(root, pady=10)
control_frame.pack(fill=tk.X)

btn_load = tk.Button(control_frame, text="Загрузить данные и построить", 
                     command=load_and_draw, font=("Arial", 11), bg="#e0e0e0")
btn_load.pack(side=tk.LEFT, padx=20)

btn_exit = tk.Button(control_frame, text="Выход", 
                     command=close_app, font=("Arial", 11), bg="#e0e0e0")
btn_exit.pack(side=tk.RIGHT, padx=20)

status_label = tk.Label(control_frame, text="Данные не загружены", fg="gray", font=("Arial", 10))
status_label.pack(side=tk.LEFT, padx=20)

# Холст для рисования (Canvas)
canvas = tk.Canvas(root, bg="white", relief=tk.SUNKEN, borderwidth=2)
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Обработчик закрытия окна через крестик
root.protocol("WM_DELETE_WINDOW", close_app)

# Запуск главного цикла обработки событий
root.mainloop()