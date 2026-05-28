import customtkinter as ctk
import requests
import sys
import os

# Настройка темы
ctk.set_appearance_mode("Dark")  # Включаем стильную темную тему по умолчанию
ctk.set_default_color_theme("blue")

# Функция, чтобы PyInstaller правильно находил иконку внутри скомпилированного файла
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Погода Про")
        # Делаем окно шире (550) и заметно ниже (480), чтобы получился аккуратный прямоугольник
        self.geometry("790x480")
        self.resizable(False, False)


        # Установка иконки для окна (если файл icon.png есть в папке)
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            import tkinter as tk
            try:
                img = tk.PhotoImage(file=icon_path)
                self.tk.call('wm', 'iconphoto', self._w, img)
            except Exception as e:
                print(f"Не удалось загрузить иконку: {e}")

        # --- ВЕРХНЯЯ ПАНЕЛЬ (Поиск) ---
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=25, padx=20, fill="x")

        # Теперь подсказка говорит, что можно писать на русском!
        self.city_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Введите город (например: Москва)",
            height=45,
            font=("Arial", 14)
        )
        self.city_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.get_weather_btn = ctk.CTkButton(
            self.search_frame,
            text="Поиск",
            width=100,
            height=45,
            font=("Arial", 14, "bold"),
            command=self.get_weather
        )
        self.get_weather_btn.pack(side="right")

        # --- ГЛАВНАЯ КАРТОЧКА (Текущая погода) ---
        self.main_card = ctk.CTkFrame(self, corner_radius=20)
        self.main_card.pack(pady=10, padx=20, fill="x")

        self.city_label = ctk.CTkLabel(self.main_card, text="Город не выбран", font=("Arial", 22, "bold"))
        self.city_label.pack(pady=(20, 5))

        self.temp_label = ctk.CTkLabel(self.main_card, text="--°", font=("Arial", 64, "bold"), text_color="#3B8ED0")
        self.temp_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_card, text="Введите название и нажмите Поиск", font=("Arial", 14))
        self.status_label.pack(pady=(5, 20))

        # --- НИЖНЯЯ ПАНЕЛЬ (Прогноз на 3 дня) ---
        self.forecast_title = ctk.CTkLabel(self, text="Прогноз на ближайшие дни:", font=("Arial", 16, "bold"))
        # Уменьшили верхний отступ с 20 до 10, чтобы подтянуть интерфейс выше
        self.forecast_title.pack(pady=(10, 5), padx=25, anchor="w")

        self.forecast_frame = ctk.CTkFrame(self, fg_color="transparent")
        # fill="x" растягивает контейнер на всю ширину, а pady=(5, 20) оставляет аккуратный отступ до нижнего края
        self.forecast_frame.pack(pady=(5, 20), padx=20, fill="x")

        # Создаем 3 карточки для прогноза
        self.forecast_days = []
        for i in range(3):
            # Изменили высоту карточек со 120 до 100, так как окно стало ниже
            card = ctk.CTkFrame(self.forecast_frame, corner_radius=12, height=100)
            card.pack(side="left", expand=True, fill="both", padx=8) # Увеличили боковой отступ между карточками до 8
            card.pack_propagate(False)

            day_lbl = ctk.CTkLabel(card, text=f"День {i+1}", font=("Arial", 12, "bold"), text_color="gray")
            day_lbl.pack(pady=(12, 2)) # Слегка скорректировали отступы внутри карточки

            temp_lbl = ctk.CTkLabel(card, text="--°C", font=("Arial", 18, "bold"))
            temp_lbl.pack(pady=2)

            self.forecast_days.append({"day": day_lbl, "temp": temp_lbl})

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            self.status_label.configure(text="Вы не ввели город!")
            return

        try:
            self.status_label.configure(text="Поиск города...")
            self.update()

            # 1. Геокодинг (работает НА РУССКОМ языке благодаря параметру language=ru)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
            geo_response = requests.get(geo_url).json()

            if not geo_response.get("results"):
                self.status_label.configure(text="Город не найден :(")
                self.temp_label.configure(text="--°")
                return

            location = geo_response["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]

            # Красивое имя города + страна (например: Москва, RU)
            city_name = location.get("name", city)
            country = location.get("country", "")
            full_location_name = f"{city_name}, {country}" if country else city_name

            # 2. Запрос погоды + ежедневного прогноза (daily=temperature_2m_max)
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max&timezone=auto"
            weather_response = requests.get(weather_url).json()

            # Данные на сегодня
            current_weather = weather_response["current_weather"]
            temperature = round(current_weather["temperature"])

            # Данные прогноза
            forecast_data = weather_response["daily"]
            forecast_temps = forecast_data["temperature_2m_max"]
            forecast_dates = forecast_data["time"]

            # Обновляем главный экран
            self.city_label.configure(text=full_location_name)
            self.temp_label.configure(text=f"{temperature}°")
            self.status_label.configure(text="Данные успешно обновлены")

            # Обновляем 3 карточки прогноза (берём со следующего дня, т.е. индексы 1, 2, 3)
            for idx, card_widgets in enumerate(self.forecast_days):
                date_str = forecast_dates[idx + 1] # Формат YYYY-MM-DD
                # Превратим "2026-05-29" в "29.05" для красоты
                short_date = ".".join(date_str.split("-")[1:][::-1])

                t_max = round(forecast_temps[idx + 1])

                card_widgets["day"].configure(text=short_date)
                card_widgets["temp"].configure(text=f"{t_max}°C")

        except Exception as e:
            self.status_label.configure(text="Ошибка сети")
            self.temp_color = "--°"

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
