import { useState, useRef } from 'react'

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

interface CharacterSVGProps {
  zones: Zone[]
  progress: Map<number, ZoneProgress>
  selectedZoneId: number | null
  onZoneSelect: (id: number | null) => void
}

const ZONE_PATHS: Record<string, string> = {
  head: 'M 200,60 C 200,60 185,70 185,90 C 185,110 200,120 200,120 C 200,120 215,110 215,90 C 215,70 200,60 200,60',
  neck: 'M 195,120 L 195,135 L 205,135 L 205,120',
  chest: 'M 185,135 L 185,180 L 215,180 L 215,135',
  back: 'M 185,135 L 175,180 L 225,180 L 215,135',
  arms_left: 'M 185,140 L 155,140 L 155,190 L 185,190',
  arms_right: 'M 215,140 L 245,140 L 245,190 L 215,190',
  core: 'M 185,180 L 185,220 L 215,220 L 215,180',
  legs: 'M 185,220 L 185,280 L 195,280 L 195,220 M 205,220 L 205,280 L 215,280 L 215,220',
  cardio: 'M 190,150 C 190,150 195,145 200,150 C 205,145 210,150 210,150 C 210,150 205,160 200,155 C 195,160 190,150 190,150',
  flexibility: 'M 175,200 Q 165,220 175,240 M 225,200 Q 235,220 225,240',
  mobility: 'M 185,280 L 185,300 M 215,280 L 215,300',
  grip: 'M 155,190 L 145,200 M 245,190 L 255,200',
}

const ZONE_CONNECTION_POINTS: Record<string, { x: number, y: number }> = {
  head: { x: 230, y: 90 },
  neck: { x: 230, y: 127 },
  chest: { x: 230, y: 157 },
  back: { x: 230, y: 157 },
  arms_left: { x: 230, y: 165 },
  arms_right: { x: 230, y: 165 },
  core: { x: 230, y: 200 },
  legs: { x: 230, y: 250 },
  cardio: { x: 230, y: 152 },
  flexibility: { x: 230, y: 220 },
  mobility: { x: 230, y: 290 },
  grip: { x: 230, y: 195 },
}

export default function CharacterSVG({ zones, progress, selectedZoneId, onZoneSelect }: CharacterSVGProps) {
  const [hoveredZone, setHoveredZone] = useState<string | null>(null)
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })
  const svgRef = useRef<SVGSVGElement>(null)

  const getZoneProgress = (zoneName: string): ZoneProgress | null => {
    const zone = zones.find(z => z.name === zoneName)
    if (!zone) return null
    return progress.get(zone.id) || null
  }

  const handleMouseEnter = (zoneName: string, event: React.MouseEvent) => {
    setHoveredZone(zoneName)
    if (svgRef.current) {
      const rect = svgRef.current.getBoundingClientRect()
      setTooltipPos({
        x: event.clientX - rect.left + 20,
        y: event.clientY - rect.top - 50
      })
    }
  }

  const handleClick = (zoneName: string) => {
    const zone = zones.find(z => z.name === zoneName)
    if (zone) {
      onZoneSelect(selectedZoneId === zone.id ? null : zone.id)
    }
  }

  const renderZonePath = (zoneName: string, displayName: string) => {
    const zone = zones.find(z => z.name === zoneName)
    const isSelected = zone && selectedZoneId === zone.id
    const prog = getZoneProgress(zoneName)
    const level = prog?.level || 1
    const xp = prog?.current_xp || 0

    return (
      <g key={zoneName}>
        <path
          className={`zone-path ${isSelected ? 'active' : ''}`}
          d={ZONE_PATHS[zoneName]}
          onMouseEnter={(e) => handleMouseEnter(zoneName, e)}
          onMouseLeave={() => setHoveredZone(null)}
          onClick={() => handleClick(zoneName)}
          style={{
            strokeWidth: isSelected ? 3 : 2,
            stroke: isSelected ? '#8b1a1a' : '#1a1a1a',
          }}
        />
        {hoveredZone === zoneName && (
          <foreignObject 
            x={tooltipPos.x} 
            y={tooltipPos.y} 
            width="200" 
            height="120"
            className="tooltip"
          >
            <div>
              <div className="tooltip-title">{displayName}</div>
              <div className="tooltip-xp">Уровень {level}</div>
              <div className="tooltip-bar">
                <div 
                  className="tooltip-bar-fill" 
                  style={{ width: `${Math.min((xp / (100 * Math.pow(level, 1.6))) * 100, 100)}%` }}
                />
              </div>
              <div style={{ fontSize: '0.75rem', marginTop: '5px' }}>
                XP: {xp.toFixed(0)} / {(100 * Math.pow(level + 1, 1.6)).toFixed(0)}
              </div>
            </div>
          </foreignObject>
        )}
      </g>
    )
  }

  return (
    <svg 
      ref={svgRef}
      viewBox="0 0 400 350" 
      className="character-svg"
      style={{ overflow: 'visible' }}
    >
      {/* Connection lines to stats panel */}
      {selectedZoneId && (() => {
        const zone = zones.find(z => z.id === selectedZoneId)
        if (!zone) return null
        
        const startPoint = Object.entries(ZONE_PATHS).find(([name]) => name === zone.name)?.[1]
        if (!startPoint) return null
        
        const startX = 230
        const startY = ZONE_CONNECTION_POINTS[zone.name]?.y || 150
        
        return (
          <g className="connection-lines-container">
            {/* Bottom line (track) */}
            <line
              x1={startX}
              y1={startY}
              x2={350}
              y2={startY}
              className="connection-line"
            />
            {/* Top line (fill) */}
            <line
              x1={startX}
              y1={startY - 3}
              x2={350}
              y2={startY - 3}
              className="connection-line-fill"
              style={{ strokeDashoffset: 0 }}
            />
            {/* Small person icon at end */}
            <circle cx={355} cy={startY - 3} r={3} fill="#1a1a1a" />
          </g>
        )
      })()}

      {/* Body zones */}
      {renderZonePath('head', 'Head')}
      {renderZonePath('neck', 'Neck')}
      {renderZonePath('chest', 'Chest')}
      {renderZonePath('back', 'Back')}
      {renderZonePath('arms_left', 'Arms')}
      {renderZonePath('arms_right', 'Arms')}
      {renderZonePath('core', 'Core')}
      {renderZonePath('legs', 'Legs')}
      {renderZonePath('cardio', 'Cardio')}
      {renderZonePath('flexibility', 'Flexibility')}
      {renderZonePath('mobility', 'Mobility')}
      {renderZonePath('grip', 'Grip')}
    </svg>
  )
}
