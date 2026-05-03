/**
 * Fitness RPG - Frontend JavaScript
 * Интерактивный UI для карты тела и характеристик
 */

// ============================================================================
// КОНФИГУРАЦИЯ
// ============================================================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    ANIMATION_DURATION: 300,
    TOOLTIP_DELAY: 200,
    
    ZONE_MAPPING: {
        'neck': { displayName: 'Neck', svgId: 'zone-head' },
        'chest': { displayName: 'Chest', svgId: 'zone-torso' },
        'back': { displayName: 'Back', svgId: 'zone-back' },
        'arms': { displayName: 'Arms', svgId: 'zone-l-arm' },
        'core': { displayName: 'Core', svgId: 'zone-core' },
        'legs': { displayName: 'Legs', svgId: 'zone-legs' },
        'grip': { displayName: 'Grip', svgId: 'zone-grip' },
        'cardio': { displayName: 'Cardio', svgId: 'zone-cardio' },
        'flexibility': { displayName: 'Flexibility', svgId: 'zone-flexibility' },
        'mobility': { displayName: 'Mobility', svgId: 'zone-mobility' }
    },
    
    MOCK_DATA: {
        user: { id: 1, username: 'Adventurer' },
        zones: [
            { zone_name: 'legs', display_name: 'Legs', level: 5, current_xp: 850, xp_to_next_level: 510, xp_threshold_current: 1360, progress_percent: 62.5, days_since_trained: 0 },
            { zone_name: 'back', display_name: 'Back', level: 3, current_xp: 400, xp_to_next_level: 180, xp_threshold_current: 580, progress_percent: 69.0, days_since_trained: 2 },
            { zone_name: 'chest', display_name: 'Chest', level: 4, current_xp: 700, xp_to_next_level: 230, xp_threshold_current: 930, progress_percent: 75.3, days_since_trained: 1 },
            { zone_name: 'arms', display_name: 'Arms', level: 4, current_xp: 600, xp_to_next_level: 330, xp_threshold_current: 930, progress_percent: 64.5, days_since_trained: 3 },
            { zone_name: 'core', display_name: 'Core', level: 3, current_xp: 350, xp_to_next_level: 230, xp_threshold_current: 580, progress_percent: 60.3, days_since_trained: 0 },
            { zone_name: 'cardio', display_name: 'Cardio', level: 6, current_xp: 1200, xp_to_next_level: 678, xp_threshold_current: 1878, progress_percent: 63.9, days_since_trained: 1 },
            { zone_name: 'flexibility', display_name: 'Flexibility', level: 2, current_xp: 150, xp_to_next_level: 153, xp_threshold_current: 303, progress_percent: 49.5, days_since_trained: 5 },
            { zone_name: 'mobility', display_name: 'Mobility', level: 2, current_xp: 180, xp_to_next_level: 123, xp_threshold_current: 303, progress_percent: 59.4, days_since_trained: 4 },
            { zone_name: 'neck', display_name: 'Neck', level: 1, current_xp: 50, xp_to_next_level: 50, xp_threshold_current: 100, progress_percent: 50.0, days_since_trained: 7 },
            { zone_name: 'grip', display_name: 'Grip', level: 3, current_xp: 420, xp_to_next_level: 160, xp_threshold_current: 580, progress_percent: 72.4, days_since_trained: 2 }
        ],
        exercises: [
            { name: 'Squats', type: 'strength', zones: 'Legs, Core', base_xp: 2.5 },
            { name: 'Deadlifts', type: 'strength', zones: 'Back, Legs, Grip', base_xp: 3.0 },
            { name: 'Bench Press', type: 'strength', zones: 'Chest, Arms', base_xp: 2.5 },
            { name: 'Pull-ups', type: 'strength', zones: 'Back, Arms, Grip', base_xp: 2.0 },
            { name: 'Running', type: 'cardio', zones: 'Cardio, Legs', base_xp: 3.0 },
            { name: 'Plank', type: 'endurance', zones: 'Core', base_xp: 0.5 },
            { name: 'Lunges', type: 'strength', zones: 'Legs, Mobility', base_xp: 1.5 },
            { name: 'Push-ups', type: 'strength', zones: 'Chest, Arms, Core', base_xp: 1.5 }
        ]
    }
};

let state = {
    currentUser: null,
    zones: [],
    exercises: [],
    selectedZone: null,
    tooltipTimeout: null
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('Fitness RPG initialized');
    initApp();
});

async function initApp() {
    await loadMockData();
    setupZoneInteractions();
    renderOverallStats();
    renderExerciseList();
    console.log('App initialized with', state.zones.length, 'zones');
}

async function loadMockData() {
    state.currentUser = CONFIG.MOCK_DATA.user;
    state.zones = CONFIG.MOCK_DATA.zones;
    state.exercises = CONFIG.MOCK_DATA.exercises;
    document.getElementById('username').textContent = state.currentUser.username;
}

function setupZoneInteractions() {
    const zoneElements = document.querySelectorAll('.zone-zone');
    zoneElements.forEach(zoneEl => {
        const zoneName = zoneEl.dataset.zone;
        zoneEl.addEventListener('mouseenter', (e) => showTooltip(e, zoneName));
        zoneEl.addEventListener('mouseleave', hideTooltip);
        zoneEl.addEventListener('mousemove', moveTooltip);
        zoneEl.addEventListener('click', () => selectZone(zoneName));
    });
}

function selectZone(zoneName) {
    if (state.selectedZone) {
        const prevEl = document.querySelector(`[data-zone="${state.selectedZone}"]`);
        if (prevEl) prevEl.classList.remove('active');
    }
    state.selectedZone = zoneName;
    const zoneEl = document.querySelector(`[data-zone="${zoneName}"]`);
    if (zoneEl) zoneEl.classList.add('active');
    renderZoneDetails(zoneName);
    drawConnectionLines(zoneName);
}

function renderZoneDetails(zoneName) {
    const zoneData = state.zones.find(z => z.zone_name === zoneName);
    if (!zoneData) return;
    
    const container = document.getElementById('zone-details');
    const decayInfo = getDecayInfo(zoneData.days_since_trained, zoneData.level);
    
    container.innerHTML = `
        <div class="zone-card">
            <div class="zone-card-header">
                <span class="zone-card-title">${zoneData.display_name}</span>
                <span class="zone-card-level">Level ${zoneData.level}</span>
            </div>
            <div class="xp-info">
                <div class="xp-text">${Math.round(zoneData.current_xp)} / ${Math.round(zoneData.xp_threshold_current)} XP</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${zoneData.progress_percent}%"></div>
                </div>
            </div>
            <div class="zone-stats">
                <div class="zone-stat">
                    <span class="zone-stat-label">To Next:</span>
                    <span class="zone-stat-value">${Math.round(zoneData.xp_to_next_level)} XP</span>
                </div>
                <div class="zone-stat">
                    <span class="zone-stat-label">Last Trained:</span>
                    <span class="zone-stat-value">${getDaysAgoText(zoneData.days_since_trained)}</span>
                </div>
            </div>
            ${decayInfo.showWarning ? `<div class="decay-warning"><strong>⚠ Decay Warning:</strong> ${decayInfo.message}</div>` : ''}
        </div>
    `;
}

function getDecayInfo(daysSinceTrained, level) {
    if (daysSinceTrained <= 1) return { showWarning: false, message: '' };
    if (daysSinceTrained === 2) return { showWarning: true, message: 'Soft decay started (-5% XP)' };
    const dailyLossPercent = (4 + 1.5 * Math.log2(level + 1)).toFixed(1);
    return { showWarning: true, message: `Progressive decay active (~${dailyLossPercent}% per day)` };
}

function getDaysAgoText(days) {
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
}

function renderOverallStats() {
    const levels = state.zones.map(z => z.level);
    const overallLevel = calculateOverallLevel(levels);
    const totalXP = state.zones.reduce((sum, z) => sum + z.current_xp, 0);
    document.getElementById('overall-level').textContent = overallLevel;
    document.getElementById('total-xp').textContent = Math.round(totalXP);
}

function calculateOverallLevel(zoneLevels) {
    const n = zoneLevels.length;
    const smoothing = 0.5;
    const reciprocalSum = zoneLevels.reduce((sum, lvl) => sum + 1.0 / (lvl + smoothing), 0);
    const harmonicMean = n / reciprocalSum;
    const meanLevel = zoneLevels.reduce((a, b) => a + b, 0) / n;
    const variance = zoneLevels.reduce((sum, lvl) => sum + Math.pow(lvl - meanLevel, 2), 0) / n;
    const stdDev = Math.sqrt(variance);
    const maxLevel = Math.max(...zoneLevels, 1);
    const variancePenalty = 1 - 0.25 * (stdDev / maxLevel);
    return Math.floor(harmonicMean * variancePenalty);
}

function renderExerciseList() {
    const container = document.getElementById('exercise-items');
    container.innerHTML = state.exercises.map(ex => `
        <div class="exercise-item" data-exercise="${ex.name}">
            <div class="exercise-name">${ex.name}</div>
            <div class="exercise-meta">
                <span class="exercise-type">${ex.type}</span>
                <span class="exercise-zones">${ex.zones}</span>
                <span class="exercise-xp">${ex.base_xp} XP/rep</span>
            </div>
        </div>
    `).join('');
}

function showTooltip(event, zoneName) {
    const zoneData = state.zones.find(z => z.zone_name === zoneName);
    if (!zoneData) return;
    
    const tooltip = document.getElementById('tooltip');
    document.getElementById('tooltip-zone-name').textContent = zoneData.display_name;
    document.getElementById('tooltip-level').textContent = `Level ${zoneData.level}`;
    document.getElementById('tooltip-xp-text').textContent = `${Math.round(zoneData.current_xp)} / ${Math.round(zoneData.xp_threshold_current)} XP`;
    document.getElementById('tooltip-progress-fill').style.width = `${zoneData.progress_percent}%`;
    
    if (zoneData.days_since_trained > 1) {
        document.getElementById('tooltip-decay').textContent = `⚠ ${zoneData.days_since_trained} days since training`;
    } else {
        document.getElementById('tooltip-decay').textContent = '';
    }
    
    state.tooltipTimeout = setTimeout(() => {
        tooltip.classList.add('visible');
    }, CONFIG.TOOLTIP_DELAY);
}

function hideTooltip() {
    clearTimeout(state.tooltipTimeout);
    document.getElementById('tooltip').classList.remove('visible');
}

function moveTooltip(event) {
    const tooltip = document.getElementById('tooltip');
    let x = event.clientX + 15;
    let y = event.clientY + 15;
    const tooltipRect = tooltip.getBoundingClientRect();
    if (x + tooltipRect.width > window.innerWidth) x = event.clientX - tooltipRect.width - 15;
    if (y + tooltipRect.height > window.innerHeight) y = event.clientY - tooltipRect.height - 15;
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
}

function drawConnectionLines(zoneName) {
    const linesContainer = document.getElementById('connection-lines');
    linesContainer.innerHTML = '';
    
    const lineCoords = {
        'neck': { x1: 0, y1: 100, x2: 200, y2: 80 },
        'chest': { x1: 0, y1: 200, x2: 200, y2: 180 },
        'back': { x1: 0, y1: 180, x2: 200, y2: 150 },
        'arms': { x1: 0, y1: 180, x2: 130, y2: 180 },
        'core': { x1: 0, y1: 280, x2: 200, y2: 230 },
        'legs': { x1: 0, y1: 400, x2: 200, y2: 350 },
        'grip': { x1: 0, y1: 240, x2: 122, y2: 235 },
        'cardio': { x1: 0, y1: 170, x2: 200, y2: 170 },
        'flexibility': { x1: 0, y1: 150, x2: 200, y2: 150 },
        'mobility': { x1: 0, y1: 300, x2: 200, y2: 280 }
    };
    
    const coords = lineCoords[zoneName];
    if (!coords) return;
    
    const trackLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    trackLine.setAttribute('x1', coords.x1);
    trackLine.setAttribute('y1', coords.y1);
    trackLine.setAttribute('x2', coords.x2);
    trackLine.setAttribute('y2', coords.y2);
    trackLine.setAttribute('class', 'connection-line connection-line-track');
    
    const fillLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    fillLine.setAttribute('x1', coords.x1);
    fillLine.setAttribute('y1', coords.y1);
    fillLine.setAttribute('x2', coords.x2);
    fillLine.setAttribute('y2', coords.y2);
    fillLine.setAttribute('class', 'connection-line connection-line-fill');
    
    linesContainer.appendChild(trackLine);
    linesContainer.appendChild(fillLine);
    
    requestAnimationFrame(() => {
        trackLine.style.opacity = '0.3';
        fillLine.style.opacity = '1';
    });
}

function calculateXPThreshold(level, baseXP = 100, exponent = 1.6) {
    if (level < 1) return 0;
    return baseXP * Math.pow(level, exponent);
}

function calculateExerciseXP(sets, reps, intensityFactor, baseXPPerRep, zoneCoefficient) {
    if (sets <= 0 || reps <= 0) return 0;
    return (sets * reps * intensityFactor) * baseXPPerRep * zoneCoefficient;
}

window.FitnessRPG = { state, selectZone, calculateXPThreshold, calculateExerciseXP };
