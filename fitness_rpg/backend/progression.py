"""
Модуль прогрессии для Fitness RPG
Содержит все математические расчёты уровней, XP и декремента
"""

import math
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import json

from models import (
    ProgressionConfig, DecayConfig, OverallLevelConfig, AppConfig,
    ZoneProgress, ZoneWithLevel, OverallStats
)

logger = logging.getLogger(__name__)


class ProgressionCalculator:
    """
    Калькулятор прогрессии уровней
    
    Физиологическое обоснование:
    - Экспоненциальная кривая отражает закон убывающей отдачи
    - Гармоническое среднее штрафует за дисбаланс развития
    - Логарифмический декремент учитывает "мышечную память"
    """
    
    def __init__(self, config_path: str = None):
        """Инициализация с конфигурацией"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        self.config = self._load_config(config_path)
        logger.info(f"ProgressionCalculator инициализирован с config: {config_path}")
    
    def _load_config(self, config_path: Path) -> AppConfig:
        """Загрузка конфигурации из JSON"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return AppConfig(**config_data)
    
    # =========================================================================
    # РАСЧЁТ УРОВНЕЙ И ПОРОГОВ XP
    # =========================================================================
    
    def calculate_xp_threshold(self, level: int) -> float:
        """
        Расчёт порога XP для достижения уровня
        
        Формула: XP_threshold(L) = BASE_XP * (L ^ EXPONENT)
        
        Args:
            level: Целевой уровень (1-based)
            
        Returns:
            Порог XP для достижения этого уровня
            
        Пример:
            level=1 → 100 XP
            level=5 → 1360 XP
            level=10 → 4850 XP
        """
        if level < 1:
            return 0.0
        
        base_xp = self.config.progression.base_xp
        exponent = self.config.progression.exponent
        
        threshold = base_xp * (level ** exponent)
        return round(threshold, 2)
    
    def calculate_level_from_xp(self, current_xp: float) -> Tuple[int, float, float]:
        """
        Определение уровня по текущему XP
        
        Args:
            current_xp: Текущее количество опыта в зоне
            
        Returns:
            (level, xp_in_current_level, xp_to_next_level)
        """
        if current_xp <= 0:
            return (0, 0.0, self.calculate_xp_threshold(1))
        
        level = 1
        cumulative_xp = 0.0
        
        while True:
            threshold = self.calculate_xp_threshold(level)
            if cumulative_xp + threshold > current_xp:
                # Достигнут максимальный уровень
                xp_in_level = current_xp - cumulative_xp
                xp_to_next = threshold - xp_in_level
                return (level, round(xp_in_level, 2), round(xp_to_next, 2))
            
            cumulative_xp += threshold
            level += 1
            
            # Защита от бесконечного цикла
            if level > 1000:
                logger.warning("Достигнут предел уровня 1000")
                break
        
        # Если прошли все уровни
        xp_in_level = current_xp - cumulative_xp + self.calculate_xp_threshold(level - 1)
        next_threshold = self.calculate_xp_threshold(level)
        return (level - 1, round(xp_in_level, 2), round(next_threshold, 2))
    
    def calculate_excess_xp(self, current_xp: float, old_level: int, new_level: int) -> float:
        """
        Расчёт избыточного XP при переходе уровня
        
        При переходе на новый уровень избыток переносится
        """
        if new_level <= old_level:
            return 0.0
        
        cumulative_to_old = sum(self.calculate_xp_threshold(l) for l in range(1, old_level + 1))
        cumulative_to_new = sum(self.calculate_xp_threshold(l) for l in range(1, new_level + 1))
        
        excess = current_xp - cumulative_to_new
        return max(0.0, round(excess, 2))
    
    # =========================================================================
    # РАСЧЁТ ОБЩЕГО УРОВНЯ (PENALTY FOR IMBALANCE)
    # =========================================================================
    
    def calculate_overall_level(self, zone_levels: List[int]) -> OverallStats:
        """
        Расчёт общего уровня с пенальти за дисбаланс
        
        Формула: Modified Harmonic Mean с множителем дисперсии
        
        Step 1: Harmonic_Mean = N / Σ(1 / (level_i + 0.5))
        Step 2: Variance_Penalty = 1 - 0.25 × (σ_levels / max_level)
        Step 3: Overall_Level = floor(Harmonic_Mean × Variance_Penalty)
        
        Физиологическое обоснование:
        - Гармоническое среднее естественно "тянет вниз" при наличии слабых зон
        - Множитель дисперсии дополнительно штрафует за перекос развития
        - Сглаживающий член +0.5 обеспечивает устойчивость к нулевым уровням
        
        Args:
            zone_levels: Список уровней всех зон
            
        Returns:
            OverallStats с детальными метриками
        """
        if not zone_levels or all(l == 0 for l in zone_levels):
            return OverallStats(
                overall_level=0,
                overall_xp=0,
                overall_xp_threshold=self.calculate_xp_threshold(1),
                harmonic_mean=0,
                variance_penalty=1.0,
                zones_count=len(zone_levels),
                max_zone_level=0,
                min_zone_level=0
            )
        
        n = len(zone_levels)
        smoothing = self.config.progression.smoothing_constant
        
        # Шаг 1: Гармоническое среднее
        reciprocal_sum = sum(1.0 / (level + smoothing) for level in zone_levels if level >= 0)
        harmonic_mean = n / reciprocal_sum if reciprocal_sum > 0 else 0
        
        # Шаг 2: Стандартное отклонение и пенальти
        mean_level = sum(zone_levels) / n
        variance = sum((l - mean_level) ** 2 for l in zone_levels) / n
        std_dev = math.sqrt(variance)
        max_level = max(zone_levels) if zone_levels else 1
        
        variance_coefficient = self.config.overall_level.variance_penalty_coefficient
        variance_penalty = 1.0 - variance_coefficient * (std_dev / max_level) if max_level > 0 else 1.0
        variance_penalty = max(0.0, min(1.0, variance_penalty))  # Clamp to [0, 1]
        
        # Шаг 3: Итоговый уровень
        overall_level = int(math.floor(harmonic_mean * variance_penalty))
        
        # Расчёт XP для общего уровня
        overall_xp = sum(zone_levels) * 100  # Упрощённо
        overall_xp_threshold = self.calculate_xp_threshold(overall_level + 1)
        
        logger.debug(
            f"Overall level calculation: harmonic={harmonic_mean:.2f}, "
            f"variance_penalty={variance_penalty:.2f}, result={overall_level}"
        )
        
        return OverallStats(
            overall_level=overall_level,
            overall_xp=overall_xp,
            overall_xp_threshold=overall_xp_threshold,
            harmonic_mean=round(harmonic_mean, 2),
            variance_penalty=round(variance_penalty, 2),
            zones_count=n,
            max_zone_level=max_level,
            min_zone_level=min(zone_levels)
        )
    
    # =========================================================================
    # РАСЧЁТ XP ЗА УПРАЖНЕНИЕ
    # =========================================================================
    
    def calculate_exercise_xp(
        self,
        sets: int,
        reps: int,
        intensity_factor: float,
        base_xp_per_rep: float,
        zone_coefficient: float
    ) -> float:
        """
        Расчёт XP за упражнение
        
        Формула: XP = (sets × reps × intensity_factor) × base_xp_per_rep × zone_coefficient
        
        Args:
            sets: Количество подходов
            reps: Количество повторений
            intensity_factor: Множитель интенсивности (1.0/1.3/1.6)
            base_xp_per_rep: Базовое XP за повторение упражнения
            zone_coefficient: Коэффициент влияния на зону (0-1)
            
        Returns:
            Заработанный XP для конкретной зоны
        """
        if sets <= 0 or reps <= 0:
            logger.warning(f"Некорректные параметры: sets={sets}, reps={reps}")
            return 0.0
        
        xp = (sets * reps * intensity_factor) * base_xp_per_rep * zone_coefficient
        return round(xp, 2)
    
    # =========================================================================
    # СИСТЕМА ДЕКРЕМЕНТА (ДЕТРЕНИНГ)
    # =========================================================================
    
    def calculate_decay(
        self,
        current_xp: float,
        current_level: int,
        days_since_trained: int,
        vacation_mode: bool = False,
        illness_mode: bool = False
    ) -> Tuple[float, float, str]:
        """
        Расчёт потери XP из-за простоя
        
        Логика:
        - Days ≤ 1: 0% потерь (восстановление)
        - Days = 2: 5% от current_XP (мягкий старт)
        - Days ≥ 3: Progressive decay по формуле
        
        Формула ежедневной потери (для days ≥ 3):
        daily_loss = current_XP × (0.04 + 0.015 × log₂(current_level + 1))
        
        Защитный буфер:
        min_remaining_XP = max(10% × XP_threshold(current_level), 50 XP)
        
        Физиологическое обоснование:
        - Принцип обратимости: адаптации теряются без стимула
        - Логарифмическая зависимость: тренированные атлеты теряют медленнее
        - Защитный буфер: предотвращает полный откат до нуля
        
        Args:
            current_xp: Текущий XP в зоне
            current_level: Текущий уровень зоны
            days_since_trained: Дней с последней тренировки
            vacation_mode: Режим отпуска (нет потерь)
            illness_mode: Режим болезни (50% потерь)
            
        Returns:
            (xp_loss, remaining_xp, reason)
        """
        decay_config = self.config.decay
        
        # Проверка специальных режимов
        if vacation_mode:
            multiplier = decay_config.vacation_mode_decay_multiplier
            reason = "vacation_mode"
        elif illness_mode:
            multiplier = decay_config.illness_mode_decay_multiplier
            reason = "illness_mode"
        else:
            multiplier = 1.0
            reason = "normal"
        
        grace_period = decay_config.grace_period_days
        
        # День 0-1: нет потерь
        if days_since_trained <= grace_period:
            logger.debug(f"Grace period: {days_since_trained} дней, потерь нет")
            return (0.0, current_xp, f"grace_period_{days_since_trained}d")
        
        # День 2: мягкий декремент
        if days_since_trained == decay_config.soft_decay_day:
            loss = current_xp * decay_config.soft_decay_rate * multiplier
            remaining = current_xp - loss
            logger.debug(f"Soft decay day 2: loss={loss:.2f}")
            return (round(loss, 2), round(remaining, 2), "soft_decay_day_2")
        
        # День 3+: прогрессивный декремент
        level_scaling = decay_config.level_scaling_factor
        base_rate = decay_config.base_decay_rate
        
        # Логарифмический расчёт ежедневной потери
        daily_loss_rate = base_rate + level_scaling * math.log2(current_level + 1)
        daily_loss = current_xp * daily_loss_rate * multiplier
        
        # Применяем за все дни пропуска (кроме первых 2)
        decay_days = days_since_trained - grace_period - 1
        total_loss = daily_loss * decay_days
        
        # Расчёт защитного буфера
        xp_threshold = self.calculate_xp_threshold(current_level)
        min_buffer_percent = decay_config.min_buffer_percent
        min_buffer_absolute = decay_config.min_buffer_absolute
        
        min_remaining = max(
            xp_threshold * min_buffer_percent,
            min_buffer_absolute
        )
        
        # Ограничиваем потерю буфером
        actual_loss = min(total_loss, current_xp - min_remaining)
        actual_loss = max(0.0, actual_loss)  # Не может быть отрицательным
        
        remaining = current_xp - actual_loss
        
        logger.info(
            f"Decay calculation: level={current_level}, days={days_since_trained}, "
            f"daily_rate={daily_loss_rate:.3f}, loss={actual_loss:.2f}, remaining={remaining:.2f}"
        )
        
        return (
            round(actual_loss, 2),
            round(remaining, 2),
            f"progressive_decay_{decay_days}d"
        )
    
    def calculate_half_life(self, level: int) -> float:
        """
        Расчёт периода полураспада XP для уровня
        
        Период полураспада - время за которое теряется 50% XP
        
        Args:
            level: Уровень зоны
            
        Returns:
            Дней до потери 50% XP
        """
        decay_config = self.config.decay
        daily_loss_rate = decay_config.base_decay_rate + decay_config.level_scaling_factor * math.log2(level + 1)
        
        # t_half = ln(2) / daily_loss_rate
        half_life = math.log(2) / daily_loss_rate if daily_loss_rate > 0 else float('inf')
        
        return round(half_life, 1)
    
    # =========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =========================================================================
    
    def get_zone_with_level(self, zone_progress: ZoneProgress) -> ZoneWithLevel:
        """Конвертация ZoneProgress в ZoneWithLevel с расчётами"""
        level, xp_in_level, xp_to_next = self.calculate_level_from_xp(zone_progress.current_xp)
        
        current_threshold = self.calculate_xp_threshold(level)
        next_threshold = self.calculate_xp_threshold(level + 1)
        
        progress_percent = (xp_in_level / current_threshold * 100) if current_threshold > 0 else 0
        
        days_since = None
        if zone_progress.last_trained_date:
            days_since = (datetime.now() - zone_progress.last_trained_date).days
        
        return ZoneWithLevel(
            zone_name=zone_progress.zone_name,
            display_name=zone_progress.zone_name.title(),
            level=level,
            current_xp=xp_in_level,
            xp_to_next_level=xp_to_next,
            xp_threshold_current=current_threshold,
            xp_threshold_next=next_threshold,
            progress_percent=round(progress_percent, 1),
            last_trained_date=zone_progress.last_trained_date,
            days_since_trained=days_since
        )
    
    def get_intensity_multiplier(self, intensity_level: str) -> float:
        """Получение множителя интенсивности"""
        multipliers = {
            "beginner": 1.0,
            "intermediate": 1.3,
            "advanced": 1.6
        }
        return multipliers.get(intensity_level.lower(), 1.0)


# =============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# =============================================================================

if __name__ == "__main__":
    # Пример использования
    calc = ProgressionCalculator()
    
    print("=== Примеры расчётов ===\n")
    
    # 1. Пороги уровней
    print("1. Пороги XP для уровней:")
    for lvl in range(1, 11):
        print(f"   Уровень {lvl}: {calc.calculate_xp_threshold(lvl)} XP")
    
    # 2. Определение уровня по XP
    print("\n2. Определение уровня по XP:")
    test_xp_values = [50, 150, 500, 2000, 5000]
    for xp in test_xp_values:
        level, xp_in, xp_next = calc.calculate_level_from_xp(xp)
        print(f"   {xp} XP → Уровень {level} ({xp_in}/{xp_in + xp_next} XP)")
    
    # 3. Общий уровень с дисбалансом
    print("\n3. Общий уровень (с дисбалансом):")
    zone_levels = [10, 1, 5, 5, 5, 5, 5, 5]  # Legs=10, Back=1, остальные=5
    stats = calc.calculate_overall_level(zone_levels)
    print(f"   Уровни зон: {zone_levels}")
    print(f"   Гармоническое среднее: {stats.harmonic_mean}")
    print(f"   Пенальти дисперсии: {stats.variance_penalty}")
    print(f"   Итоговый уровень: {stats.overall_level}")
    
    # 4. Декремент
    print("\n4. Декремент (потери при простое):")
    for days in [1, 2, 3, 7, 14]:
        loss, remaining, reason = calc.calculate_decay(
            current_xp=2000,
            current_level=7,
            days_since_trained=days
        )
        print(f"   {days} дней: потеря {loss} XP, осталось {remaining} ({reason})")
    
    # 5. Период полураспада
    print("\n5. Период полураспада XP:")
    for lvl in [1, 5, 10, 20]:
        half_life = calc.calculate_half_life(lvl)
        print(f"   Уровень {lvl}: {half_life} дней")
