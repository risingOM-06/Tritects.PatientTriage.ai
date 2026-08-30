from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import heapq
import pickle
import pandas as pd
import time
from pathlib import Path

app = FastAPI(title="PatientTriage.ai Live Engine")

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "PatientTriage.ai Live Engine"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "model" / "triage_model.pkl"

print(f"Loading AI Model from: {model_path}")
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found: {model_path}")

with open(model_path, "rb") as f:
    model = pickle.load(f)

# Global Data Structures & State
patient_queue = []  
patient_database = {}  
intake_paused = False  # NEW: Tracks if the ER is accepting new patients

class PatientInput(BaseModel):
    patient_id: str
    age: int
    arrival_mode: str
    has_history: bool
    hr: int
    rr: int
    spo2: int
    temp_c: float
    hr_slope: float = 0.0
    spo2_slope: float = 0.0

# --- NEW: PAUSE ENDPOINT ---
@app.post("/api/toggle_pause")
async def toggle_pause():
    global intake_paused
    intake_paused = not intake_paused
    return {"status": "success", "is_paused": intake_paused}

# --- NEW: TREAT/REMOVE PATIENT ENDPOINT ---
@app.post("/api/treat/{patient_id}")
async def treat_patient(patient_id: str):
    global patient_queue
    if patient_id in patient_database:
        del patient_database[patient_id] # Remove from DB
        
        # O(n) Heap Rebuild to instantly remove them from the queue
        patient_queue = [item for item in patient_queue if item[1] != patient_id]
        heapq.heapify(patient_queue)
        return {"status": "success"}
    return {"status": "error", "message": "Patient not found"}

@app.post("/api/intake")
async def admit_patient(patient: PatientInput):
    global intake_paused
    
    # If the nurse paused the queue, reject the incoming patient
    if intake_paused:
        return {"status": "paused", "message": "ER Intake is currently paused."}

    features = pd.DataFrame([{
        "age": patient.age,
        "is_pediatric": 1 if patient.age < 12 else 0,
        "is_geriatric": 1 if patient.age > 65 else 0,
        "is_ambulance": 1 if patient.arrival_mode == "Ambulance" else 0,
        "has_history": 1 if patient.has_history else 0,
        "hr": patient.hr,
        "rr": patient.rr,
        "spo2": patient.spo2,
        "temp_c": patient.temp_c,
        "hr_slope": patient.hr_slope,
        "spo2_slope": patient.spo2_slope
    }])

    predicted_t_safe = model.predict(features)[0]
    base_risk_score = max(0, min(100, 100 - (predicted_t_safe / 120 * 100)))
    
    red_flag = True if patient.spo2 < 90 or predicted_t_safe < 15 else False

    patient_data = {
        "patient_id": patient.patient_id,
        "base_risk_score": round(base_risk_score, 1),
        "dynamic_score": round(base_risk_score, 1), # Starts equal to base
        "red_flag": red_flag,
        "wait_time_min": 0, 
        "arrival_mode": patient.arrival_mode,
        "arrival_timestamp": time.time(),
        "predicted_t_safe": round(predicted_t_safe, 1)
    }
    
    patient_database[patient.patient_id] = patient_data
    heapq.heappush(patient_queue, (-base_risk_score, patient.patient_id))
    
    return {"status": "success", "patient_id": patient.patient_id}

@app.get("/api/queue")
async def get_live_queue():
    global patient_queue
    current_time = time.time()
    response_queue = []
    new_heap = []
    
    # --- UPGRADED: THE DYNAMIC DECAY DAEMON ---
    for pat in patient_database.values():
        # 1. Calculate wait time (x10 for demo speed)
        pat["wait_time_min"] = round(((current_time - pat["arrival_timestamp"]) / 60) * 10, 1)
        
        # 2. Continuous Deterioration: Add 0.5 risk points for every 1 minute of waiting
        dynamic_score = min(100, pat["base_risk_score"] + (pat["wait_time_min"] * 0.5))
        pat["dynamic_score"] = round(dynamic_score, 1)
        
        # 3. Update Risk Level String based on the new dynamic score
        if dynamic_score >= 75: pat["risk_level"] = "Critical"
        elif dynamic_score >= 50: pat["risk_level"] = "High"
        elif dynamic_score >= 25: pat["risk_level"] = "Moderate"
        else: pat["risk_level"] = "Low"

        # 4. Prepare for re-heapification
        new_heap.append((-dynamic_score, pat["patient_id"]))
        
    # 5. Re-sort the Max-Heap using Python's highly optimized O(n) heapify
    heapq.heapify(new_heap)
    patient_queue = new_heap
    
    # 6. Read the newly sorted heap to send to the UI
    for neg_score, pid in sorted(patient_queue):
        response_queue.append(patient_database[pid])
        
    return {
        "total_waiting": len(response_queue),
        "queue": response_queue,
        "is_paused": intake_paused
    }

@app.post("/api/reset")
async def reset_engine():
    patient_queue.clear()
    patient_database.clear()
    return {"status": "Engine reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)