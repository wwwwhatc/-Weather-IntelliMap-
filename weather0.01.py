import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib import rcParams
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用 SimHei 字体，确保显示中文
rcParams['axes.unicode_minus'] = False

# 设置API密钥和基础URL
API_KEY = 'API KEY'  # 替换为你的 OpenWeatherMap API 密钥
BASE_URL = 'http://api.openweathermap.org/data/2.5/'

# 天气描述翻译为中文的映射（可以根据需要扩展或自定义）
weather_description_translation = {
    'clear sky': '晴天',
    'few clouds': '少量云',
    'scattered clouds': '散云',
    'broken clouds': '多云',
    'overcast clouds': '阴，多云',
    'shower rain': '阵雨',
    'rain': '雨',
    'thunderstorm': '雷暴',
    'snow': '雪',
    'mist': '雾',
}

# 获取当前天气数据的函数
def get_weather_data(city):
    url = f'{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        messagebox.showerror("网络错误", f"无法获取城市 {city} 的当前天气数据。\n错误详情：{e}")
        return None

# 获取天气预报数据的函数
def get_forecast_data(city):
    url = f'{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        messagebox.showerror("网络错误", f"无法获取城市 {city} 的天气预报数据。\n错误详情：{e}")
        return None

# 创建天气图表函数（保持不变）
def create_weather_plot(cities, weather_type, canvas_frame, description_frame, chart_frame):
    # 清空之前的图表
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    for widget in chart_frame.winfo_children():
        widget.destroy()

    # 创建地图图表
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100, subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([-180, 180, -90, 90])  # 设置地图范围
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.LAND, edgecolor='gray')

    city_weather_data = []
    city_names = []

    for idx, city in enumerate(cities):
        city = city.strip()
        if not city:
            continue  # 跳过空字符串
        data = get_weather_data(city)
        if not data or data.get('cod') != 200:
            messagebox.showerror("错误", f"无法获取城市：{city}")
            continue

        lat, lon = data['coord']['lat'], data['coord']['lon']
        city_name = data['name']
        temp = data['main']['temp']
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        description = data['weather'][0]['description']

        # 使用天气描述的中文翻译
        description_cn = weather_description_translation.get(description, description)

        # 标记城市位置
        label = f'{city_name} - {temp}°C'
        ax.scatter(lon, lat, color=f'C{idx}', s=100, transform=ccrs.PlateCarree(), label=label)
        ax.text(lon + 3, lat + 3, city_name, transform=ccrs.PlateCarree(), fontsize=9, weight='bold')

        city_weather_data.append({
            'city': city_name,
            'description': description_cn,  # 使用中文描述
            'temp': temp,
            'wind_speed': wind_speed,
            'humidity': humidity,
            'pressure': pressure
        })
        city_names.append(city_name)

    ax.set_title(f'天气对比：{weather_type}', fontsize=16, pad=20)
    ax.legend(loc='upper left', fontsize=10, frameon=True, shadow=True)

    # 使用 FigureCanvasTkAgg 嵌入图表并自动调整大小
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 更新天气描述区域
    for widget in description_frame.winfo_children():
        widget.destroy()  # 清空现有的天气描述

    # 创建并排显示的城市天气描述
    max_width = 200  # 设置最大宽度，单位是像素，您可以根据实际需求调整
    for idx, city_data in enumerate(city_weather_data):
        city_label = tk.Label(description_frame, text=f"{city_data['city']}：\n"
                                                      f"天气：{city_data['description']} | "
                                                      f"温度：{city_data['temp']}°C | "
                                                      f"风速：{city_data['wind_speed']} m/s | "
                                                      f"湿度：{city_data['humidity']}% | "
                                                      f"气压：{city_data['pressure']} hPa",
                              anchor="w", padx=10, pady=5, wraplength=max_width, relief=tk.RIDGE, borderwidth=1, bg="#f0f0f0")
        city_label.grid(row=0, column=idx, padx=5, pady=5, sticky='nsew')

    # 创建数据图表
    fig_data, ax_data = plt.subplots(figsize=(8, 5), dpi=100)

    if weather_type == '温度':
        values = [data['temp'] for data in city_weather_data]
        ax_data.bar(city_names, values, color='lightblue')
        ax_data.set_title('城市温度对比', fontsize=14)
        ax_data.set_ylabel('温度 (°C)', fontsize=12)
    elif weather_type == '风速':
        values = [data['wind_speed'] for data in city_weather_data]
        ax_data.bar(city_names, values, color='lightgreen')
        ax_data.set_title('城市风速对比', fontsize=14)
        ax_data.set_ylabel('风速 (m/s)', fontsize=12)
    elif weather_type == '湿度':
        values = [data['humidity'] for data in city_weather_data]
        ax_data.bar(city_names, values, color='lightcoral')
        ax_data.set_title('城市湿度对比', fontsize=14)
        ax_data.set_ylabel('湿度 (%)', fontsize=12)
    elif weather_type == '气压':
        values = [data['pressure'] for data in city_weather_data]
        ax_data.bar(city_names, values, color='lightsalmon')
        ax_data.set_title('城市气压对比', fontsize=14)
        ax_data.set_ylabel('气压 (hPa)', fontsize=12)

    ax_data.tick_params(axis='x', rotation=45)
    ax_data.grid(axis='y', linestyle='--', alpha=0.7)

    # 使用 FigureCanvasTkAgg 嵌入数据图表并自动调整大小
    canvas_data = FigureCanvasTkAgg(fig_data, master=chart_frame)
    canvas_data.draw()
    canvas_data.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# 创建天气预报图表函数（已修改支持多个城市）
def create_forecast_plot(cities, forecast_frame):
    # 清空之前的图表
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)

    all_dates = []
    city_temps = {}
    city_descriptions = {}

    for city in cities:
        city = city.strip()
        if not city:
            continue  # 跳过空字符串
        data = get_forecast_data(city)
        if not data or data.get('cod') != "200":
            messagebox.showerror("错误", f"无法获取城市：{city}")
            continue  # 继续处理下一个城市

        # 解析数据
        forecast_list = data['list']
        dates = []
        temps = []
        descriptions = []

        for entry in forecast_list:
            dt_txt = entry['dt_txt']  # 格式: '2023-10-10 12:00:00'
            date = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
            dates.append(date.strftime('%m-%d %H:%M'))
            temps.append(entry['main']['temp'])
            description = entry['weather'][0]['description']
            descriptions.append(weather_description_translation.get(description, description))

        # 存储数据以便绘图
        city_temps[city] = temps
        city_descriptions[city] = descriptions

        # 确保所有城市的日期相同
        if not all_dates:
            all_dates = dates
        elif all_dates != dates:
            messagebox.showwarning("警告", f"城市 {city} 的预报日期与其他城市不一致，可能导致图表显示问题。")

    if not city_temps:
        return  # 没有有效的城市数据

    # 绘制每个城市的温度趋势
    for city, temps in city_temps.items():
        ax.plot(all_dates, temps, marker='o', linestyle='-', label=city)

    ax.set_title(f"多个城市未来5天天气预报温度趋势", fontsize=16, pad=20)
    ax.set_xlabel('日期时间', fontsize=12)
    ax.set_ylabel('温度 (°C)', fontsize=12)
    plt.xticks(rotation=45)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 使用 FigureCanvasTkAgg 嵌入图表并自动调整大小
    canvas = FigureCanvasTkAgg(fig, master=forecast_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 创建带滚动条的天气描述区域
    description_canvas = tk.Canvas(forecast_frame)
    scrollbar = ttk.Scrollbar(forecast_frame, orient="vertical", command=description_canvas.yview)
    scrollable_frame = ttk.Frame(description_canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: description_canvas.configure(
            scrollregion=description_canvas.bbox("all")
        )
    )

    description_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    description_canvas.configure(yscrollcommand=scrollbar.set)

    description_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 显示详细的天气描述
    for city in cities:
        city = city.strip()
        if not city:
            continue
        data = get_forecast_data(city)
        if not data or data.get('cod') != "200":
            continue

        forecast_list = data['list']
        dates = []
        temps = []
        descriptions = []

        for entry in forecast_list:
            dt_txt = entry['dt_txt']
            date = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
            dates.append(date.strftime('%m-%d %H:%M'))
            temps.append(entry['main']['temp'])
            description = entry['weather'][0]['description']
            descriptions.append(weather_description_translation.get(description, description))

        # 每24小时一次的预报，大约每8个间隔是一天
        for i in range(0, len(dates), 8):
            day = dates[i].split(' ')[0]
            day_temps = temps[i:i+8]
            day_descriptions = descriptions[i:i+8]
            if not day_temps:
                continue
            avg_temp = sum(day_temps) / len(day_temps)
            if day_descriptions:
                main_description = max(set(day_descriptions), key=day_descriptions.count)  # 最频繁的描述
            else:
                main_description = "无数据"

            city_label = ttk.Label(scrollable_frame, text=f"城市: {city}", font=("Arial", 12, "bold"))
            city_label.pack(anchor='w', padx=10, pady=(10, 0))

            day_label = ttk.Label(scrollable_frame, text=f"日期: {day}")
            day_label.pack(anchor='w', padx=20)

            temp_label = ttk.Label(scrollable_frame, text=f"平均温度: {avg_temp:.2f}°C")
            temp_label.pack(anchor='w', padx=20)

            desc_label = ttk.Label(scrollable_frame, text=f"主要天气: {main_description}")
            desc_label.pack(anchor='w', padx=20, pady=(0, 10))

# 创建启动界面函数（保持不变）
def create_start_frame(root, show_weather_map, show_forecast):
    start_frame = ttk.Frame(root, padding=10)
    start_frame.grid(row=0, column=0, sticky='nsew')

    # 配置行和列的权重
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    start_frame.grid_rowconfigure(0, weight=1)
    start_frame.grid_rowconfigure(1, weight=1)
    start_frame.grid_columnconfigure(0, weight=1)

    # 标题
    title_label = ttk.Label(start_frame, text="天气智图 (Weather IntelliMap)", font=("Arial", 20, "bold"))
    title_label.grid(row=0, column=0, pady=(50, 20))

    # 按钮
    button_frame = ttk.Frame(start_frame)
    button_frame.grid(row=1, column=0, pady=10)

    map_button = ttk.Button(button_frame, text="天气地图功能", command=show_weather_map, width=20)
    map_button.grid(row=0, column=0, padx=10, pady=5)

    forecast_button = ttk.Button(button_frame, text="天气预报功能", command=show_forecast, width=20)
    forecast_button.grid(row=0, column=1, padx=10, pady=5)

# 创建天气地图界面函数（保持不变）
def create_weather_map_frame(root, go_back):
    # 清除所有现有的框架
    for widget in root.winfo_children():
        widget.destroy()

    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky='nsew')

    # 配置行和列的权重
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(3, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)
    frame.grid_columnconfigure(3, weight=1)

    # 标题和返回按钮
    header_frame = ttk.Frame(frame)
    header_frame.grid(row=0, column=0, columnspan=4, sticky='ew')

    back_button = ttk.Button(header_frame, text="返回", command=go_back)
    back_button.pack(anchor='nw')

    # 输入框和按钮区域
    control_frame = ttk.LabelFrame(frame, text="查询设置", padding=10)
    control_frame.grid(row=1, column=0, columnspan=4, sticky='ew', pady=10)

    # 城市输入
    city_label = ttk.Label(control_frame, text="城市名称（逗号分隔）:")
    city_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    city_entry = ttk.Entry(control_frame, width=40)
    city_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # 天气类型选择
    weather_label = ttk.Label(control_frame, text="天气类型:")
    weather_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    weather_type_combobox = ttk.Combobox(control_frame, values=["温度", "风速", "湿度", "气压"], state="readonly")
    weather_type_combobox.set("温度")
    weather_type_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    # 查询按钮
    search_button = ttk.Button(control_frame, text="查询",
                               command=lambda: create_weather_plot(city_entry.get().split(','),
                                                                   weather_type_combobox.get(),
                                                                   canvas_frame,
                                                                   description_frame,
                                                                   chart_frame))
    search_button.grid(row=0, column=4, padx=10, pady=5)

    # 天气描述区域
    description_frame = ttk.LabelFrame(frame, text="天气描述", padding=10)
    description_frame.grid(row=2, column=0, columnspan=4, sticky='ew', pady=10)

    # 地图显示区域
    canvas_frame = ttk.Frame(frame, relief=tk.SUNKEN, borderwidth=1)
    canvas_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

    # 数据图表显示区域
    chart_frame = ttk.Frame(frame, relief=tk.SUNKEN, borderwidth=1)
    chart_frame.grid(row=3, column=2, columnspan=2, sticky='nsew', padx=5, pady=5)

# 创建天气预报界面函数（已修改支持多个城市）
def create_forecast_frame(root, go_back):
    # 清除所有现有的框架
    for widget in root.winfo_children():
        widget.destroy()

    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky='nsew')

    # 配置行和列的权重
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(3, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=3)
    frame.grid_columnconfigure(2, weight=1)

    # 标题和返回按钮
    header_frame = ttk.Frame(frame)
    header_frame.grid(row=0, column=0, columnspan=3, sticky='ew')

    back_button = ttk.Button(header_frame, text="返回", command=go_back)
    back_button.pack(anchor='nw')

    # 输入框和按钮区域
    control_frame = ttk.LabelFrame(frame, text="查询设置", padding=10)
    control_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

    # 城市输入
    city_label = ttk.Label(control_frame, text="城市名称（逗号分隔）:")
    city_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    city_entry = ttk.Entry(control_frame, width=40)
    city_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # 查询按钮
    search_button = ttk.Button(control_frame, text="查询",
                               command=lambda: create_forecast_plot(city_entry.get().split(','), forecast_frame))
    search_button.grid(row=0, column=2, padx=10, pady=5)

    # 天气预报显示区域
    forecast_frame = ttk.LabelFrame(frame, text="天气预报", padding=10)
    forecast_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=10)

# 创建图形化界面函数（保持不变）
def create_gui():
    root = tk.Tk()
    root.title("天气智图 (Weather IntelliMap)")
    root.geometry("600x300")
    root.resizable(True, True)

    # 设置窗口的行和列权重
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    def show_weather_map():
        create_weather_map_frame(root, show_start_frame)

    def show_forecast():
        create_forecast_frame(root, show_start_frame)

    def show_start_frame():
        # 清除所有现有的框架
        for widget in root.winfo_children():
            widget.destroy()
        create_start_frame(root, show_weather_map, show_forecast)

    # 初始化启动界面
    show_start_frame()

    root.mainloop()

# 启动GUI应用
if __name__ == "__main__":
    create_gui()
