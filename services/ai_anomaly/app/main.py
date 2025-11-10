from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
import numpy as np

app = FastAPI(title="AI-SOC Anomaly", version="0.1.0")

# simple, stateless model (for demo). In production, persist and retrain per tenant/entity.
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
trained = False

class TrainRequest(BaseModel):
    samples: list[list[float]]

class ScoreRequest(BaseModel):
    samples: list[list[float]]

@app.post("/train")
def train(req: TrainRequest):
    global model, trained
    X = np.array(req.samples, dtype=float)
    model.fit(X)
    trained = True
    return {"status": "ok", "n": len(X)}

@app.post("/score")
def score(req: ScoreRequest):
    if not trained:
        return {"error": "model not trained"}
    X = np.array(req.samples, dtype=float)
    scores = model.decision_function(X).tolist()
    labels = model.predict(X).tolist()  # -1 anomaly, 1 normal
    return {"scores": scores, "labels": labels}
