
# Import Libraries
import uvicorn
import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException

from . import pipeline
from . import heuristics
from . import schemas

app = FastAPI(title="Compatibility AI", description="A 48h speech recognition take-home task.")


# Load User Profiles
try:
    USER_PROFILES = pipeline.load_user_profiles()
    USER_1_VEC = USER_PROFILES["user_1"]["psychometrics"]
    USER_2_VEC = USER_PROFILES["user_2"]["psychometrics"]
except FileNotFoundError:
    print("WARNING: user_profiles.json not found. Using defaults.")
    USER_1_VEC = [0.5, 0.5, 0.5, 0.5, 0.5]
    USER_2_VEC = [0.5, 0.5, 0.5, 0.5, 0.5]


# Transcribe Audio
@app.post("/transcribe", response_model=schemas.TranscriptOutput)
async def transcribe(file: UploadFile = File(...)):
    """
    Uploads an audio file and returns the transcript.
    """
    #temp_path = f"temp_{file.filename}"
    temp_path = os.path.join(pipeline.PROJECT_ROOT, f"temp_{file.filename}")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        transcript_text = pipeline.transcribe_audio(temp_path)
        return {"transcript": transcript_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription Failed: {str(e)}")
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Extract Topics
@app.post("/summarise", response_model=schemas.TopicsOutput)
async def summarise(request: schemas.TranscriptInput):
    """
    Takes a transcript string and returns a list of 5 topics.
    """
    try:
        topics, _, _ = pipeline.get_topics_and_vectors(request.text) # Use get_topics_and_vectors_mock() while the API calls are down
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic extraction failed: {str(e)}")
    

# Match Users
@app.post("/match", response_model=schemas.MatchOutput)
async def match(request: schemas.TranscriptInput):
    """
    Takes a transcript, returns the compatibility scores
    """
    try:

        # Extract topic vectors
        topics, topic_vec, engagement_score = pipeline.get_topics_and_vectors(request.text) # Use get_topics_and_vectors_mock() while the API calls are down
        vader_compound_score = pipeline.get_vader_sentiment(request.text)

        # Fuse vectors
        fused_vec_1 = pipeline.fuse_vectors(USER_1_VEC, topic_vec)
        fused_vec_2 = pipeline.fuse_vectors(USER_2_VEC, topic_vec)

        # Calculate baseline score
        baseline = heuristics.baseline_compatibility_score(fused_vec_1, fused_vec_2)

        # Calculate transcript length
        word_count = len(request.text.split())

        # Calculate heuristic score
        analysis_results = {"topic_vector":topic_vec, "engagement_score": engagement_score, "vader_engagement": vader_compound_score, "word_count": word_count}
        heuristic = pipeline.heuristic_compatibility_score(USER_1_VEC, USER_2_VEC, analysis_results)

        return {"baseline_score": baseline,
                "heuristic_score": heuristic}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")
    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)