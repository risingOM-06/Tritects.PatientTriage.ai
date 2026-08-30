import requests
import random
import time

API_URL = "http://localhost:8000/api/intake"

def generate_surge_patient(i):
    age = random.randint(1, 90)
    # 40% Ambulance, 60% Walk-in
    is_ambulance = random.random() < 0.40 
    
    if is_ambulance:
        mode = "Ambulance"
        has_history = True
        spo2 = random.randint(82, 98)
        hr = random.randint(70, 140)
        # Ambulances have telemetry: simulate some patients actively crashing in transit
        spo2_slope = round(random.uniform(-3.0, 0.5), 1) 
    else:
        mode = "Walk-In"
        has_history = random.choice([True, False])
        spo2 = random.randint(88, 100)
        hr = random.randint(60, 110)
        spo2_slope = 0.0 # Walk-ins only have a 2-minute snapshot, no trend

    return {
        "patient_id": f"MAS-{i:04d}", # MAS = Mass Casualty
        "age": age,
        "arrival_mode": mode,
        "has_history": has_history,
        "hr": hr,
        "rr": 18,
        "spo2": spo2,
        "temp_c": 37.5,
        "hr_slope": 0.0,
        "spo2_slope": spo2_slope
    }

print("🚨 INITIATING MASS CASUALTY SURGE (500 PATIENTS) 🚨")
print("Targeting Live API Engine...")

for i in range(1, 501):
    patient_data = generate_surge_patient(i)
    
    try:
        requests.post(API_URL, json=patient_data)
    except Exception as e:
        print("API Offline - Please start the FastAPI server.")
        break
        
    # Print a status update every 50 patients
    if i % 50 == 0:
        print(f"Injected {i}/500 patients into the Max-Heap...")
        time.sleep(0.5) # Slight pause to simulate chaotic arrival waves

print("✅ SURGE COMPLETE. Check your live dashboard!")