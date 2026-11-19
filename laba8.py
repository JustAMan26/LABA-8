import tkinter as tk
from tkinter import messagebox

def create_test_data(filename):
    """Создание тестового текстового файла с данными"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("01.10 15.2\n")
        f.write("02.10 16.5\n")
        f.write("03.10 14.8\n")
        f.write("04.10 17.1\n")
        f.write("05.10 15.9\n")
        f.write("06.10 18.3\n")
        f.write("07.10 19.0\n")
        f.write("08.10 17.5\n")

def read_data(filename):
    """Чтение данных из текстового файла"""
    dates = []
    values = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    dates.append(parts[0])
                    values.append(float(parts[1]))
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {filename} не найден!")
    return dates, values

def draw_3d_chart(dates, num_days, values, fill_code):
    """
    Процедура построения трехмерной столбиковой диаграммы.
    Параметры (согласно заданию):
    - dates: массив дат
    - num_days: количество дней
    - values: массив значений по оси Y
    - fill_code: код заполнителя (цвет)
    """
    global cv
    
    # Обновляем размеры полотна
    cv.update()
    W = cv.winfo_width()
    H = cv.winfo_height()
    
    cv.delete("all") # Очистка перед рисованием
    
    # Отступы для осей и заголовка
    left_margin = 80
    right_margin = 50
    top_margin = 60
    bottom_margin = 80
    
    plot_w = W - left_margin - right_margin
    plot_h = H - top_margin - bottom_margin
    
    # Заголовок диаграммы
    cv.create_text(W/2, 30, text="Курс немецкой марки к рублю", font=("Arial", 16, "bold"))
    
    if num_days == 0 or max(values) == 0:
        return
        
    max_val = max(values) * 1.15 # Добавляем запас сверху для красоты
    
    # Параметры для создания 3D-эффекта (смещение)
    dx_3d = 15
    dy_3d = 15
    
    bar_w = plot_w / num_days # Ширина одного столбца
    
    # Рисуем оси координат
    cv.create_line(left_margin, top_margin, left_margin, top_margin + plot_h, width=2)
    cv.create_line(left_margin, top_margin + plot_h, left_margin + plot_w, top_margin + plot_h, width=2)
    
    # Разметка оси Y (сетка и метки)
    num_y_ticks = 5
    for i in range(num_y_ticks + 1):
        val = (max_val / num_y_ticks) * i
        y_pix = top_margin + plot_h - (val / max_val) * plot_h
        
        cv.create_line(left_margin, y_pix, left_margin + plot_w, y_pix, dash=(4, 4), fill='gray')
        cv.create_line(left_margin - 5, y_pix, left_margin, y_pix, width=2)
        cv.create_text(left_margin - 10, y_pix, text=f"{val:.1f}", anchor='e', font=("Arial", 10))
        
    # Рисуем столбцы
    for i in range(num_days):
        val = values[i]
        h_pix = (val / max_val) * plot_h
        
        # Координаты передней грани
        x1 = left_margin + i * bar_w + 5
        x2 = x1 + bar_w - 10
        y1 = top_margin + plot_h - h_pix
        y2 = top_margin + plot_h
        
        # 1. Передняя грань (Прямоугольник)
        cv.create_rectangle(x1, y1, x2, y2, fill=fill_code, outline='black')
        
        # 2. Верхняя грань (Многоугольник для 3D)
        top_points = [x1, y1, x1 + dx_3d, y1 - dy_3d, x2 + dx_3d, y1 - dy_3d, x2, y1]
        cv.create_polygon(top_points, fill=fill_code, outline='black')
        
        # 3. Боковая грань (Многоугольник для 3D)
        side_points = [x2, y1, x2 + dx_3d, y1 - dy_3d, x2 + dx_3d, y2 - dy_3d, x2, y2]
        cv.create_polygon(side_points, fill=fill_code, outline='black')
        
        # Подпись даты на оси X
        x_label = (x1 + x2) / 2 + dx_3d / 2
        cv.create_text(x_label, top_margin + plot_h + 20, text=dates[i], anchor='n', font=("Arial", 9))

# ==================== ОСНОВНАЯ ЧАСТЬ ПРОГРАММЫ ====================
if __name__ == "__main__":
    filename = "data.txt"
    
    # 1. Формируем текстовый файл с данными
    create_test_data(filename) 
    
    # 2. Считываем данные
    dates, values = read_data(filename)
    num_days = len(dates)

    # 3. Создаем графический интерфейс (GUI)
    root = tk.Tk()
    root.title("Лабораторная работа 8, Вариант 20")
    root.geometry("800x600")

    # Полотно (Canvas) занимает всю доступную область
    cv = tk.Canvas(root, bg="white")
    cv.pack(fill=tk.BOTH, expand=True)

    # Кнопка для запуска построения диаграммы
    def on_draw():
        # Вызов процедуры с передачей всех требуемых параметров
        draw_3d_chart(dates, num_days, values, "#4C72B0") # "#4C72B0" - код синего заполнителя

    btn = tk.Button(root, text="Построить диаграмму", command=on_draw, font=("Arial", 12))
    btn.pack(side=tk.BOTTOM, pady=10)

    # Запуск цикла обработки событий
    root.mainloop()
