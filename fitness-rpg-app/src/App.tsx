import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import CharacterSVG from './components/CharacterSVG'
import StatsPanel from './components/StatsPanel'

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

export default function App() {
  const [zones, setZones] = useState<Zone[]>([])
  const [progress, setProgress] = useState<Map<number, ZoneProgress>>(new Map())
  const [selectedZoneId, setSelectedZoneId] = useState<number | null>(null)
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [overallLevel, setOverallLevel] = useState<{level: number, xp: number, threshold: number} | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const zonesData = await invoke<Zone[]>('get_zones')
      setZones(zonesData)
      
      const allProgress = await invoke<[Zone, ZoneProgress][]>('get_all_progress')
      const progressMap = new Map<number, ZoneProgress>()
      allProgress.forEach(([_, prog]) => {
        progressMap.set(prog.zone_id, prog)
      })
      setProgress(progressMap)
      
      const exercisesData = await invoke<Exercise[]>('get_exercises')
      setExercises(exercisesData)
      
      const overall = await invoke<[number, number, number]>('calculate_overall')
      setOverallLevel({ level: overall[0], xp: overall[1], threshold: overall[2] })
      
      setLoading(false)
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
      setLoading(false)
    }
  }

  async function handleLogWorkout(exerciseName: string, sets: number, reps: number, intensityFactor: number) {
    try {
      await invoke('log_exercise', {
        exerciseName,
        sets,
        reps,
        intensityFactor
      })
      await loadData()
    } catch (error) {
      console.error('Ошибка записи тренировки:', error)
      alert('Не удалось записать тренировку: ' + error)
    }
  }

  async function handleApplyDecay() {
    try {
      await invoke<ZoneProgress[]>('apply_decay_tick')
      await loadData()
    } catch (error) {
      console.error('Ошибка применения декремента:', error)
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.5rem'
      }}>
        Загрузка...
      </div>
    )
  }

  return (
    <div className="app-container">
      <div className="character-section">
        <CharacterSVG 
          zones={zones}
          progress={progress}
          selectedZoneId={selectedZoneId}
          onZoneSelect={setSelectedZoneId}
        />
      </div>
      
      <StatsPanel 
        zones={zones}
        progress={progress}
        exercises={exercises}
        overallLevel={overallLevel}
        selectedZoneId={selectedZoneId}
        onZoneSelect={setSelectedZoneId}
        onLogWorkout={handleLogWorkout}
        onApplyDecay={handleApplyDecay}
      />
    </div>
  )
}
