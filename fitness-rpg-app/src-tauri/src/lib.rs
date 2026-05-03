use serde::{Deserialize, Serialize};
use rusqlite::{Connection, Result};
use chrono::{Utc, NaiveDateTime, Days};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

// ==================== МОДЕЛИ ДАННЫХ ====================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Zone {
    pub id: i32,
    pub name: String,
    pub display_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ZoneProgress {
    pub zone_id: i32,
    pub current_xp: f64,
    pub level: i32,
    pub last_trained: Option<i64>, // timestamp
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Exercise {
    pub name: String,
    pub exercise_type: String,
    pub zones: HashMap<String, f64>,
    pub base_xp_per_rep: f64,
    pub beginner_params: BeginnerParams,
    pub notes: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BeginnerParams {
    pub sets: i32,
    pub reps: i32,
    pub rest_seconds: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkoutLog {
    pub id: Option<i32>,
    pub exercise_name: String,
    pub sets: i32,
    pub reps: i32,
    pub intensity_factor: f64,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub base_xp: f64,
    pub exponent: f64,
    pub decay_start_days: i32,
    pub daily_decay_base: f64,
    pub daily_decay_level_mult: f64,
    pub min_remaining_percent: f64,
    pub min_remaining_absolute: f64,
    pub skip_days_tolerance: i32,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            base_xp: 100.0,
            exponent: 1.6,
            decay_start_days: 2,
            daily_decay_base: 0.04,
            daily_decay_level_mult: 0.015,
            min_remaining_percent: 0.1,
            min_remaining_absolute: 50.0,
            skip_days_tolerance: 2,
        }
    }
}

// ==================== ПРОГРЕССИЯ ====================

pub fn calculate_xp_threshold(level: i32, config: &Config) -> f64 {
    config.base_xp * (level as f64).powf(config.exponent)
}

pub fn calculate_level_from_xp(xp: f64, config: &Config) -> (i32, f64, f64) {
    let mut level = 1;
    let mut threshold = calculate_xp_threshold(level, config);
    
    while xp >= threshold && level < 200 {
        level += 1;
        threshold = calculate_xp_threshold(level, config);
    }
    
    let prev_threshold = if level > 1 {
        calculate_xp_threshold(level - 1, config)
    } else {
        0.0
    };
    
    let progress_in_level = xp - prev_threshold;
    let needed_for_next = threshold - prev_threshold;
    
    (level, progress_in_level, needed_for_next)
}

pub fn calculate_overall_level(zone_levels: &[i32]) -> i32 {
    if zone_levels.is_empty() {
        return 0;
    }
    
    let n = zone_levels.len() as f64;
    let sum_reciprocals: f64 = zone_levels.iter()
        .map(|&l| 1.0 / ((l as f64) + 0.5))
        .sum();
    
    let harmonic_mean = n / sum_reciprocals;
    
    let max_level = *zone_levels.iter().max().unwrap_or(&1) as f64;
    let mean_level = zone_levels.iter().sum::<i32>() as f64 / n;
    let variance: f64 = zone_levels.iter()
        .map(|&l| {
            let diff = (l as f64) - mean_level;
            diff * diff
        })
        .sum::<f64>() / n;
    let std_dev = variance.sqrt();
    
    let variance_penalty = if max_level > 0.0 {
        0.25 * (std_dev / max_level)
    } else {
        0.0
    };
    
    let penalty_multiplier = (1.0 - variance_penalty).max(0.5);
    let overall = harmonic_mean * penalty_multiplier;
    
    overall.floor() as i32
}

pub fn calculate_xp_for_exercise(
    sets: i32,
    reps: i32,
    intensity_factor: f64,
    base_xp_per_rep: f64,
    zone_coefficient: f64,
) -> f64 {
    (sets as f64 * reps as f64 * intensity_factor) * base_xp_per_rep * zone_coefficient
}

pub fn apply_decay(
    current_xp: f64,
    current_level: i32,
    days_since_trained: i32,
    config: &Config,
) -> f64 {
    if days_since_trained <= config.skip_days_tolerance {
        return current_xp;
    }
    
    let decay_days = days_since_trained - config.skip_days_tolerance;
    let daily_loss_rate = config.daily_decay_base 
        + config.daily_decay_level_mult * ((current_level + 1) as f64).log2();
    
    let mut remaining_xp = current_xp;
    for _ in 0..decay_days {
        let loss = remaining_xp * daily_loss_rate;
        remaining_xp -= loss;
    }
    
    let min_threshold = calculate_xp_threshold(current_level.max(1), config);
    let min_remaining = (min_threshold * config.min_remaining_percent)
        .max(config.min_remaining_absolute);
    
    remaining_xp.max(min_remaining)
}

// ==================== БАЗА ДАННЫХ ====================

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS zones (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL
            )",
            [],
        )?;
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS zone_progress (
                zone_id INTEGER PRIMARY KEY,
                current_xp REAL NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1,
                last_trained INTEGER,
                FOREIGN KEY (zone_id) REFERENCES zones(id)
            )",
            [],
        )?;
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_name TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                intensity_factor REAL NOT NULL,
                timestamp INTEGER NOT NULL
            )",
            [],
        )?;
        
        Ok(Database { conn })
    }
    
    pub fn init_zones(&self) -> Result<()> {
        let zones = [
            ("legs", "Legs"),
            ("back", "Back"),
            ("chest", "Chest"),
            ("arms", "Arms"),
            ("core", "Core"),
            ("cardio", "Cardio"),
            ("flexibility", "Flexibility"),
            ("mobility", "Mobility"),
            ("neck", "Neck"),
            ("grip", "Grip"),
        ];
        
        for (name, display) in zones {
            self.conn.execute(
                "INSERT OR IGNORE INTO zones (name, display_name) VALUES (?1, ?2)",
                [name, display],
            )?;
        }
        
        let mut stmt = self.conn.prepare("SELECT id FROM zones")?;
        let zone_ids: Vec<i32> = stmt.query_map([], |row| row.get(0))?
            .filter_map(Result::ok).collect();
        
        for zone_id in zone_ids {
            self.conn.execute(
                "INSERT OR IGNORE INTO zone_progress (zone_id, current_xp, level) VALUES (?1, 0, 1)",
                [zone_id],
            )?;
        }
        
        Ok(())
    }
    
    pub fn get_all_zones(&self) -> Result<Vec<Zone>> {
        let mut stmt = self.conn.prepare("SELECT id, name, display_name FROM zones")?;
        let zones = stmt.query_map([], |row| {
            Ok(Zone {
                id: row.get(0)?,
                name: row.get(1)?,
                display_name: row.get(2)?,
            })
        })?;
        
        zones.filter_map(Result::ok).collect()
    }
    
    pub fn get_zone_progress(&self, zone_id: i32) -> Result<ZoneProgress> {
        let mut stmt = self.conn.prepare(
            "SELECT zone_id, current_xp, level, last_trained FROM zone_progress WHERE zone_id = ?1"
        )?;
        
        stmt.query_row([zone_id], |row| {
            Ok(ZoneProgress {
                zone_id: row.get(0)?,
                current_xp: row.get(1)?,
                level: row.get(2)?,
                last_trained: row.get(3).ok(),
            })
        })
    }
    
    pub fn get_all_zone_progress(&self) -> Result<Vec<ZoneProgress>> {
        let mut stmt = self.conn.prepare(
            "SELECT zone_id, current_xp, level, last_trained FROM zone_progress"
        )?;
        
        let progress = stmt.query_map([], |row| {
            Ok(ZoneProgress {
                zone_id: row.get(0)?,
                current_xp: row.get(1)?,
                level: row.get(2)?,
                last_trained: row.get(3).ok(),
            })
        })?;
        
        progress.filter_map(Result::ok).collect()
    }
    
    pub fn add_xp_to_zone(&self, zone_id: i32, xp_amount: f64) -> Result<ZoneProgress> {
        let now = Utc::now().timestamp();
        
        let mut progress = self.get_zone_progress(zone_id)?;
        let new_xp = progress.current_xp + xp_amount;
        
        let config = Config::default();
        let (new_level, _, _) = calculate_level_from_xp(new_xp, &config);
        
        self.conn.execute(
            "UPDATE zone_progress SET current_xp = ?1, level = ?2, last_trained = ?3 WHERE zone_id = ?4",
            [new_xp, new_level, now, zone_id],
        )?;
        
        progress.current_xp = new_xp;
        progress.level = new_level;
        progress.last_trained = Some(now);
        
        Ok(progress)
    }
    
    pub fn log_workout(&self, log: &WorkoutLog) -> Result<i32> {
        let now = Utc::now().timestamp();
        
        self.conn.execute(
            "INSERT INTO workout_logs (exercise_name, sets, reps, intensity_factor, timestamp) VALUES (?1, ?2, ?3, ?4, ?5)",
            [&log.exercise_name, log.sets, log.reps, log.intensity_factor, now],
        )?;
        
        Ok(self.conn.last_insert_rowid() as i32)
    }
    
    pub fn apply_decay_to_all(&self, config: &Config) -> Result<Vec<ZoneProgress>> {
        let now = Utc::now().timestamp();
        let mut updated = Vec::new();
        
        let all_progress = self.get_all_zone_progress()?;
        
        for mut progress in all_progress {
            if let Some(last_trained) = progress.last_trained {
                let days_since = ((now - last_trained) / 86400) as i32;
                
                if days_since > config.skip_days_tolerance {
                    let new_xp = apply_decay(
                        progress.current_xp,
                        progress.level,
                        days_since,
                        config,
                    );
                    
                    if new_xp < progress.current_xp {
                        let (_, new_level, _,) = calculate_level_from_xp(new_xp, config);
                        
                        self.conn.execute(
                            "UPDATE zone_progress SET current_xp = ?1, level = ?2 WHERE zone_id = ?3",
                            [new_xp, new_level, progress.zone_id],
                        )?;
                        
                        progress.current_xp = new_xp;
                        progress.level = new_level;
                    }
                }
            }
            
            updated.push(progress);
        }
        
        Ok(updated)
    }
    
    pub fn get_recent_workouts(&self, limit: i32) -> Result<Vec<WorkoutLog>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, exercise_name, sets, reps, intensity_factor, timestamp FROM workout_logs ORDER BY timestamp DESC LIMIT ?1"
        )?;
        
        let logs = stmt.query_map([limit], |row| {
            Ok(WorkoutLog {
                id: Some(row.get(0)?),
                exercise_name: row.get(1)?,
                sets: row.get(2)?,
                reps: row.get(3)?,
                intensity_factor: row.get(4)?,
                timestamp: row.get(5)?,
            })
        })?;
        
        logs.filter_map(Result::ok).collect()
    }
}

// ==================== ЗАГРУЗКА УПРАЖНЕНИЙ ====================

pub fn load_exercises() -> Result<Vec<Exercise>, String> {
    let exe_path = std::env::current_exe().unwrap_or_default();
    let exe_dir = exe_path.parent().unwrap_or(Path::new("."));
    
    let json_paths = [
        exe_dir.join("exercises_db.json"),
        Path::new("backend/exercises_db.json").to_path_buf(),
        Path::new("exercises_db.json").to_path_buf(),
    ];
    
    let content = json_paths.iter()
        .find_map(|p| fs::read_to_string(p).ok())
        .ok_or_else(|| "Не удалось найти exercises_db.json".to_string())?;
    
    serde_json::from_str(&content)
        .map_err(|e| format!("Ошибка парсинга JSON: {}", e))
}

// ==================== TAURI COMMANDS ====================

#[tauri::command]
fn get_zones(db_state: tauri::State<Database>) -> Result<Vec<Zone>, String> {
    db_state.inner().get_all_zones().map_err(|e| e.to_string())
}

#[tauri::command]
fn get_zone_progress(db_state: tauri::State<Database>, zone_id: i32) -> Result<ZoneProgress, String> {
    db_state.inner().get_zone_progress(zone_id).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_all_progress(db_state: tauri::State<Database>) -> Result<Vec<(Zone, ZoneProgress)>, String> {
    let db = db_state.inner();
    let zones = db.get_all_zones().map_err(|e| e.to_string())?;
    let progress = db.get_all_zone_progress().map_err(|e| e.to_string())?;
    
    let mut result = Vec::new();
    for zone in zones {
        if let Some(prog) = progress.iter().find(|p| p.zone_id == zone.id) {
            result.push((zone.clone(), prog.clone()));
        }
    }
    
    Ok(result)
}

#[tauri::command]
fn log_exercise(
    db_state: tauri::State<Database>,
    exercise_name: String,
    sets: i32,
    reps: i32,
    intensity_factor: f64,
) -> Result<(), String> {
    let db = db_state.inner();
    
    let exercises = load_exercises().map_err(|e| e.to_string())?;
    let exercise = exercises.iter()
        .find(|e| e.name.to_lowercase() == exercise_name.to_lowercase())
        .ok_or_else(|| format!("Упражнение '{}' не найдено", exercise_name))?;
    
    let log = WorkoutLog {
        id: None,
        exercise_name: exercise.name.clone(),
        sets,
        reps,
        intensity_factor,
        timestamp: Utc::now().timestamp(),
    };
    
    db.log_workout(&log).map_err(|e| e.to_string())?;
    
    let config = Config::default();
    
    for (zone_name, &coefficient) in &exercise.zones {
        let zones = db.get_all_zones().map_err(|e| e.to_string())?;
        if let Some(zone) = zones.iter().find(|z| z.name == *zone_name) {
            let xp = calculate_xp_for_exercise(
                sets,
                reps,
                intensity_factor,
                exercise.base_xp_per_rep,
                coefficient,
            );
            
            db.add_xp_to_zone(zone.id, xp).map_err(|e| e.to_string())?;
        }
    }
    
    Ok(())
}

#[tauri::command]
fn calculate_overall(db_state: tauri::State<Database>) -> Result<(i32, f64, f64), String> {
    let db = db_state.inner();
    let progress = db.get_all_zone_progress().map_err(|e| e.to_string())?;
    
    let levels: Vec<i32> = progress.iter().map(|p| p.level).collect();
    let overall = calculate_overall_level(&levels);
    
    let config = Config::default();
    let total_xp: f64 = progress.iter().map(|p| p.current_xp).sum();
    let threshold = calculate_xp_threshold(overall, &config);
    
    Ok((overall, total_xp, threshold))
}

#[tauri::command]
fn apply_decay_tick(db_state: tauri::State<Database>) -> Result<Vec<ZoneProgress>, String> {
    let db = db_state.inner();
    let config = Config::default();
    db.apply_decay_to_all(&config).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_exercises() -> Result<Vec<Exercise>, String> {
    load_exercises()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(Database::new("fitness_rpg.db").expect("Не удалось создать БД"))
        .invoke_handler(tauri::generate_handler![
            get_zones,
            get_zone_progress,
            get_all_progress,
            log_exercise,
            calculate_overall,
            apply_decay_tick,
            get_exercises,
        ])
        .run(tauri::generate_context!())
        .expect("Ошибка при запуске приложения");
}
