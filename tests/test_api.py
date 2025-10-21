# --- API Endpoint Tests --- #

from fastapi.testclient import TestClient
from src.main import app
import os

client = TestClient(app)

def test_transcribe_endpoint():
    audio_path = "tests/dummy_audio.wav"
    if not os.path.exists(audio_path):
        raise FileNotFoundError("Please create dummy audio file.")
    with open(audio_path, "rb") as f:
        response = client.post("/transcribe", files={"file": ("dummy_audio.wav", f, "audio/wav")})
        assert response.status_code == 200
        assert "transcript" in response.json()




def test_summarise_endpoint():
    response = client.post("/summarise", json={"text": "This is a test transcript."})
    assert response.status_code == 200
    assert "topics" in response.json()
    assert isinstance(response.json()["topics"], list)




def test_match_endpoint():
    response = client.post("/match", json={"text": "This is a test transcript about space and mars."})
    assert response.status_code == 200
    assert "baseline_score" in response.json()
    assert "heuristic_score" in response.json()
    assert "score" in response.json()["baseline_score"]
    assert "match_score" in response.json()["heuristic_score"]