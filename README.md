# 🏥 PatientTriage.ai

### Real-Time AI-Assisted Emergency Department Prioritization System

**PatientTriage.ai** is a real-time emergency department triage simulation and decision-support prototype that prioritizes patients based on predicted clinical urgency, dynamic deterioration while waiting, and emergency room capacity.

Unlike a traditional first-come-first-served queue, PatientTriage.ai continuously re-evaluates patient priority as waiting time increases and dynamically updates the treatment queue.

> ⚠️ **Disclaimer:** PatientTriage.ai is an educational and simulation prototype. It is not a clinically validated medical device and must not be used for real-world diagnosis, treatment, or medical decision-making.

---

## 🌐 Live Demo

🚀 **Frontend:** https://tritects-patient-triage-ai.vercel.app/

The application is deployed using:

* **Frontend:** Vercel
* **Backend:** Railway
* **API Framework:** FastAPI
* **Machine Learning:** Scikit-learn
* **Data Processing:** Pandas
* **Core Data Structure:** Max-Heap Priority Queue

---

# 📌 Problem Statement

Emergency departments often face overcrowding and limited treatment capacity.

A major challenge is that patient urgency is **not static**.

A patient who initially appears stable may deteriorate while waiting, meaning a simple first-come-first-served queue may not always prioritize the patient with the highest current urgency.

PatientTriage.ai explores the following question:

> **How can a real-time software system continuously prioritize patients based on predicted urgency, waiting time, and treatment capacity?**

---

# 💡 Our Solution

PatientTriage.ai implements a live triage simulation engine that combines:

* Machine learning-based urgency estimation
* Dynamic risk scoring
* Waiting-time deterioration
* Priority queue scheduling
* Emergency room capacity management
* Real-time frontend updates
* Cloud deployment

The system continuously updates patient priority rather than assigning a permanent position in the queue.

---

# ⚙️ System Workflow

```text
                     PATIENT ARRIVAL
                           │
                           ▼
                  FEATURE ENGINEERING
                           │
                           ▼
                    ML MODEL INFERENCE
                           │
                           ▼
                  BASE RISK ESTIMATION
                           │
                           ▼
                DYNAMIC RISK ADJUSTMENT
                   (WAITING TIME)
                           │
                           ▼
                  PRIORITY MAX-HEAP
                           │
                           ▼
                 LIVE PATIENT QUEUE
                           │
                           ▼
                EMERGENCY ROOM ASSIGNMENT
                           │
                           ▼
                     TREATMENT
                           │
                           ▼
                  AUDIT / EVENT LOG
```

---

# 🧠 How the AI Engine Works

The backend receives patient information including:

* Age
* Arrival mode
* Medical history
* Heart rate
* Respiratory rate
* Blood oxygen saturation (SpO₂)
* Body temperature
* Heart rate trend
* SpO₂ trend

These features are processed and passed to the trained machine learning model.

The model predicts an estimated safe waiting time:

```text
Predicted Safe Time
        ↓
Converted into Base Risk Score
        ↓
Dynamic Risk Score
```

The base risk score is calculated from the model output and then adjusted dynamically as the patient continues waiting.

---

# 📈 Dynamic Patient Prioritization

One of the core features of PatientTriage.ai is that patient priority changes over time.

The system calculates:

```text
Dynamic Risk Score
=
Base Risk Score
+
Waiting Time Deterioration
```

This means that the queue is continuously updated.

Example:

```text
Patient A
Initial Risk: 80
Wait Time: 2 minutes

Patient B
Initial Risk: 70
Wait Time: 15 minutes

↓

Patient B may eventually receive a higher dynamic priority.
```

This prevents the queue from being permanently static.

---

# 🔴 Risk Classification

Patients are categorized dynamically based on their current risk score.

| Risk Score | Priority Level |
| ---------- | -------------- |
| 75+        | 🔴 Critical    |
| 50–74      | 🟠 High        |
| 25–49      | 🟡 Moderate    |
| Below 25   | 🟢 Low         |

Additional red-flag conditions are also evaluated, such as critically low SpO₂ values.

---

# ⚡ Priority Queue Implementation

The backend uses a heap-based priority queue to efficiently manage patients.

Python's `heapq` implements a Min-Heap, so negative scores are used to simulate a Max-Heap.

```python
heapq.heappush(
    patient_queue,
    (-dynamic_score, patient_id)
)
```

Patients with higher urgency are therefore prioritized.

The priority queue is periodically rebuilt as patient risk scores change over time.

---

# 🏥 Emergency Room Capacity Management

The frontend simulates a physical emergency department with limited treatment rooms.

Current implementation:

* 5 Emergency Rooms
* Vacant rooms are displayed as available
* Treated patients are moved from the priority queue into an ER room
* Once all rooms are occupied, intake/treatment capacity is visually restricted
* Patients can be discharged to free ER capacity

Example:

```text
ER 1   🟢 Vacant
ER 2   🔴 Occupied
ER 3   🔴 Occupied
ER 4   🟢 Vacant
ER 5   🔴 Occupied
```

This introduces a capacity constraint into the simulation rather than assuming unlimited treatment resources.

---

# 🚨 System Lockdown Simulation

When all emergency rooms are occupied, the system displays a capacity warning:

```text
🚨 SYSTEM LOCKDOWN
ALL EMERGENCY ROOMS ARE OCCUPIED
```

This demonstrates how treatment capacity can affect patient flow and emergency department congestion.

---

# 📊 Live Dashboard Features

The dashboard displays real-time operational metrics including:

* Total waiting patients
* Critical patients
* High-risk patients
* Ambulance arrivals
* Walk-in arrivals
* Average waiting time
* Total discharged patients
* Intake status
* Live priority queue
* Emergency room occupancy

---

# 🔍 AI Decision Insights

Users can select a patient from the live queue to inspect available decision information.

The dashboard displays:

* Patient ID
* Base AI risk score
* Dynamic risk score
* Risk level
* Predicted safe waiting time
* Red-flag status
* Arrival mode
* Elapsed waiting time

This provides visibility into the values used by the prioritization engine.

---

# 🔄 Real-Time Background Processing

The FastAPI backend runs an asynchronous background task that periodically:

1. Calculates updated waiting time
2. Adjusts patient risk
3. Updates risk classification
4. Rebuilds the priority queue

Conceptually:

```text
Patient enters queue
        ↓
AI calculates base risk
        ↓
Patient waits
        ↓
Risk changes over time
        ↓
Priority queue updates
        ↓
Dashboard refreshes
```

The frontend polls the backend periodically to display the latest queue state.

---

# 🏗️ System Architecture

```text
┌──────────────────────────────┐
│                              │
│       USER / WEB BROWSER     │
│                              │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────┐
│                              │
│        VERCEL FRONTEND       │
│                              │
│ HTML • CSS • JavaScript      │
│                              │
└───────────────┬──────────────┘
                │ HTTPS / REST API
                ▼
┌──────────────────────────────┐
│                              │
│        RAILWAY BACKEND       │
│                              │
│           FastAPI            │
│                              │
└───────────────┬──────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐   ┌──────────────┐
│ ML MODEL     │   │ PRIORITY     │
│              │   │ QUEUE ENGINE │
└──────────────┘   └──────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Fetch API
* Vercel

## Backend

* Python
* FastAPI
* Uvicorn
* AsyncIO
* Railway

## Machine Learning

* Scikit-learn
* Random Forest
* Pandas
* Pickle

## Algorithms and Data Structures

* Max-Heap
* Priority Queue
* Dynamic Queue Reprioritization

---

# 📁 Project Structure

```text
PatientTriage.ai
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html
│   ├── triage_engine.js
│   └── config.js
│
├── model/
│   ├── train_model.py
│   └── triage_model.pkl
│
├── data/
│   └── synthetic_patient_data.csv
│
├── tests/
│   └── surge_tests.py
│
└── README.md
```

---

# 🚀 Running Locally

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

---

## 2. Set Up the Python Environment

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Run the Backend

From the backend directory:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API should now be available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/health
```

---

## 5. Configure the Frontend

Update `frontend/config.js`:

```javascript
window.API_BASE_URL = "http://localhost:8000";
```

For production deployment, replace this with the Railway backend URL.

---

## 6. Run the Frontend

Open `frontend/index.html` using a local development server.

For example:

```bash
npx serve frontend
```

---

# 🔌 API Endpoints

## Add Patient

```text
POST /api/intake
```

Example payload:

```json
{
  "patient_id": "PT-12345",
  "age": 45,
  "arrival_mode": "Walk-In",
  "has_history": true,
  "hr": 95,
  "rr": 18,
  "spo2": 94,
  "temp_c": 37.5,
  "hr_slope": 0.5,
  "spo2_slope": -0.5
}
```

---

## Get Live Queue

```text
GET /api/queue
```

Returns:

* Total waiting patients
* Current patient priority queue
* Intake status
* System flow status

---

## Treat Patient

```text
POST /api/treat/{patient_id}
```

Removes the patient from the active queue and records the treatment event.

---

## Pause / Resume Intake

```text
POST /api/toggle_pause
```

---

## Reset Simulation

```text
POST /api/reset
```

---

## System Health Check

```text
GET /api/health
```

Returns system information including:

* Server uptime
* Active asynchronous tasks
* Queue size
* Database size
* Model loading status

---

# 🧪 Testing

The project includes simulation-oriented testing to evaluate how the prioritization engine behaves under increased patient inflow.

Testing focuses on scenarios such as:

* Multiple patient arrivals
* Queue growth
* Priority ordering
* Dynamic deterioration
* High patient inflow
* Emergency room capacity constraints

---

# ⚠️ Current Limitations

PatientTriage.ai is currently a prototype and simulation.

Important limitations include:

### 1. Synthetic Training Data

The current machine learning model is trained using synthetic patient data generated for simulation purposes.

The model is **not clinically validated**.

---

### 2. In-Memory State

The current backend stores active patient information in memory.

This means a backend restart can reset active simulation data.

A production system would use persistent infrastructure such as:

```text
FastAPI
   ↓
PostgreSQL
   ↓
Redis
```

---

### 3. Simplified Clinical Features

The prototype uses a limited set of simulated clinical variables.

Real-world deployment would require significantly more clinical information and validation.

---

### 4. Not a Medical Device

The system must not be used for:

* Medical diagnosis
* Real-world patient treatment
* Clinical decision-making
* Hospital deployment without appropriate validation and regulatory approval

---

# 🔮 Future Improvements

Planned directions for future development include:

* [ ] Real clinical dataset integration
* [ ] Clinical validation with domain experts
* [ ] Feature-level explainability using SHAP
* [ ] PostgreSQL persistent storage
* [ ] Redis-based distributed priority queue
* [ ] WebSocket-based real-time updates
* [ ] Authentication and role-based access
* [ ] Historical analytics dashboard
* [ ] Surge prediction
* [ ] Emergency department capacity forecasting
* [ ] Multi-hospital deployment architecture

---

# 🎯 Key Innovation

The core idea behind PatientTriage.ai is that:

> **Patient urgency should not be treated as static.**

The system combines initial AI-assisted risk estimation with continuous waiting-time deterioration and dynamic priority queue updates.

Instead of only asking:

> **Who arrived first?**

PatientTriage.ai asks:

> **Who cannot afford to wait?**

---

# 👥 Team

**TriTects**

Built as a full-stack AI and systems engineering project combining:

* Machine Learning
* Backend Engineering
* Frontend Development
* Data Structures and Algorithms
* Cloud Deployment

---

# 📄 Disclaimer

This project is intended strictly for educational, research, and simulation purposes.

PatientTriage.ai does not provide medical advice and has not been clinically validated. The predictions and prioritization produced by this system must not be used as a substitute for qualified medical professionals or real-world clinical protocols.

---

## ⭐ If you found this project interesting

Consider giving the repository a star!

**PatientTriage.ai — Because urgency can change while waiting.**
