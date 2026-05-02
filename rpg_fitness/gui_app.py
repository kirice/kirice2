"""
RPG Fitness Tracker - GUI Приложение
Интерфейс с интерактивной моделью тела, анимациями и статистикой.
Технология: Flet (Python)
"""

import flet as ft
from flet import (
    Page, Text, Row, Column, Container, Icon, Divider, 
    ElevatedButton, TextField, Dropdown, dropdown, AlertDialog,
    TextButton, LinearGradient, Colors, alignment, border_radius,
    Animation, MainAxisAlignment, CrossAxisAlignment, ScrollMode,
    ThemeMode, Control, ControlEvent
)
import math
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Импорт логики из предыдущих модулей (предполагается, что они в той же папке)
# Если модули еще не созданы в этом контексте, мы продублируем минимальную логику здесь для автономности
# В реальном проекте лучше сделать: from progression import calculate_overall_level, get_xp_for_level

# --- КОНФИГУРАЦИЯ И ДАННЫЕ (Мини-версия для демонстрации) ---
BODY_ZONES = {
    "legs": {"name": "Ноги", "color": "0xFF5733"},
    "back": {"name": "Спина", "color": "0xC70039"},
    "chest": {"name": "Грудь", "color": "0x900C3F"},
    "arms": {"name": "Руки", "color": "0x581845"},
    "core": {"name": "Пресс", "color": "0x28B463"},
    "cardio": {"name": "Кардио", "color": "0x2E86C1"},
    "flexibility": {"name": "Гибкость", "color": "0xF1C40F"},
    "mobility": {"name": "Мобильность", "color": "0x8E44AD"}
}

EXERCISES_DB = [
    {"name": "Приседания", "zones": ["legs", "core", "back"], "coeffs": [1.0, 0.4, 0.2]},
    {"name": "Отжимания", "zones": ["chest", "arms", "core"], "coeffs": [1.0, 0.8, 0.3]},
    {"name": "Подтягивания", "zones": ["back", "arms", "core"], "coeffs": [1.0, 0.7, 0.3]},
    {"name": "Планка", "zones": ["core", "back", "legs"], "coeffs": [1.0, 0.5, 0.2]},
    {"name": "Бег", "zones": ["cardio", "legs", "core"], "coeffs": [1.0, 0.6, 0.3]},
    {"name": "Выпады", "zones": ["legs", "core"], "coeffs": [1.0, 0.3]},
    {"name": "Тяга гантели", "zones": ["back", "arms"], "coeffs": [1.0, 0.6]},
    {"name": "Жим лежа", "zones": ["chest", "arms", "core"], "coeffs": [1.0, 0.7, 0.2]},
]

# --- ЛОГИКА ПРОГРЕССИИ (Упрощенная копия) ---
def get_xp_threshold(level: int) -> int:
    return int(100 * (level ** 1.8))

def calculate_level(xp: int) -> tuple[int, int, int]:
    level = 1
    while xp >= get_xp_threshold(level):
        xp -= get_xp_threshold(level)
        level += 1
    return level, xp, get_xp_threshold(level)

def calculate_overall(levels: List[int]) -> int:
    if not levels: return 0
    # Гармоническое среднее с защитой от нуля
    safe_levels = [max(l, 1) for l in levels]
    n = len(safe_levels)
    harmonic_sum = sum(1 / l for l in safe_levels)
    return int(n / harmonic_sum)

# --- SVG МОДЕЛЬ ТЕЛА (Упрощенная схема) ---
# Координаты и пути для отрисовки силуэта человека
HUMAN_SVG_PATHS = {
    "head": "M 50 10 A 10 10 0 1 1 50 30 A 10 10 0 1 1 50 10 Z", # Голова (декор)
    "chest": "M 35 35 L 65 35 L 60 55 L 40 55 Z", # Грудь
    "abs": "M 40 56 L 60 56 L 58 75 L 42 75 Z", # Пресс (Core)
    "l_arm": "M 35 38 L 20 50 L 25 55 L 38 45 Z", # Левая рука
    "r_arm": "M 65 38 L 80 50 L 75 55 L 62 45 Z", # Правая рука
    "l_leg": "M 42 76 L 35 95 L 40 97 L 45 80 Z", # Левая нога
    "r_leg": "M 58 76 L 65 95 L 60 97 L 55 80 Z", # Правая нога
    "back": "M 35 35 L 65 35 L 65 55 L 35 55 Z", # Спина (задняя проекция, условно)
}

# Маппинг зон на части SVG
ZONE_MAP = {
    "legs": ["l_leg", "r_leg"],
    "arms": ["l_arm", "r_arm"],
    "chest": ["chest"],
    "core": ["abs"],
    "back": ["back"],
    # Cardio, Flexibility, Mobility - абстрактные, подсветим ореолом или цветом всего тела
    "cardio": ["chest", "abs"], 
    "flexibility": ["l_leg", "r_leg", "l_arm", "r_arm"],
    "mobility": ["chest", "abs", "l_leg", "r_leg"]
}

class RPGFitnessApp(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.user_data = self.load_data()
        self.hovered_zone = None
        
    def load_data(self):
        # Заглушка данных, в реальности читаем из JSON
        return {
            "zones": {z: {"xp": 0, "level": 1, "last_workout": None} for z in BODY_ZONES},
            "history": []
        }

    def build(self):
        self.page.title = "RPG Fitness Tracker"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a2e"
        self.page.padding = 20
        
        # Заголовок
        header = ft.Row([
            ft.Text("RPG FITNESS", size=30, weight="bold", color="#e94560"),
            ft.Icon(ft.icons.FITNESS_CENTER, color="#e94560")
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Общий уровень
        self.overall_level_text = ft.Text("Общий уровень: 1", size=20, color="#ffffff")
        self.update_overall_display()

        # Интерактивное тело (SVG)
        self.body_container = ft.Container(
            content=self.create_human_svg(),
            width=300,
            height=400,
            alignment=ft.alignment.center,
            on_hover=self.on_body_hover,
            tooltip="Наведи на зону тела"
        )

        # Панель статистики
        self.stats_column = ft.Column([], spacing=5, width=300)
        self.update_stats_panel()

        # Форма тренировки
        self.exercise_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(e["name"]) for e in EXERCISES_DB],
            label="Выберите упражнение",
            width=300,
            on_change=self.on_exercise_change
        )
        self.sets_field = ft.TextField(label="Подходы", value="3", width=100, keyboard_type=ft.KeyboardType.NUMBER)
        self.reps_field = ft.TextField(label="Повторы", value="10", width=100, keyboard_type=ft.KeyboardType.NUMBER)
        
        train_btn = ft.ElevatedButton(
            "Записать тренировку", 
            icon=ft.icons.PLAY_ARROW,
            bgcolor="#e94560",
            color="white",
            on_click=self.log_workout
        )

        form_row = ft.Row([
            self.exercise_dropdown,
            self.sets_field,
            self.reps_field,
            train_btn
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Сборка интерфейса
        return ft.Column([
            header,
            self.overall_level_text,
            ft.Divider(color="#333355"),
            ft.Row([
                # Левая колонка: Тело
                ft.Column([
                    self.body_container,
                    ft.Text("Наведите на зону для деталей", size=12, color="#666688", italic=True),
                ], alignment=ft.MainAxisAlignment.start, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                
                # Правая колонка: Статистика и Форма
                ft.Column([
                    self.stats_column,
                    ft.Divider(color="#333355"),
                    form_row,
                    ft.Container(height=20) # Отступ
                ], alignment=ft.MainAxisAlignment.start, horizontal_alignment=ft.CrossAxisAlignment.START)
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START)
        ], scroll=ft.ScrollMode.AUTO)

    def create_human_svg(self):
        """Создает SVG силуэт человека с интерактивными путями"""
        paths = []
        
        # Базовый контур (фон)
        paths.append(
            ft.Path(
                d="M 50 10 C 30 10 20 30 20 50 L 20 80 L 30 95 L 40 90 L 40 100 L 60 100 L 60 90 L 70 95 L 80 80 L 80 50 C 80 30 70 10 50 10 Z",
                fill="#2a2a40",
                stroke="#444466",
                stroke_width=2
            )
        )

        # Зоны (интерактивные)
        for zone_id, path_ids in ZONE_MAP.items():
            if zone_id in ["cardio", "flexibility", "mobility"]:
                continue # Эти зоны подсвечиваются логически, а не геометрически отдельно
            
            zone_color = BODY_ZONES.get(zone_id, {}).get("color", "#ffffff")
            hex_color = f"#{zone_color[2:]}"
            
            for pid in path_ids:
                if pid in HUMAN_SVG_PATHS:
                    paths.append(
                        ft.Path(
                            d=HUMAN_SVG_PATHS[pid],
                            fill=hex_color,
                            stroke="#ffffff",
                            stroke_width=1,
                            opacity=0.6,
                            data={"zone": zone_id}, # Данные для обработчика событий
                            on_hover=self.on_zone_hover,
                            on_click=lambda e, z=zone_id: self.select_zone(z)
                        )
                    )
        
        # Ореол для абстрактных зон (если выбраны)
        if self.hovered_zone in ["cardio", "flexibility", "mobility"]:
             paths.append(
                ft.Circle(
                    cx=50, cy=55, r=45,
                    fill="transparent",
                    stroke=f"#{BODY_ZONES[self.hovered_zone]['color'][2:]}",
                    stroke_width=3,
                    stroke_dasharray=[5, 5],
                    opacity=0.8
                )
             )

        return ft.Svg(
            content=ft.SvgContent(
                width="100%",
                height="100%",
                view_box="0 0 100 110",
                children=paths
            )
        )

    def on_body_hover(self, e):
        pass # Обработка на уровне всего контейнера не нужна, если есть точечные пути

    def on_zone_hover(self, e):
        """Реакция на наведение на конкретную часть тела"""
        if hasattr(e.control, 'data') and e.data == "true":
            zone = e.control.data.get("zone")
            if zone != self.hovered_zone:
                self.hovered_zone = zone
                self.update_stats_panel()
                self.page.update()
        elif e.data == "false":
            self.hovered_zone = None
            self.update_stats_panel()
            self.page.update()

    def select_zone(self, zone_name):
        """Клик по зоне открывает детали или фокусирует форму"""
        # Находим упражнение, которое качает эту зону, и выбираем его
        for ex in EXERCISES_DB:
            if zone_name in ex["zones"]:
                self.exercise_dropdown.value = ex["name"]
                break
        self.page.update()
        ft.alert("Зона выбрана", f"Вы выбрали тренировку для: {BODY_ZONES[zone_name]['name']}")

    def update_overall_display(self):
        levels = [calculate_level(z["xp"])[0] for z in self.user_data["zones"].values()]
        overall = calculate_overall(levels)
        self.overall_level_text.value = f"Общий уровень героя: {overall}"
        self.page.update()

    def update_stats_panel(self):
        """Обновляет панель статистики справа"""
        self.stats_column.controls.clear()
        
        title = ft.Text("Статистика зон", size=18, weight="bold", color="#a0a0c0")
        self.stats_column.controls.append(title)

        zones_to_show = [self.hovered_zone] if self.hovered_zone else list(BODY_ZONES.keys())

        for zone_key in zones_to_show:
            if zone_key not in BODY_ZONES: continue
            
            data = self.user_data["zones"][zone_key]
            lvl, curr_xp, next_xp = calculate_level(data["xp"])
            progress_pct = (curr_xp / next_xp) * 100 if next_xp > 0 else 0
            
            # Карточка зоны
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(BODY_ZONES[zone_key]["name"], weight="bold", color=f"#{BODY_ZONES[zone_key]['color'][2:]}"),
                        ft.Text(f"Lvl {lvl}", size=12, color="#888")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.LinearProgressIndicator(value=progress_pct/100, color=f"#{BODY_ZONES[zone_key]['color'][2:]}"),
                    ft.Text(f"{int(curr_xp)} / {next_xp} XP", size=10, color="#666")
                ], spacing=2),
                padding=10,
                bgcolor="#232335",
                border_radius=8,
                animate=ft.animation.Animation(300, "easeOut"),
                opacity=1.0 if self.hovered_zone is None or self.hovered_zone == zone_key else 0.3
            )
            
            # Анимация появления
            card.opacity = 0
            self.stats_column.controls.append(card)
            
        # Принудительная перерисовка для анимации
        self.page.update()
        
        # Запуск анимации прозрачности (через обновление состояния)
        for c in self.stats_column.controls[1:]:
            c.opacity = 1.0 if self.hovered_zone is None or (hasattr(c.content, 'controls') and len(c.content.controls) > 0) else 0.3
        self.page.update()

    def log_workout(self, e):
        """Запись тренировки и начисление XP"""
        ex_name = self.exercise_dropdown.value
        if not ex_name:
            ft.alert("Ошибка", "Выберите упражнение!")
            return
        
        try:
            sets = int(self.sets_field.value)
            reps = int(self.reps_field.value)
        except ValueError:
            ft.alert("Ошибка", "Введите корректные числа!")
            return

        # Поиск упражнения в БД
        ex_data = next((x for x in EXERCISES_DB if x["name"] == ex_name), None)
        if not ex_data:
            return

        # Расчет XP
        base_xp = sets * reps * 10 # Базовая формула
        
        # Распределение по зонам
        for i, zone in enumerate(ex_data["zones"]):
            coeff = ex_data["coeffs"][i]
            gained = int(base_xp * coeff)
            self.user_data["zones"][zone]["xp"] += gained
            self.user_data["zones"][zone]["last_workout"] = datetime.now().isoformat()
            
            # Проверка уровня
            new_lvl, _, _ = calculate_level(self.user_data["zones"][zone]["xp"])
            old_lvl, _, _ = calculate_level(self.user_data["zones"][zone]["xp"] - gained)
            
            if new_lvl > old_lvl:
                self.show_level_up_animation(zone, new_lvl)

        self.update_overall_display()
        self.update_stats_panel()
        ft.alert("Успех!", f"+{base_xp} XP получено!")
        self.save_data()

    def show_level_up_animation(self, zone, new_level):
        """Эффект повышения уровня"""
        dlg = ft.AlertDialog(
            title=ft.Text("LEVEL UP!", color="#e94560", weight="bold"),
            content=ft.Text(f"{BODY_ZONES[zone]['name']} достиг уровня {new_level}!"),
            actions=[ft.TextButton("Круто!", on_click=lambda e: self.page.close(dlg))]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def save_data(self):
        # Сохранение в JSON (упрощенно)
        with open("user_progress.json", "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)

def main(page: Page):
    app = RPGFitnessApp(page)
    page.add(app)

if __name__ == "__main__":
    ft.run(main=main, view=ft.AppView.WEB_BROWSER)
