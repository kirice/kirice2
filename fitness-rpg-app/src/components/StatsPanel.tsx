import { useState } from 'react'

interface Zone {
  id: number
  name: string
  display_name: string
}

interface ZoneProgress {
  zone_id: number
  current_xp: number
  level: number
  last_trained: number | null
}

interface Exercise {
  name: string
  exercise_type: string
  zones: Record<string, number>
  base_xp_per_rep: number
  beginner_params: {
    sets: number
    reps: number
    rest_seconds: number
  }
  notes: string
}

interface StatsPanelProps {
  zones: Zone[]
  progress: Map<number, ZoneProgress>
  exercises: Exercise[]
  overallLevel: { level: number; xp: number; threshold: number } | null
  selectedZoneId: number | null
  onZoneSelect: (id: number | null) => void
  onLogWorkout: (exerciseName: string, sets: number, reps: number, intensityFactor: number) => void
  onApplyDecay: () => void
}

export default function StatsPanel({
  zones,
  progress,
  exercises,
  overallLevel,
  selectedZoneId,
  onZoneSelect,
  onLogWorkout,
  onApplyDecay,
}: StatsPanelProps) {
  const [selectedExercise, setSelectedExercise] = useState('')
  const [sets, setSets] = useState(3)
  const [reps, setReps] = useState(10)
  const [intensity, setIntensity] = useState(1.0)

  const handleLogWorkout = () => {
    if (selectedExercise) {
      onLogWorkout(selectedExercise, sets, reps, intensity)
      setSelectedExercise('')
      setSets(3)
      setReps(10)
      setIntensity(1.0)
    }
  }

  const getZoneProgressById = (zoneId: number): ZoneProgress | null => {
    return progress.get(zoneId) || null
  }

  const calculateXPThreshold = (level: number): number => {
    return 100 * Math.pow(level, 1.6)
  }

  return (
    <div className="stats-section">
      {/* Overall Level */}
      <div className="overall-level-card">
        <h2>ОБЩИЙ УРОВЕНЬ</h2>
        <div className="level-display">
          {overallLevel ? `Level ${overallLevel.level}` : '-'}
        </div>
        {overallLevel && (
          <>
            <div className="xp-bar-container">
              <div 
                className="xp-bar-fill" 
                style={{ width: `${(overallLevel.xp / overallLevel.threshold) * 100}%` }}
              />
              <div className="xp-bar-text">
                {overallLevel.xp.toFixed(0)} / {overallLevel.threshold.toFixed(0)} XP
              </div>
            </div>
          </>
        )}
      </div>

      {/* Zone List */}
      <div className="zone-list">
        {zones.map(zone => {
          const prog = getZoneProgressById(zone.id)
          const level = prog?.level || 1
          
          return (
            <div
              key={zone.id}
              className={`zone-item ${selectedZoneId === zone.id ? 'active' : ''}`}
              onClick={() => onZoneSelect(zone.id)}
            >
              <span className="zone-name">{zone.display_name}</span>
              <span className="zone-level">Lvl {level}</span>
            </div>
          )
        })}
      </div>

      {/* Selected Zone Details */}
      {selectedZoneId && (() => {
        const zone = zones.find(z => z.id === selectedZoneId)
        if (!zone) return null
        const prog = getZoneProgressById(selectedZoneId)
        
        return (
          <div style={{ 
            padding: '15px', 
            background: 'rgba(139, 26, 26, 0.1)',
            border: '2px solid #8b1a1a',
            borderRadius: '4px'
          }}>
            <h3 style={{ marginBottom: '10px', color: '#8b1a1a' }}>
              {zone.display_name}
            </h3>
            {prog && (
              <>
                <div>Уровень: <strong>{prog.level}</strong></div>
                <div>XP: <strong>{prog.current_xp.toFixed(1)}</strong></div>
                <div style={{ marginTop: '8px' }}>
                  Прогресс до {prog.level + 1} уровня:
                  <div className="xp-bar-container" style={{ height: '12px', marginTop: '5px' }}>
                    <div 
                      className="xp-bar-fill" 
                      style={{ 
                        width: `${Math.min((prog.current_xp / calculateXPThreshold(prog.level + 1)) * 100, 100)}%` 
                      }}
                    />
                  </div>
                </div>
                {prog.last_trained && (
                  <div style={{ fontSize: '0.8rem', marginTop: '8px', fontStyle: 'italic' }}>
                    Последняя тренировка: {new Date(prog.last_trained * 1000).toLocaleDateString()}
                  </div>
                )}
              </>
            )}
          </div>
        )
      })()}

      {/* Workout Log Section */}
      <div className="workout-section">
        <h3>ЗАПИСАТЬ ТРЕНИРОВКУ</h3>
        
        <select 
          className="exercise-select"
          value={selectedExercise}
          onChange={(e) => setSelectedExercise(e.target.value)}
        >
          <option value="">Выберите упражнение...</option>
          {exercises.map(ex => (
            <option key={ex.name} value={ex.name}>
              {ex.name} ({ex.exercise_type})
            </option>
          ))}
        </select>

        <div className="workout-form">
          <div className="form-group">
            <label>Подходы</label>
            <input 
              type="number" 
              min="1" 
              max="20"
              value={sets}
              onChange={(e) => setSets(parseInt(e.target.value) || 1)}
            />
          </div>
          
          <div className="form-group">
            <label>Повторения</label>
            <input 
              type="number" 
              min="1" 
              max="100"
              value={reps}
              onChange={(e) => setReps(parseInt(e.target.value) || 1)}
            />
          </div>
          
          <div className="form-group">
            <label>Интенсивность</label>
            <select value={intensity} onChange={(e) => setIntensity(parseFloat(e.target.value))}>
              <option value="1.0">Новичок (1.0x)</option>
              <option value="1.3">Средний (1.3x)</option>
              <option value="1.6">Продвинутый (1.6x)</option>
            </select>
          </div>
          
          <button className="log-button" onClick={handleLogWorkout}>
            ЗАПИСАТЬ
          </button>
        </div>
      </div>

      {/* Apply Decay Button (for testing) */}
      <button 
        onClick={onApplyDecay}
        style={{
          marginTop: '10px',
          padding: '8px',
          background: 'transparent',
          border: '1px solid #8b1a1a',
          color: '#8b1a1a',
          cursor: 'pointer',
          fontFamily: 'inherit',
          fontSize: '0.85rem'
        }}
      >
        Применить декремент (тест)
      </button>
    </div>
  )
}
