# 🏋️ RPG Fitness Tracker

Система геймификации физических упражнений с RPG-элементами: уровни, зоны тела, прогрессия и детренинг.

## 📋 Содержание

1. [Математические модели](#математические-модели)
2. [Структура данных](#структура-данных)
3. [База упражнений](#база-упражнений)
4. [Установка и запуск](#установка-и-запуск)
5. [Настройка параметров](#настройка-параметров)
6. [Рекомендации по балансу](#рекомендации-по-балансу)

---

## 🧮 Математические модели

### 1. Прогрессия уровня зоны

**Формула:** `XP_threshold(L) = BASE_XP × (L ^ EXPONENT)`

Где:
- `BASE_XP = 100` — базовое количество XP для уровня 1
- `EXPONENT = 1.8` — экспонента роста (полиномиальный рост)

**Таблица для первых 10 уровней:**

| Уровень | XP для след. | Накоплено XP |
|---------|--------------|--------------|
| 1 → 2   | 100          | 0            |
| 2 → 3   | 348          | 100          |
| 3 → 4   | 722          | 448          |
| 4 → 5   | 1,212        | 1,170        |
| 5 → 6   | 1,811        | 2,382        |
| 6 → 7   | 2,519        | 4,193        |
| 7 → 8   | 3,334        | 6,712        |
| 8 → 9   | 4,254        | 10,046       |
| 9 → 10  | 5,277        | 14,300       |
| 10 → 11 | 6,310        | 19,577       |

Для достижения **уровня 11** требуется накопить **~19,577 XP**.

### 2. Конверсия упражнений в XP

**Базовые формулы:**

- **Силовые (повторения):** `XP = sets × reps × XP_PER_REP_BASE × intensity_mult × zone_coeff`
- **Изометрические:** `XP = sets × (duration_sec / 10) × XP_PER_SECOND_HOLD × intensity_mult × zone_coeff`
- **Кардио (время):** `XP = (duration_min) × XP_PER_MINUTE_CARDIO × intensity_mult × zone_coeff`
- **Кардио (дистанция):** `XP = distance_km × XP_PER_KM_RUN × intensity_mult × zone_coeff`

**Константы:**
- `XP_PER_REP_BASE = 1.0`
- `XP_PER_SECOND_HOLD = 0.5`
- `XP_PER_MINUTE_CARDIO = 10.0`
- `XP_PER_KM_RUN = 50.0`

**Пример:** Приседания 3×15
- Base XP = 3 × 15 × 1.0 × 1.0 = 45 XP
- Legs (coeff 1.0): 45 × 1.0 = **45 XP**
- Core (coeff 0.4): 45 × 0.4 = **18 XP**
- Back (coeff 0.2): 45 × 0.2 = **9 XP**

### 3. Общий уровень (с пенальти за дисбаланс)

**ФОРМУЛА: Модифицированное гармоническое среднее**

```
Overall = n / Σ(1 / max(level_i, MIN_FLOOR))
```

Где `MIN_FLOOR = 1.0` защищает от деления на ноль.

**Почему гармоническое среднее?**

| Метод | Формула | Результат для Legs=100, Back=1, остальные=50 |
|-------|---------|---------------------------------------------|
| Арифметическое | Σlevels / n | **56.25** ❌ (не штрафует) |
| Геометрическое | (Πlevels)^(1/n) | **36.8** ⚠️ (мягко) |
| **Гармоническое** | n / Σ(1/level) | **7** ✅ (сильный штраф) |

**Расчёт для примера:**
```
sum_reciprocals = 1/100 + 1/1 + 6×(1/50) = 0.01 + 1 + 0.12 = 1.13
overall = 8 / 1.13 ≈ 7.08 → 7
```

Это даёт диапазон **~5–12** вместо 56, как требовалось!

### 4. Декремент (детренинг)

**Формула экспоненциального затухания:**

```
HL = HALFLIFE_DAYS + level × HALFLIFE_SCALE
loss_rate = ln(2) / HL
new_xp = old_xp × exp(-loss_rate × days_skipped)
```

**Правила:**
- **0–1 день пропуска:** без потерь (grace period)
- **2 дня:** начало мягкого снижения
- **3+ дня:** прогрессивный декремент

**Защитный буфер:** Минимум 10% XP никогда не сгорает.

**Пример расчёта:**
- Зона уровня 10, XP = 5000, пропуск 14 дней
- HL = 7 + 10 × 0.1 = 8 дней
- loss_rate = ln(2) / 8 ≈ 0.0866
- remaining = 5000 × exp(-0.0866 × 14) ≈ 5000 × 0.298 ≈ **1490 XP**
- С буфером: max(1490, 5000 × 0.10) = **1490 XP** (буфер не активен)

**Период полураспада:**
- Уровень 1: ~7 дней
- Уровень 10: ~8 дней
- Уровень 50: ~12 дней
- Уровень 100: ~17 дней

Чем выше уровень, тем быстрее теряется прогресс (принцип обратимости).

---

## 🗄️ Структура данных

### JSON-файл пользователя (`data/{user_id}.json`)

```json
{
  "user_id": "player1",
  "created_at": "2025-01-15T10:00:00",
  "difficulty": "normal",
  "zones": {
    "Legs": {
      "name": "Legs",
      "current_xp": 1250.5,
      "level": 5,
      "last_trained": "2025-01-20T14:30:00"
    },
    "Back": { ... },
    ...
  },
  "workout_log": [
    {
      "timestamp": "2025-01-20T14:30:00",
      "exercise_id": "squats_001",
      "exercise_name": "Приседания (Squats)",
      "sets": 3,
      "reps": 15,
      "duration_seconds": null,
      "distance_km": null,
      "xp_gained": {
        "Legs": 45.0,
        "Core": 18.0,
        "Back": 9.0
      }
    }
  ],
  "settings": {
    "apply_decrement_on_load": true,
    "timezone": "UTC"
  }
}
```

### SQLite схема (альтернатива)

```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    difficulty TEXT
);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    zone_name TEXT,
    current_xp REAL,
    level INTEGER,
    last_trained TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, zone_name)
);

CREATE TABLE workout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    exercise_id TEXT,
    timestamp TIMESTAMP,
    sets INTEGER,
    reps INTEGER,
    duration_seconds REAL,
    distance_km REAL,
    xp_data TEXT,  -- JSON
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_zones_user ON zones(user_id);
CREATE INDEX idx_workout_user ON workout_log(user_id);
CREATE INDEX idx_workout_timestamp ON workout_log(timestamp);
```

---

## 📚 База упражнений

В системе **46 упражнений** по 8 категориям:

| Категория | Количество | Примеры |
|-----------|------------|---------|
| **Legs** | 8 | Приседания, Выпады, Становая тяга, Wall Sit |
| **Back** | 6 | Подтягивания, Тяга в наклоне, Супермен |
| **Chest** | 5 | Отжимания, Жим лёжа, Dips |
| **Arms** | 6 | Bicep Curl, Tricep Extension, Chin-ups |
| **Core** | 6 | Планка, Скручивания, Leg Raises, Mountain Climbers |
| **Cardio** | 5 | Бег, Велосипед, Скакалка, Burpees, HIIT |
| **Flexibility/Mobility** | 6 | Йога, Растяжка, Foam Rolling, Hip Mobility |
| **Compound** | 4 | Thrusters, Clean & Press, Renegade Row, Bear Crawl |

**Пример записи упражнения:**

```json
{
  "id": "squats_001",
  "name": "Приседания (Squats)",
  "zones": {"Legs": 1.0, "Core": 0.4, "Back": 0.2},
  "type": "strength",
  "intensity_multiplier": 1.0,
  "recommendations": {
    "beginner": {"sets": 3, "reps": 10, "weight": "bodyweight"},
    "intermediate": {"sets": 4, "reps": 15, "weight": "moderate"},
    "advanced": {"sets": 5, "reps": 20, "weight": "heavy"}
  }
}
```

Полная база находится в файле `exercises_db.py`.

---

## 🚀 Установка и запуск

### Требования

- Python 3.10+
- Никаких внешних зависимостей (только стандартная библиотека)

### Быстрый старт

```bash
cd /workspace/rpg_fitness

# 1. Запустить демо-режим (показать формулы)
python progression.py

# 2. Запустить CLI интерфейс
python cli.py

# 3. Или с параметрами
python cli.py --data-dir ./my_data
python cli.py --demo
```

### Использование CLI

```
🏋️  RPG FITNESS TRACKER - Добро пожаловать!

--- АВТОРИЗАЦИЯ ---
1. Войти / Создать нового пользователя
2. Список пользователей
3. Выход

Выберите действие (1-3): 1
Введите имя пользователя: player1
✅ Пользователь player1 создан! Сложность: normal

--- ГЛАВНОЕ МЕНЮ ---
1. 📝 Записать тренировку
2. 📊 Просмотреть зоны тела
3. 🔍 Поиск упражнений
4. 📜 История тренировок
5. ⚙️  Настройки
6. 🚪 Выйти в меню пользователя
```

### Программное использование

```python
from database import Database
from progression import calculate_xp_from_exercise, calculate_overall_level
from exercises_db import get_exercise_by_id

# Инициализация
db = Database("./data")
db.create_user("test_user", difficulty="normal")

# Запись тренировки
exercise = get_exercise_by_id("squats_001")
xp = calculate_xp_from_exercise(exercise, sets=3, reps=15)

for zone_name, xp_amount in xp.items():
    db.update_zone_after_workout(zone_name, xp_amount)

db.save()

# Получить статистику
stats = db.get_user_stats()
print(f"Общий уровень: {stats['overall_level']}")
```

---

## ⚙️ Настройка параметров

Все параметры вынесены в `config.py`:

### Баланс прогрессии

```python
LEVEL_BASE_XP = 100.0      # Увеличить = медленнее прокачка
LEVEL_EXPONENT = 1.8       # 1.5 = мягче, 2.0 = круче
NEWBIE_BOOST = 1.5         # Множитель XP для уровней 1-5
```

### Декремент

```python
HALFLIFE_DAYS = 7.0        # Увеличить = медленнее потеря
HALFLIFE_SCALE = 0.1       # Влияние уровня на скорость потери
DECREMENT_BUFFER_PERCENT = 0.10  # 10% XP несгораемые
GRACE_PERIOD_DAYS = 1      # Дней без потерь
```

### Пресеты сложности

```python
DIFFICULTY_PRESETS = {
    "easy": {
        "LEVEL_BASE_XP": 80.0,     # Легче набирать
        "LEVEL_EXPONENT": 1.6,     # Мягкая кривая
        "HALFLIFE_DAYS": 10.0,     # Медленная потеря
        "NEWBIE_BOOST": 2.0,       # Большой бонус новичка
    },
    "normal": {...},
    "hard": {
        "LEVEL_BASE_XP": 150.0,    # Сложнее набирать
        "LEVEL_EXPONENT": 2.0,     # Крутая кривая
        "HALFLIFE_DAYS": 5.0,      # Быстрая потеря
        "NEWBIE_BOOST": 1.2,       # Маленький бонус
    },
}
```

### Зоны тела

```python
BODY_ZONES = [
    "Legs", "Back", "Chest", "Arms", 
    "Core", "Cardio", "Flexibility", "Mobility"
]
# Можно добавить или удалить зоны
```

---

## 💡 Рекомендации по балансу

### Для новичков

1. **Используйте пресет "easy"** первые 2-4 недели
2. **NEWBIE_BOOST = 2.0** даёт быструю обратную связь
3. **HALFLIFE_DAYS = 10.0** прощает пропуски
4. Фокусируйтесь на **3-4 зонах**, не распыляйтесь

### Масштабирование до 200+ уровня

1. **EXPONENT = 2.0** для поздних уровней (квадратичный рост)
2. Увеличьте `MAX_LEVEL_CAP` в config.py
3. Добавьте **престиж-систему** после уровня 100:
   - Сброс уровня с сохранением % бонуса к XP
   - Уникальные достижения

### Периодизация и восстановление

1. **Активное восстановление:**
   - Упражнения типа "Foam Rolling", "Static Stretching"
   - Дают XP в зоны Flexibility/Mobility
   - Не вызывают усталости

2. **Декремент как инструмент:**
   - После 7+ дней отдыха декремент симулирует реальную потерю формы
   - Используйте это для планирования циклов

3. **Сезонные корректировки:**
   - Отпуск: временно увеличьте `GRACE_PERIOD_DAYS`
   - Болезнь: ручной сброс декремента через настройки

### Как не перегрузить новичка

| Неделя | Фокус | Ожидаемый уровень |
|--------|-------|-------------------|
| 1-2 | 3 зоны, 2 тренировки/нед | 2-3 |
| 3-4 | 4 зоны, 3 тренировки/нед | 4-6 |
| 5-8 | Все зоны, 3-4 тренировки | 7-12 |
| 9+ | Специализация | 12+ |

**Признаки перегрузки:**
- Слишком быстрый рост (>5 уровней/неделю)
- Все зоны прокачаны равномерно (нет слабых мест)
- Нет мотивации из-за лёгкости

**Решение:** Переключиться на "normal" или "hard".

---

## 📄 Лицензия

MIT License. Используйте свободно для личных и коммерческих проектов.

## 🤝 Contributing

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

**Создано с 💪 для фитнес-энтузиастов и RPG-фанатов**
