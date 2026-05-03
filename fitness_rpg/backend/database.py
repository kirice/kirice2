"""
Модуль работы с базой данных для Fitness RPG
SQLite обёртка с CRUD операциями
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class Database:
    """
    Класс для работы с SQLite базой данных
    
    Использует контекстный менеджер для безопасного подключения
    """
    
    def __init__(self, db_path: str = None):
        """
        Инициализация подключения к БД
        
        Args:
            db_path: Путь к файлу базы данных (по умолчанию fitness_rpg.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent / "fitness_rpg.db"
        
        self.db_path = db_path
        logger.info(f"Database инициализирован: {db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Получение подключения к БД"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Возвращает строки как словари
        return conn
    
    def initialize_schema(self):
        """Инициализация схемы БД из SQL файла"""
        schema_path = Path(__file__).parent / "database_schema.sql"
        
        if not schema_path.exists():
            logger.error(f"Файл схемы не найден: {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        try:
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Схема БД успешно инициализирована")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации схемы: {e}")
            return False
    
    # =========================================================================
    # ОПЕРАЦИИ С ПОЛЬЗОВАТЕЛЯМИ
    # =========================================================================
    
    def create_user(self, username: str) -> Optional[int]:
        """
        Создание нового пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            ID созданного пользователя или None при ошибке
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, created_at, last_login) VALUES (?, ?, ?)",
                    (username, datetime.now(), datetime.now())
                )
                conn.commit()
                user_id = cursor.lastrowid
                logger.info(f"Создан пользователь: {username} (ID={user_id})")
                return user_id
        except sqlite3.IntegrityError as e:
            logger.warning(f"Пользователь уже существует: {username}")
            return self.get_user_by_name(username)['id'] if self.get_user_by_name(username) else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            return None
    
    def get_user_by_name(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по имени"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None
    
    def update_last_login(self, user_id: int):
        """Обновление времени последнего входа"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления last_login: {e}")
    
    def set_user_mode(self, user_id: int, vacation_mode: bool = None, illness_mode: bool = None):
        """Установка режимов пользователя (отпуск/болезнь)"""
        try:
            updates = []
            params = []
            
            if vacation_mode is not None:
                updates.append("vacation_mode = ?")
                params.append(vacation_mode)
            
            if illness_mode is not None:
                updates.append("illness_mode = ?")
                params.append(illness_mode)
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                
                with self.get_connection() as conn:
                    conn.execute(query, params)
                    conn.commit()
                    
            logger.info(f"Обновлены режимы пользователя {user_id}")
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления режимов: {e}")
    
    # =========================================================================
    # ОПЕРАЦИИ С ЗОНАМИ
    # =========================================================================
    
    def get_all_zones(self) -> List[Dict[str, Any]]:
        """Получение всех зон тела"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM zones ORDER BY order_index"
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения зон: {e}")
            return []
    
    def get_zone_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение зоны по имени"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM zones WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения зоны: {e}")
            return None
    
    def init_user_zones(self, user_id: int) -> bool:
        """
        Инициализация прогресса зон для нового пользователя
        
        Создаёт записи с нулевым прогрессом для всех зон
        """
        try:
            zones = self.get_all_zones()
            
            with self.get_connection() as conn:
                for zone in zones:
                    conn.execute(
                        """INSERT OR IGNORE INTO zone_progress 
                           (user_id, zone_id, current_xp, total_xp_earned, level) 
                           VALUES (?, ?, 0, 0, 0)""",
                        (user_id, zone['id'])
                    )
                conn.commit()
            
            logger.info(f"Инициализированы зоны для пользователя {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации зон: {e}")
            return False
    
    def get_user_zone_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение прогресса всех зон пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT zp.*, z.name as zone_name, z.display_name 
                       FROM zone_progress zp
                       JOIN zones z ON zp.zone_id = z.id
                       WHERE zp.user_id = ?
                       ORDER BY z.order_index""",
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения прогресса зон: {e}")
            return []
    
    def get_zone_progress(self, user_id: int, zone_name: str) -> Optional[Dict[str, Any]]:
        """Получение прогресса конкретной зоны"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT zp.*, z.name as zone_name, z.display_name 
                       FROM zone_progress zp
                       JOIN zones z ON zp.zone_id = z.id
                       WHERE zp.user_id = ? AND z.name = ?""",
                    (user_id, zone_name)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения прогресса зоны: {e}")
            return None
    
    def update_zone_xp(self, user_id: int, zone_name: str, xp_to_add: float) -> Optional[Dict[str, Any]]:
        """
        Добавление XP в зону
        
        Args:
            user_id: ID пользователя
            zone_name: Название зоны
            xp_to_add: Количество XP для добавления
            
        Returns:
            Обновлённый прогресс зоны или None
        """
        try:
            with self.get_connection() as conn:
                # Получаем текущий прогресс
                cursor = conn.execute(
                    """SELECT zp.*, z.id as zone_id FROM zone_progress zp
                       JOIN zones z ON zp.zone_id = z.id
                       WHERE zp.user_id = ? AND z.name = ?""",
                    (user_id, zone_name)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.error(f"Зона {zone_name} не найдена для пользователя {user_id}")
                    return None
                
                # Обновляем XP
                new_current_xp = row['current_xp'] + xp_to_add
                new_total_xp = row['total_xp_earned'] + xp_to_add
                
                conn.execute(
                    """UPDATE zone_progress 
                       SET current_xp = ?, total_xp_earned = ?, last_trained_date = ?
                       WHERE id = ?""",
                    (new_current_xp, new_total_xp, datetime.now(), row['id'])
                )
                conn.commit()
                
                logger.debug(f"Добавлено {xp_to_add} XP в зону {zone_name}")
                
                return self.get_zone_progress(user_id, zone_name)
                
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления XP зоны: {e}")
            return None
    
    def log_level_change(self, user_id: int, zone_id: int, old_level: int, 
                         new_level: int, old_xp: float, new_xp: float, 
                         change_type: str):
        """Логирование изменения уровня"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO level_history 
                       (user_id, zone_id, old_level, new_level, old_xp, new_xp, change_type)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, zone_id, old_level, new_level, old_xp, new_xp, change_type)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка логирования изменения уровня: {e}")
    
    # =========================================================================
    # ОПЕРАЦИИ С УПРАЖНЕНИЯМИ
    # =========================================================================
    
    def load_exercises_from_json(self, json_path: str = None) -> int:
        """
        Загрузка упражнений из JSON файла в БД
        
        Args:
            json_path: Путь к JSON файлу с упражнениями
            
        Returns:
            Количество загруженных упражнений
        """
        if json_path is None:
            json_path = Path(__file__).parent / "exercises_db.json"
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            exercises = data.get('exercises', [])
            zones_map = {z['name']: z['id'] for z in self.get_all_zones()}
            
            loaded_count = 0
            
            with self.get_connection() as conn:
                for ex in exercises:
                    # Вставляем упражнение
                    cursor = conn.execute(
                        """INSERT OR REPLACE INTO exercises 
                           (name, type, base_xp_per_rep, description, notes, is_active)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            ex['name'],
                            ex['type'],
                            ex['base_xp_per_rep'],
                            ex.get('notes', ''),
                            ex.get('notes', ''),
                            ex.get('is_active', True)
                        )
                    )
                    exercise_id = cursor.lastrowid
                    
                    # Вставляем коэффициенты зон
                    for zone_name, coeff in ex.get('zones', {}).items():
                        if zone_name in zones_map:
                            conn.execute(
                                """INSERT OR REPLACE INTO exercise_zone_coeffs
                                   (exercise_id, zone_id, coefficient)
                                   VALUES (?, ?, ?)""",
                                (exercise_id, zones_map[zone_name], coeff)
                            )
                    
                    loaded_count += 1
                
                conn.commit()
            
            logger.info(f"Загружено {loaded_count} упражнений из {json_path}")
            return loaded_count
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Ошибка загрузки упражнений: {e}")
            return 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка БД при загрузке упражнений: {e}")
            return 0
    
    def get_exercise_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение упражнения по имени"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM exercises WHERE name = ? AND is_active = 1",
                    (name,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения упражнения: {e}")
            return None
    
    def get_exercise_zone_coeffs(self, exercise_id: int) -> Dict[str, float]:
        """Получение коэффициентов зон для упражнения"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT z.name, ezc.coefficient
                       FROM exercise_zone_coeffs ezc
                       JOIN zones z ON ezc.zone_id = z.id
                       WHERE ezc.exercise_id = ?""",
                    (exercise_id,)
                )
                return {row['name']: row['coefficient'] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения коэффициентов: {e}")
            return {}
    
    def get_all_exercises(self) -> List[Dict[str, Any]]:
        """Получение всех активных упражнений"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM exercises WHERE is_active = 1 ORDER BY name"
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения упражнений: {e}")
            return []
    
    # =========================================================================
    # ОПЕРАЦИИ С ТРЕНИРОВКАМИ
    # =========================================================================
    
    def log_workout(self, user_id: int, exercise_id: int, sets: int, reps: int,
                    intensity_factor: float, xp_earned: float, notes: str = None) -> Optional[int]:
        """
        Логирование тренировки
        
        Args:
            user_id: ID пользователя
            exercise_id: ID упражнения
            sets: Количество подходов
            reps: Количество повторений
            intensity_factor: Множитель интенсивности
            xp_earned: Заработанный XP
            notes: Заметки
            
        Returns:
            ID записи о тренировке или None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """INSERT INTO workout_logs 
                       (user_id, exercise_id, workout_date, sets, reps, intensity_factor, xp_earned, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, exercise_id, datetime.now(), sets, reps, intensity_factor, xp_earned, notes)
                )
                conn.commit()
                log_id = cursor.lastrowid
                logger.info(f"Записана тренировка: user={user_id}, exercise={exercise_id}, log_id={log_id}")
                return log_id
        except sqlite3.Error as e:
            logger.error(f"Ошибка логирования тренировки: {e}")
            return None
    
    def log_zone_xp(self, workout_log_id: int, zone_id: int, xp_earned: float):
        """Логирование XP по зонам для тренировки"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO workout_zone_xp (workout_log_id, zone_id, xp_earned)
                       VALUES (?, ?, ?)""",
                    (workout_log_id, zone_id, xp_earned)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка логирования XP зоны: {e}")
    
    def get_user_workouts(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории тренировок пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT wl.*, e.name as exercise_name
                       FROM workout_logs wl
                       JOIN exercises e ON wl.exercise_id = e.id
                       WHERE wl.user_id = ?
                       ORDER BY wl.workout_date DESC
                       LIMIT ?""",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения истории тренировок: {e}")
            return []
    
    # =========================================================================
    # СТАТИСТИКА
    # =========================================================================
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение общей статистики пользователя"""
        try:
            with self.get_connection() as conn:
                # Количество тренировок
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM workout_logs WHERE user_id = ?",
                    (user_id,)
                )
                total_workouts = cursor.fetchone()['count']
                
                # Общий заработанный XP
                cursor = conn.execute(
                    "SELECT SUM(xp_earned) as total FROM workout_logs WHERE user_id = ?",
                    (user_id,)
                )
                total_xp = cursor.fetchone()['total'] or 0
                
                # Последняя тренировка
                cursor = conn.execute(
                    "SELECT MAX(workout_date) as last_date FROM workout_logs WHERE user_id = ?",
                    (user_id,)
                )
                last_workout = cursor.fetchone()['last_date']
                
                return {
                    'total_workouts': total_workouts,
                    'total_xp_earned': total_xp,
                    'last_workout_date': last_workout
                }
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}


# =============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    db = Database()
    
    # Инициализация схемы
    print("=== Инициализация БД ===")
    db.initialize_schema()
    
    # Загрузка упражнений
    print("\n=== Загрузка упражнений ===")
    count = db.load_exercises_from_json()
    print(f"Загружено упражнений: {count}")
    
    # Создание тестового пользователя
    print("\n=== Создание пользователя ===")
    user_id = db.create_user("test_user")
    print(f"ID пользователя: {user_id}")
    
    # Инициализация зон
    print("\n=== Инициализация зон ===")
    db.init_user_zones(user_id)
    
    # Получение зон
    zones = db.get_user_zone_progress(user_id)
    print(f"Зоны пользователя: {[z['zone_name'] for z in zones]}")
    
    # Получение упражнений
    exercises = db.get_all_exercises()
    print(f"\nВсего упражнений: {len(exercises)}")
    print(f"Примеры: {[e['name'] for e in exercises[:5]]}")
