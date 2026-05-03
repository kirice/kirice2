-- SQLite схема базы данных для Fitness RPG

-- Таблица пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    vacation_mode BOOLEAN DEFAULT FALSE,
    illness_mode BOOLEAN DEFAULT FALSE
);

-- Таблица зон тела
CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL
);

-- Прогресс по зонам
CREATE TABLE zone_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    current_xp REAL DEFAULT 0,
    total_xp_earned REAL DEFAULT 0,
    level INTEGER DEFAULT 0,
    last_trained_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE,
    UNIQUE(user_id, zone_id)
);

-- Таблица упражнений
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('strength', 'endurance', 'mobility', 'flexibility', 'cardio')),
    base_xp_per_rep REAL NOT NULL,
    description TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Коэффициенты упражнений для зон
CREATE TABLE exercise_zone_coeffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    coefficient REAL NOT NULL CHECK(coefficient > 0 AND coefficient <= 1.0),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE,
    UNIQUE(exercise_id, zone_id)
);

-- Логи тренировок
CREATE TABLE workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    workout_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    intensity_factor REAL DEFAULT 1.0,
    xp_earned REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

-- Детализированный XP по зонам для каждой тренировки
CREATE TABLE workout_zone_xp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_log_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    xp_earned REAL NOT NULL,
    FOREIGN KEY (workout_log_id) REFERENCES workout_logs(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
);

-- История изменений уровня (для отслеживания прогресса/декремента)
CREATE TABLE level_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    old_level INTEGER,
    new_level INTEGER,
    old_xp REAL,
    new_xp REAL,
    change_type TEXT CHECK(change_type IN ('gain', 'decay', 'manual')),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
);

-- Конфигурация пользователя
CREATE TABLE user_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    config_json TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для оптимизации
CREATE INDEX idx_zone_progress_user ON zone_progress(user_id);
CREATE INDEX idx_zone_progress_zone ON zone_progress(zone_id);
CREATE INDEX idx_workout_logs_user ON workout_logs(user_id);
CREATE INDEX idx_workout_logs_date ON workout_logs(workout_date);
CREATE INDEX idx_exercise_zone_exercise ON exercise_zone_coeffs(exercise_id);
CREATE INDEX idx_exercise_zone_zone ON exercise_zone_coeffs(zone_id);

-- Начальные данные: зоны тела
INSERT INTO zones (name, display_name, description, order_index) VALUES
('legs', 'Legs', 'Quadriceps, Hamstrings, Glutes, Calves', 1),
('back', 'Back', 'Latissimus Dorsi, Trapezius, Rhomboids, Erector Spinae', 2),
('chest', 'Chest', 'Pectoralis Major, Pectoralis Minor', 3),
('arms', 'Arms', 'Biceps, Triceps, Forearms', 4),
('core', 'Core', 'Abdominals, Obliques, Transverse Abdominis', 5),
('cardio', 'Cardio', 'Cardiovascular Endurance, VO2 Max', 6),
('flexibility', 'Flexibility', 'Overall Flexibility, Range of Motion', 7),
('mobility', 'Mobility', 'Joint Mobility, Functional Movement', 8),
('neck', 'Neck', 'Neck Muscles, Upper Trapezius', 9),
('grip', 'Grip', 'Forearm Strength, Grip Endurance', 10);
