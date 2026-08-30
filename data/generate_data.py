import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

NUM_PATIENTS = 2000
patients = []

for i in range(NUM_PATIENTS):
    # 1. Demographics & Age Stratification
    age = random.randint(1, 90)
    if age < 12:
        age_group = "Pediatric"
        hr = random.randint(80, 140)
        rr = random.randint(20, 35)
    elif age > 65:
        age_group = "Geriatric"
        hr = random.randint(55, 90)
        rr = random.randint(14, 22)
    else:
        age_group = "Adult"
        hr = random.randint(60, 100)
        rr = random.randint(12, 20)

    # 2. Arrival Mode (Ambulance vs. Walk-In)
    arrival_mode = random.choices(["Ambulance", "Walk-In"], weights=[0.35, 0.65])[0]

    # 3. Simulate Data Depth based on Arrival Mode
    if arrival_mode == "Ambulance":
        has_history = True # Ambulances transmit ID/priors ahead
        # Continuous telemetry: has a rate of change (slope over time)
        spo2_slope = round(np.random.normal(-1.0, 1.5), 1) # negative means dropping
        hr_slope = round(np.random.normal(1.0, 2.5), 1)
    else:
        # Walk-in: 2-minute rapid snapshot, high uncertainty, 50% chance of zero history
        has_history = random.choices([True, False], weights=[0.5, 0.5])[0]
        spo2_slope = 0.0 # No trend available for a single snapshot
        hr_slope = 0.0

    # 4. Vitals & Clinical Anomalies
    is_critical = random.random() < 0.22
    if is_critical:
        spo2 = random.randint(80, 92)
        hr += random.randint(30, 50)
        temp_c = round(random.uniform(38.5, 40.5), 1)
        if arrival_mode == "Ambulance":
            spo2_slope -= random.uniform(1.5, 3.0) # Actively deteriorating in transit
    else:
        spo2 = random.randint(94, 100)
        temp_c = round(random.uniform(36.5, 37.5), 1)

    # 5. Calculate Target Safe Time Threshold (t_safe)
    t_safe = 120 
    if spo2 < 90: t_safe -= 70
    elif spo2 < 95: t_safe -= 30
    
    # Telemetry penalty for ambulance patients whose vitals are dropping
    if arrival_mode == "Ambulance" and spo2_slope < -1.5:
        t_safe -= 30

    # Pediatric / Geriatric specific rules
    if temp_c > 39.0 and age < 12: t_safe -= 40
    if temp_c < 35.5 and age > 65: t_safe -= 40

    # Asymmetric Uncertainty Penalty for zero-history walk-ins
    if arrival_mode == "Walk-In" and not has_history:
        t_safe = int(t_safe * 0.70) # Steeper penalty for zero-history walk-ins

    t_safe = max(0, t_safe)

    patients.append({
        "patient_id": f"PT-{i:04d}",
        "age": age,
        "is_pediatric": 1 if age < 12 else 0,
        "is_geriatric": 1 if age > 65 else 0,
        "is_ambulance": 1 if arrival_mode == "Ambulance" else 0,
        "has_history": 1 if has_history else 0,
        "hr": hr,
        "rr": rr,
        "spo2": spo2,
        "temp_c": temp_c,
        "hr_slope": hr_slope,
        "spo2_slope": spo2_slope,
        "target_t_safe_mins": t_safe
    })

df = pd.DataFrame(patients)
df.to_csv("triage_training_data.csv", index=False)
print("Upgraded dataset generated successfully with Ambulance telemetry & Walk-in snapshot profiles!")