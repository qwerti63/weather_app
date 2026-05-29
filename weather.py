#imports
import customtkinter as ctk
import requests
import sys
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

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
        self.geometry("790x480")
        self.resizable(False, False)
        
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            import tkinter as tk
            try:
                img = tk.PhotoImage(file=icon_path)
                self.tk.call('wm', 'iconphoto', self._w, img)
            except Exception as e:
                print(f"Не удалось загрузить иконку: {e}")

        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(pady=25, padx=20, fill="x")

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

        self.main_card = ctk.CTkFrame(self, corner_radius=20)
        self.main_card.pack(pady=10, padx=20, fill="x")

        self.city_label = ctk.CTkLabel(self.main_card, text="Город не выбран", font=("Arial", 22, "bold"))
        self.city_label.pack(pady=(20, 5))

        self.temp_label = ctk.CTkLabel(self.main_card, text="--°", font=("Arial", 64, "bold"), text_color="#3B8ED0")
        self.temp_label.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main_card, text="Введите название и нажмите Поиск", font=("Arial", 14))
        self.status_label.pack(pady=(5, 20))

        self.forecast_title = ctk.CTkLabel(self, text="Прогноз на ближайшие дни:", font=("Arial", 16, "bold"))
        self.forecast_title.pack(pady=(10, 5), padx=25, anchor="w")

        self.forecast_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.forecast_frame.pack(pady=(5, 20), padx=20, fill="x")

        self.forecast_days = []
        for i in range(3):
            card = ctk.CTkFrame(self.forecast_frame, corner_radius=12, height=100)
            card.pack(side="left", expand=True, fill="both", padx=8)
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
            
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
            geo_response = requests.get(geo_url).json()

            if not geo_response.get("results"):
                self.status_label.configure(text="Город не найден :(")
                self.temp_label.configure(text="--°")
                return

            location = geo_response["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]

            city_name = location.get("name", city)
            country = location.get("country", "")
            full_location_name = f"{city_name}, {country}" if country else city_name

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max&timezone=auto"
            weather_response = requests.get(weather_url).json()

            current_weather = weather_response["current_weather"]
            temperature = round(current_weather["temperature"])
            
            forecast_data = weather_response["daily"]
            forecast_temps = forecast_data["temperature_2m_max"]
            forecast_dates = forecast_data["time"]

            self.city_label.configure(text=full_location_name)
            self.temp_label.configure(text=f"{temperature}°")
            self.status_label.configure(text="Данные успешно обновлены")

            for idx, card_widgets in enumerate(self.forecast_days):
                date_str = forecast_dates[idx + 1] # Формат YYYY-MM-DD
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
