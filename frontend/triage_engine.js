const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";

// -----------------------------------------------------
// 1. FETCH LIVE QUEUE FROM PYTHON BACKEND
// -----------------------------------------------------
async function fetchLiveQueue() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/queue`);
        const data = await response.json();
        renderDashboard(data);
    } catch (error) {
        console.error("Backend offline:", error);
        document.getElementById("erStatus").textContent = "API DISCONNECTED - START PYTHON SERVER";
        document.getElementById("erStatus").style.color = "red";
    }
}
// --- NEW ER ROOM STATE ---
let emergencyRooms = [null, null, null, null, null]; // 5 empty slots
let totalDischargedCount = 0;

function renderER() {
    const container = document.getElementById("er-rooms-container");
    container.innerHTML = emergencyRooms.map((patient, index) => `
        <div class="room-card ${patient ? 'occupied' : ''}">
            <div style="font-weight:bold; font-size:14px; margin-bottom:8px;">
                <span class="light ${patient ? 'light-red' : 'light-green'}"></span> ER ${index + 1}
            </div>
            ${patient ? `
                <div style="font-size:12px; font-weight:800; color:var(--danger)">${patient.patient_id}</div>
                <button class="primary" style="margin-top:10px; font-size:11px; width:100%; background:#172033" onclick="dischargePatient(${index})">⏏ Discharge</button>
            ` : `
                <div style="font-size:12px; color:var(--muted)">Vacant</div>
                <button class="primary" style="margin-top:10px; font-size:11px; width:100%; visibility:hidden;">—</button>
            `}
        </div>
    `).join("");
}
// Call this once on load
renderER();
// -----------------------------------------------------
// 2. RENDER THE UI
// -----------------------------------------------------
let selectedPatientId = null;
let currentQueueData = [];

function renderDashboard(data) {
    const q = data.queue;
    currentQueueData = q;

    // Update Top Stats
    document.getElementById("total").textContent = data.total_waiting;
    document.getElementById("critical").textContent = q.filter(p => p.risk_level === "Critical").length;
    document.getElementById("high").textContent = q.filter(p => p.risk_level === "High").length;
    document.getElementById("ambulance").textContent = q.filter(p => p.arrival_mode === "Ambulance").length;
    document.getElementById("nonambulance").textContent = q.filter(p => p.arrival_mode !== "Ambulance").length;

    const avgWait = q.length ? (q.reduce((acc, p) => acc + p.wait_time_min, 0) / q.length) : 0;
    document.getElementById("avgwait").textContent = avgWait.toFixed(1);

    // Update the pause button & ER status UI state
    const pauseBtn = document.getElementById("pauseBtn");
    if (data.is_paused) {
        pauseBtn.textContent = "▶ Resume Intake";
        pauseBtn.style.background = "#059669"; // Green
        document.getElementById("erStatus").textContent = "INTAKE PAUSED - SIMULATION RUNNING";
    } else {
        pauseBtn.textContent = "⏸ Pause Intake";
        pauseBtn.style.background = "#d97706"; // Orange
        document.getElementById("erStatus").textContent = "SYSTEM ONLINE & LISTENING";
    }

    // Check ER Capacity
    const hasVacantRoom = emergencyRooms.includes(null);
    document.getElementById("erFullWarning").style.display = hasVacantRoom ? "none" : "block";

    // Render Table
    const tbody = document.getElementById("queue");
    tbody.innerHTML = q.map((p, i) => {
    const riskLevel = p.risk_level || "Low";

    return `
        <tr class="${selectedPatientId === p.patient_id ? 'selected' : ''}" onclick="selectPatient('${p.patient_id}')">
          <td>${i + 1}</td>
          <td><b>${p.patient_id}</b></td>
          <td><b>${p.dynamic_score}</b> <span style="color:var(--muted); font-size:10px">(was ${p.base_risk_score})</span></td>
          <td>
                <span class="badge ${riskLevel.toLowerCase()}">
                    ${riskLevel}
                </span>
            </td>
          <td>${p.red_flag ? '<span class="red">YES</span>' : '—'}</td>
          <td>${p.wait_time_min.toFixed(1)}m</td>
          <td>${p.arrival_mode}</td>
          <td>
            <button class="primary" style="padding: 6px 10px; font-size: 11px; background:${hasVacantRoom ? '#059669' : '#9ca3af'}; cursor:${hasVacantRoom ? 'pointer' : 'not-allowed'}" 
                    onclick="${hasVacantRoom ? `treatPatient('${p.patient_id}'); event.stopPropagation();` : 'event.stopPropagation();'}"
                    ${hasVacantRoom ? '' : 'disabled'}>
              ${hasVacantRoom ? '✓ Treat' : 'ER FULL'}
            </button>
          </td>
        </tr>
    `;
}).join("");

    updateSelectedPatientDetails();
}

function selectPatient(id) {
    selectedPatientId = id;
    renderDashboard({ queue: currentQueueData, total_waiting: currentQueueData.length, is_paused: false }); 
}

function updateSelectedPatientDetails() {
    const detailsDiv = document.getElementById("details");
    if (!selectedPatientId) {
        detailsDiv.innerHTML = '<div style="color:var(--muted)">Select a patient from the queue to view AI inference.</div>';
        return;
    }

    const p = currentQueueData.find(x => x.patient_id === selectedPatientId);
    if (!p) return;

    detailsDiv.innerHTML = `
      <div class="detail-row"><span>Patient ID</span><b>${p.patient_id}</b></div>
      <div class="detail-row"><span>AI Risk Score</span><b>${p.base_risk_score}/100</b></div>
      <div class="detail-row"><span>Dynamic Score</span><b>${p.dynamic_score}/100</b></div>
      <div class="detail-row"><span>Risk Level</span><span class="badge ${p.risk_level.toLowerCase()}">${p.risk_level}</span></div>
      <div class="detail-row"><span>Predicted Safe Time</span><b style="color:#2563eb">${p.predicted_t_safe} mins</b></div>
      <div class="detail-row"><span>Red Flag Overrides</span><b class="${p.red_flag ? 'red' : 'green'}">${p.red_flag ? 'TRIGGERED' : 'CLEAR'}</b></div>
      <div class="detail-row"><span>Arrival Mode</span><b>${p.arrival_mode}</b></div>
      <div class="detail-row"><span>Elapsed Wait Time</span><b>${p.wait_time_min.toFixed(1)} min</b></div>
    `;
}

// -----------------------------------------------------
// 3. INJECT TEST PATIENT (Mixed Walk-in & Ambulance)
// -----------------------------------------------------
async function injectTestPatient() {
    const isAmbulance = Math.random() < 0.4; // 40% chance of ambulance
    const newPatient = {
        patient_id: (isAmbulance ? "AMB-" : "PT-") + Math.floor(Math.random() * 90000 + 10000),
        age: Math.floor(Math.random() * 80) + 1,
        arrival_mode: isAmbulance ? "Ambulance" : "Walk-In",
        has_history: isAmbulance ? true : Math.random() < 0.5,
        hr: Math.floor(Math.random() * 60) + 70,
        rr: 18,
        spo2: Math.floor(Math.random() * 20) + 80, // Generates some critical SpO2 values
        temp_c: 37.5,
        hr_slope: isAmbulance ? Number((Math.random() * 4 - 2).toFixed(1)) : 0.0,
        spo2_slope: isAmbulance ? Number((Math.random() * -3).toFixed(1)) : 0.0
    };
    
    await fetch(`${API_BASE_URL}/api/intake`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(newPatient)
    });
    
    fetchLiveQueue(); 
}

// Poll the Python server every 2 seconds
setInterval(fetchLiveQueue, 2000);
fetchLiveQueue();

// -----------------------------------------------------
// 4. CONTROLS (Reset, Pause, Treat)
// -----------------------------------------------------
async function resetEngine() {
    await fetch(`${API_BASE_URL}/api/reset`, { method: 'POST' });
    fetchLiveQueue();
}

async function togglePause() {
    await fetch(`${API_BASE_URL}/api/toggle_pause`, { method: 'POST' });
    fetchLiveQueue();
}

async function treatPatient(patientId) {
    // 1. Find the first available ER Room (Left to Right)
    const roomIndex = emergencyRooms.indexOf(null);
    if (roomIndex === -1) return; // Failsafe if full

    // 2. Grab patient data and move them to the ER Room
    const p = currentQueueData.find(x => x.patient_id === patientId);
    if (p) {
        emergencyRooms[roomIndex] = p;
        renderER(); // Turn light red
    }

    // 3. Remove them from the backend queue
    await fetch(`${API_BASE_URL}/api/treat/${patientId}`, {
    method: 'POST'
});
    fetchLiveQueue(); 
}

function dischargePatient(index) {
    const p = emergencyRooms[index];

    if (!p) return;

    emergencyRooms[index] = null;

    totalDischargedCount++;

    document.getElementById("dischargedCount").textContent =
        totalDischargedCount;

    renderER();

    fetchLiveQueue();
}