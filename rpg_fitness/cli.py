#!/usr/bin/env python3
"""
RPG Fitness Tracker - CLI интерфейс.
Консольное приложение для логирования тренировок, просмотра статистики
и управления прогрессом.

Использование:
    python cli.py              # Запустить интерактивный режим
    python cli.py --help       # Показать справку
"""

import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional, List

from config import BODY_ZONES, DIFFICULTY_PRESETS
from database import Database, init_user
from progression import (
    ZoneProgress, 
    calculate_overall_level, 
    calculate_xp_from_exercise,
    get_zone_progress_percentage,
    apply_decrement_all_zones,
)
from exercises_db import (
    EXERCISES, 
    get_exercise_by_id, 
    search_exercises, 
    get_exercises_by_zone,
)


class RPGFitnessCLI:
    """Класс CLI приложения."""
    
    def __init__(self, data_dir: str = "./data"):
        self.db = Database(data_dir)
        self.current_user: Optional[str] = None
    
    def start(self) -> None:
        """Запустить интерактивный режим CLI."""
        print("=" * 60)
        print("🏋️  RPG FITNESS TRACKER - Добро пожаловать!")
        print("=" * 60)
        
        while True:
            if not self.current_user:
                self._show_auth_menu()
            else:
                self._show_main_menu()
    
    def _show_auth_menu(self) -> None:
        """Меню авторизации."""
        print("\n--- АВТОРИЗАЦИЯ ---")
        print("1. Войти / Создать нового пользователя")
        print("2. Список пользователей")
        print("3. Выход")
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == "1":
            user_id = input("Введите имя пользователя: ").strip()
            if not user_id:
                print("❌ Имя пользователя не может быть пустым")
                return
            
            if self.db.load_user(user_id):
                print(f"✅ Добро пожаловать обратно, {user_id}!")
                self.current_user = user_id
            else:
                difficulty = input("Выберите сложность (easy/normal/hard) [normal]: ").strip() or "normal"
                if self.db.create_user(user_id, difficulty):
                    print(f"✅ Пользователь {user_id} создан! Сложность: {difficulty}")
                    self.current_user = user_id
                else:
                    print("❌ Ошибка создания пользователя")
        
        elif choice == "2":
            users = self.db.list_users()
            if users:
                print("\nПользователи:")
                for u in users:
                    print(f"  - {u}")
            else:
                print("\nНет зарегистрированных пользователей")
        
        elif choice == "3":
            print("До свидания! 💪")
            sys.exit(0)
    
    def _show_main_menu(self) -> None:
        """Главное меню."""
        # Применяем декремент при загрузке
        self.db.apply_decrement_to_all()
        
        stats = self.db.get_user_stats()
        print(f"\n{'='*60}")
        print(f"👤 Пользователь: {self.current_user}")
        print(f"⭐ Общий уровень: {stats['overall_level']}")
        print(f"📊 Средний уровень зон: {stats['average_zone_level']}")
        print(f"🏆 Макс. зона: {stats['max_zone']['name']} ({stats['max_zone']['level']})")
        print(f"⚠️  Мин. зона: {stats['min_zone']['name']} ({stats['min_zone']['level']})")
        print(f"{'='*60}")
        
        print("\n--- ГЛАВНОЕ МЕНЮ ---")
        print("1. 📝 Записать тренировку")
        print("2. 📊 Просмотреть зоны тела")
        print("3. 🔍 Поиск упражнений")
        print("4. 📜 История тренировок")
        print("5. ⚙️  Настройки")
        print("6. 🚪 Выйти в меню пользователя")
        
        choice = input("\nВыберите действие (1-6): ").strip()
        
        if choice == "1":
            self._log_workout()
        elif choice == "2":
            self._show_zones()
        elif choice == "3":
            self._search_exercises()
        elif choice == "4":
            self._show_history()
        elif choice == "5":
            self._show_settings()
        elif choice == "6":
            self.current_user = None
            self.db.user_data = {}
    
    def _log_workout(self) -> None:
        """Записать тренировку."""
        print("\n--- ЗАПИСЬ ТРЕНИРОВКИ ---")
        
        # Поиск упражнения
        query = input("Введите название упражнения или ID: ").strip()
        exercises = search_exercises(query)
        
        if not exercises:
            print("❌ Упражнение не найдено")
            return
        
        if len(exercises) > 1:
            print("\nНайдено несколько упражнений:")
            for i, ex in enumerate(exercises[:10]):
                print(f"  {i+1}. {ex['name']} (ID: {ex['id']})")
            
            try:
                idx = int(input("Выберите номер (1-10): ").strip()) - 1
                exercise = exercises[idx]
            except (ValueError, IndexError):
                print("❌ Неверный выбор")
                return
        else:
            exercise = exercises[0]
        
        print(f"\n✅ Выбрано: {exercise['name']}")
        print(f"   Зоны: {', '.join(exercise['zones'].keys())}")
        print(f"   Тип: {exercise['type']}")
        
        # Ввод параметров
        is_isometric = exercise.get("isometric", False)
        is_distance_based = exercise.get("distance_based", False)
        is_time_based = exercise.get("time_based", False)
        
        sets = 1
        reps = 0
        duration_seconds = None
        distance_km = None
        
        if is_distance_based:
            dist_input = input("Дистанция (км): ").strip()
            try:
                distance_km = float(dist_input) if dist_input else 0
            except ValueError:
                print("❌ Неверное значение дистанции")
                return
        elif is_time_based or is_isometric:
            dur_input = input("Длительность (секунд): ").strip()
            try:
                duration_seconds = float(dur_input) if dur_input else 0
            except ValueError:
                print("❌ Неверное значение длительности")
                return
        else:
            sets_input = input("Количество подходов: ").strip()
            reps_input = input("Повторения за подход: ").strip()
            try:
                sets = int(sets_input) if sets_input else 1
                reps = int(reps_input) if reps_input else 0
            except ValueError:
                print("❌ Неверные значения подходов/повторений")
                return
        
        if sets <= 0 and not (duration_seconds or distance_km):
            print("❌ Некорректные параметры тренировки")
            return
        
        # Расчёт XP
        zones = self.db.get_zones()
        avg_level = sum(z.level for z in zones.values()) / len(zones) if zones else 1
        
        xp_gained = calculate_xp_from_exercise(
            exercise=exercise,
            sets=sets,
            reps=reps,
            duration_seconds=duration_seconds,
            distance_km=distance_km,
            user_level_avg=avg_level,
        )
        
        if not xp_gained:
            print("❌ Не удалось рассчитать XP")
            return
        
        # Обновление зон
        timestamp = datetime.now()
        workout_log_entry = {
            "timestamp": timestamp.isoformat(),
            "exercise_id": exercise["id"],
            "exercise_name": exercise["name"],
            "sets": sets,
            "reps": reps,
            "duration_seconds": duration_seconds,
            "distance_km": distance_km,
            "xp_gained": xp_gained,
        }
        
        print("\n🎉 Получено XP:")
        for zone_name, xp in xp_gained.items():
            self.db.update_zone_after_workout(zone_name, xp, timestamp)
            print(f"   {zone_name}: +{xp:.1f} XP")
        
        self.db.add_workout_log(workout_log_entry)
        self.db.save()
        
        print("\n✅ Тренировка записана!")
    
    def _show_zones(self) -> None:
        """Показать прогресс по зонам."""
        print("\n--- ЗОНЫ ТЕЛА ---")
        
        zones = self.db.get_zones()
        overall_level = calculate_overall_level(zones)
        
        print(f"\n⭐ ОБЩИЙ УРОВЕНЬ: {overall_level}")
        print("-" * 50)
        print(f"{'Зона':<15} {'Уровень':<10} {'Прогресс':<25}")
        print("-" * 50)
        
        for zone_name in BODY_ZONES:
            if zone_name in zones:
                zone = zones[zone_name]
                progress_pct = get_zone_progress_percentage(zone)
                progress_bar = self._make_progress_bar(progress_pct, length=20)
                
                # Проверка на декремент
                warning = ""
                if zone.last_trained:
                    days_since = (datetime.now() - zone.last_trained).days
                    if days_since > 3:
                        warning = f" ⚠️  {days_since} дн. назад"
                
                print(f"{zone_name:<15} {zone.level:<10} {progress_bar} {warning}")
        
        print("-" * 50)
    
    def _make_progress_bar(self, progress: float, length: int = 20) -> str:
        """Создать визуальную полосу прогресса."""
        filled = int(length * progress)
        empty = length - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {progress*100:5.1f}%"
    
    def _search_exercises(self) -> None:
        """Поиск упражнений."""
        print("\n--- ПОИСК УПРАЖНЕНИЙ ---")
        
        while True:
            query = input("Введите запрос (или 'quit' для выхода): ").strip()
            if query.lower() in ("quit", "exit", "q"):
                break
            
            exercises = search_exercises(query)
            if not exercises:
                print("❌ Ничего не найдено")
                continue
            
            print(f"\nНайдено {len(exercises)} упражнений:")
            for ex in exercises[:20]:
                zones_str = ", ".join(f"{z}×{c}" for z, c in ex["zones"].items())
                print(f"  • {ex['name']}")
                print(f"    ID: {ex['id']} | Тип: {ex['type']} | Зоны: {zones_str}")
                
                rec = ex.get("recommendations", {})
                if "beginner" in rec:
                    beg = rec["beginner"]
                    if "reps" in beg:
                        print(f"    Новичок: {beg.get('sets', 3)}×{beg.get('reps', 10)}")
                    elif "duration_seconds" in beg:
                        print(f"    Новичок: {beg.get('duration_seconds', 30)} сек")
            
            if len(exercises) > 20:
                print(f"  ... и ещё {len(exercises) - 20}")
    
    def _show_history(self) -> None:
        """Показать историю тренировок."""
        print("\n--- ИСТОРИЯ ТРЕНИРОВОК ---")
        
        log = self.db.get_workout_log(limit=20)
        if not log:
            print("История пуста")
            return
        
        for entry in reversed(log):
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            name = entry.get("exercise_name", "Unknown")
            xp_total = sum(entry.get("xp_gained", {}).values())
            
            details = []
            if entry.get("sets"):
                details.append(f"{entry['sets']}×{entry.get('reps', 0)}")
            if entry.get("duration_seconds"):
                details.append(f"{entry['duration_seconds']} сек")
            if entry.get("distance_km"):
                details.append(f"{entry['distance_km']} км")
            
            print(f"  [{ts}] {name} ({', '.join(details)}) → +{xp_total:.1f} XP")
    
    def _show_settings(self) -> None:
        """Показать настройки."""
        print("\n--- НАСТРОЙКИ ---")
        
        stats = self.db.get_user_stats()
        print(f"Сложность: {stats.get('difficulty', 'unknown')}")
        print(f"Всего тренировок: {stats.get('total_workouts', 0)}")
        print(f"Дата регистрации: {stats.get('created_at', 'unknown')[:10]}")
        
        print("\nДействия:")
        print("1. Применить декремент вручную")
        print("2. Экспорт данных")
        print("3. Назад")
        
        choice = input("\nВыберите (1-3): ").strip()
        
        if choice == "1":
            self.db.apply_decrement_to_all()
            print("✅ Декремент применён")
        elif choice == "2":
            import json
            print(json.dumps(self.db.user_data, indent=2, ensure_ascii=False))


def main():
    """Точка входа CLI."""
    parser = argparse.ArgumentParser(description="RPG Fitness Tracker CLI")
    parser.add_argument("--data-dir", default="./data", help="Директория для данных")
    parser.add_argument("--demo", action="store_true", help="Запустить демо-режим")
    
    args = parser.parse_args()
    
    if args.demo:
        # Демо-режим: показать формулы и примеры
        from progression import demo_formulas
        demo_formulas()
        return
    
    cli = RPGFitnessCLI(args.data_dir)
    try:
        cli.start()
    except KeyboardInterrupt:
        print("\n\nДо свидания! 💪")
        sys.exit(0)


if __name__ == "__main__":
    main()
