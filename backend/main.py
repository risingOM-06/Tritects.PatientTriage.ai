from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import heapq
import pickle
import pandas as pd
import time
import os
import asyncio
import csv
from datetime import datetime
from pathlib import Path
app = FastAPI(title="PatientTriage.ai Live Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading AI Model...")
BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "model" / "triage_model.pkl"
print(f"Loading AI Model from: {model_path}")
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found: {model_path}")
with open(model_path, "rb") as f:
    model = pickle.load(f)
print("AI Model loaded successfully.")

# Global Data Structures & State
patient_queue = []  
patient_database = {}  
intake_paused = False  
start_time = time.time() # Tracks server uptime for the DevOps health check

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

# --- UPGRADE 1: TRUE BACKGROUND DAEMON ---
async def decay_daemon():
    """Runs continuously in the background, updating scores independent of the UI."""
    global patient_queue
    while True:
        if not intake_paused and patient_database:
            current_time = time.time()
            new_heap = []
            
            for pat in patient_database.values():
                # 1. Calculate wait time (x10 for demo speed)
                pat["wait_time_min"] = round(((current_time - pat["arrival_timestamp"]) / 60) * 10, 1)
                
                # 2. Continuous Deterioration: Add 0.5 risk points for every 1 minute of waiting
                dynamic_score = min(100, pat["base_risk_score"] + (pat["wait_time_min"] * 0.5))
                pat["dynamic_score"] = round(dynamic_score, 1)
                
                # 3. Update Risk Level String
                if dynamic_score >= 75: pat["risk_level"] = "Critical"
                elif dynamic_score >= 50: pat["risk_level"] = "High"
                elif dynamic_score >= 25: pat["risk_level"] = "Moderate"
                else: pat["risk_level"] = "Low"

                # 4. Prepare for re-heapification
                new_heap.append((-dynamic_score, pat["patient_id"]))
                
            # 5. Re-sort the Max-Heap in the background
            heapq.heapify(new_heap)
            patient_queue = new_heap
            
        # Run this decay loop every 2 seconds independently of API calls
        await asyncio.sleep(2)

# Trigger the daemon when the FastAPI server starts
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(decay_daemon())


@app.post("/api/toggle_pause")
async def toggle_pause():
    global intake_paused
    intake_paused = not intake_paused
    return {"status": "success", "is_paused": intake_paused}


# --- NEW: COMPLIANT AUDIT LOGGING ---
@app.post("/api/treat/{patient_id}")
async def treat_patient(patient_id: str):
    global patient_queue
    if patient_id in patient_database:
        # 1. Get the patient data before deleting it
        pat = patient_database[patient_id]
        
        # 2. Write to a permanent Audit Log (The "Enterprise Flex")
        audit_file = "clinical_audit_log.csv"
        file_exists = os.path.isfile(audit_file)
        
        with open(audit_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write headers if the file is brand new
            if not file_exists:
                writer.writerow(["Timestamp", "Patient_ID", "Arrival_Mode", "Wait_Time_Mins", "Final_Risk_Score", "AI_T_Safe_Prediction"])
            
            # Log the permanent record
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                pat["patient_id"],
                pat["arrival_mode"],
                pat["wait_time_min"],
                pat["dynamic_score"],
                pat["predicted_t_safe"]
            ])
            
        # 3. Remove from active memory
        del patient_database[patient_id] 
        patient_queue = [item for item in patient_queue if item[1] != patient_id]
        heapq.heapify(patient_queue)
        
        return {"status": "success", "message": "Patient treated and securely logged."}
    return {"status": "error", "message": "Patient not found"}


@app.post("/api/intake")
async def admit_patient(patient: PatientInput):
    global intake_paused
    
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
        "dynamic_score": round(base_risk_score, 1),
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
    """Now purely an O(n log n) read endpoint. The math is handled by the background daemon."""
    current_time = time.time()
    response_queue = []
    
    # 1. Read the background-sorted heap to send to the UI
    for neg_score, pid in sorted(patient_queue):
        if pid in patient_database:
            response_queue.append(patient_database[pid])
            
    # --- UPGRADE 2: FLOW ACCUMULATION METRIC ---
    # Count how many patients arrived in the last 60 seconds (real-time)
    inflow_last_minute = len([p for p in patient_database.values() if (current_time - p["arrival_timestamp"]) < 60])
    
    # If a surge hits (more than 15 patients a minute), trigger a systemic warning
    if inflow_last_minute > 15:
        system_status = "CRITICAL: ACCUMULATION RATE EXCEEDS CAPACITY"
    else:
        system_status = "STABLE: FLOW RATE NOMINAL"
        
    return {
        "total_waiting": len(response_queue),
        "queue": response_queue,
        "is_paused": intake_paused,
        "system_status": system_status
    }

@app.post("/api/reset")
async def reset_engine():
    patient_queue.clear()
    patient_database.clear()
    return {"status": "Engine reset"}

# --- DEVOPS HEALTH CHECK ---
@app.get("/api/health")
async def system_health():
    """DevOps monitoring endpoint for load balancers."""
    return {
        "status": "Healthy",
        "active_tasks": len(asyncio.all_tasks()),
        "heap_size_elements": len(patient_queue),
        "database_keys": len(patient_database.keys()),
        "ai_model_loaded": 'model' in globals() and model is not None,
        "uptime_sec": round(time.time() - start_time, 1)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)