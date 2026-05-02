"""
Модуль работы с базой данных (JSON бэкенд).
Хранение и загрузка данных пользователя.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from config import BODY_ZONES, DIFFICULTY_PRESETS
from progression import ZoneProgress, calculate_level_from_xp


class Database:
    """Класс для работы с JSON-базой данных."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_user: Optional[str] = None
        self.user_data: Dict[str, Any] = {}
    
    def _get_user_file_path(self, user_id: str) -> Path:
        """Получить путь к файлу пользователя."""
        return self.data_dir / f"{user_id}.json"
    
    def create_user(self, user_id: str, difficulty: str = "normal") -> bool:
        """
        Создать нового пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            difficulty: Уровень сложности ("easy", "normal", "hard")
        
        Returns:
            True если пользователь создан, False если уже существует
        """
        if difficulty not in DIFFICULTY_PRESETS:
            difficulty = "normal"
        
        file_path = self._get_user_file_path(user_id)
        if file_path.exists():
            return False
        
        # Инициализация зон
        zones = {}
        for zone_name in BODY_ZONES:
            zones[zone_name] = {
                "name": zone_name,
                "current_xp": 0.0,
                "level": 1,
                "last_trained": None,
            }
        
        user_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "difficulty": difficulty,
            "zones": zones,
            "workout_log": [],
            "settings": {
                "apply_decrement_on_load": True,
                "timezone": "UTC",
            },
        }
        
        self._save_user_data(user_id, user_data)
        self.current_user = user_id
        self.user_data = user_data
        return True
    
    def load_user(self, user_id: str) -> bool:
        """
        Загрузить данные пользователя.
        
        Returns:
            True если загрузка успешна, False если пользователь не найден
        """
        file_path = self._get_user_file_path(user_id)
        if not file_path.exists():
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.user_data = json.load(f)
        
        self.current_user = user_id
        return True
    
    def _save_user_data(self, user_id: str, data: Dict[str, Any]) -> None:
        """Сохранить данные пользователя в JSON файл."""
        file_path = self._get_user_file_path(user_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save(self) -> bool:
        """Сохранить текущие данные пользователя."""
        if not self.current_user:
            return False
        self._save_user_data(self.current_user, self.user_data)
        return True
    
    def get_zones(self) -> Dict[str, ZoneProgress]:
        """Получить все зоны пользователя как объекты ZoneProgress."""
        if not self.user_data:
            return {}
        
        zones = {}
        for zone_name, zone_data in self.user_data.get("zones", {}).items():
            zones[zone_name] = ZoneProgress.from_dict(zone_data)
        
        return zones
    
    def set_zone(self, zone: ZoneProgress) -> None:
        """Обновить данные зоны."""
        if not self.current_user:
            return
        
        self.user_data["zones"][zone.name] = zone.to_dict()
    
    def add_workout_log(self, workout: Dict[str, Any]) -> None:
        """Добавить запись о тренировке в лог."""
        if not self.current_user:
            return
        
        self.user_data["workout_log"].append(workout)
        
        # Ограничение размера лога (последние 1000 записей)
        if len(self.user_data["workout_log"]) > 1000:
            self.user_data["workout_log"] = self.user_data["workout_log"][-1000:]
    
    def get_workout_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получить последние записи из лога тренировок."""
        if not self.user_data:
            return []
        
        log = self.user_data.get("workout_log", [])
        return log[-limit:]
    
    def update_zone_after_workout(
        self, 
        zone_name: str, 
        xp_gained: float,
        timestamp: Optional[datetime] = None
    ) -> ZoneProgress:
        """
        Обновить зону после тренировки.
        
        Args:
            zone_name: Название зоны
            xp_gained: Количество полученного XP
            timestamp: Время тренировки (по умолчанию сейчас)
        
        Returns:
            Обновлённый объект ZoneProgress
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        zones = self.get_zones()
        if zone_name not in zones:
            # Создаём новую зону если не существует
            zone = ZoneProgress(name=zone_name, current_xp=xp_gained, level=1, last_trained=timestamp)
        else:
            zone = zones[zone_name]
            zone.current_xp += xp_gained
            zone.last_trained = timestamp
            
            # Пересчёт уровня
            new_level, _, _ = calculate_level_from_xp(zone.current_xp)
            zone.level = new_level
        
        self.set_zone(zone)
        return zone
    
    def apply_decrement_to_all(self, current_time: Optional[datetime] = None) -> Dict[str, ZoneProgress]:
        """
        Применить декремент ко всем зонам и сохранить изменения.
        
        Returns:
            Словарь обновлённых зон
        """
        from progression import apply_decrement_all_zones
        
        zones = self.get_zones()
        updated_zones = apply_decrement_all_zones(zones, current_time)
        
        # Сохраняем обновлённые зоны
        for zone in updated_zones.values():
            self.set_zone(zone)
        
        self.save()
        return updated_zones
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Получить общую статистику пользователя."""
        if not self.user_data:
            return {}
        
        zones = self.get_zones()
        total_workouts = len(self.user_data.get("workout_log", []))
        
        # Общий уровень
        from progression import calculate_overall_level
        overall_level = calculate_overall_level(zones)
        
        # Средний уровень зон
        avg_level = sum(z.level for z in zones.values()) / len(zones) if zones else 0
        
        # Зона с максимальным уровнем
        max_zone = max(zones.items(), key=lambda x: x[1].level) if zones else None
        
        # Зона с минимальным уровнем
        min_zone = min(zones.items(), key=lambda x: x[1].level) if zones else None
        
        return {
            "user_id": self.current_user,
            "overall_level": overall_level,
            "average_zone_level": round(avg_level, 2),
            "total_workouts": total_workouts,
            "max_zone": {"name": max_zone[0], "level": max_zone[1].level} if max_zone else None,
            "min_zone": {"name": min_zone[0], "level": min_zone[1].level} if min_zone else None,
            "created_at": self.user_data.get("created_at"),
            "difficulty": self.user_data.get("difficulty"),
        }
    
    def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя и его данные."""
        file_path = self._get_user_file_path(user_id)
        if file_path.exists():
            file_path.unlink()
            if self.current_user == user_id:
                self.current_user = None
                self.user_data = {}
            return True
        return False
    
    def list_users(self) -> List[str]:
        """Получить список всех пользователей."""
        users = []
        for file_path in self.data_dir.glob("*.json"):
            users.append(file_path.stem)
        return sorted(users)


# Функции удобства для быстрого доступа
def get_db(data_dir: str = "./data") -> Database:
    """Создать экземпляр Database."""
    return Database(data_dir)


def init_user(db: Database, user_id: str, difficulty: str = "normal") -> bool:
    """Инициализировать нового пользователя или загрузить существующего."""
    if not db.load_user(user_id):
        return db.create_user(user_id, difficulty)
    return True
