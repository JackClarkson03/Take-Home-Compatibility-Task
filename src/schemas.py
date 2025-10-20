

# Import Libraries
from pydantic import BaseModel
from typing import List, Optional


# Input Models
class TranscriptInput(BaseModel):
    """The JSON body for /summaries and /macth"""
    text: str


# Output Models
class TranscriptOutput(BaseModel):
    transcript: str

class TopicsOutput(BaseModel):
    topics: List[str]

class ScoreInterpretation(BaseModel):
    """A single score and its meaning"""
    score: float
    interpretation: str

class HeuristicBreakdown(BaseModel):
    """The detailed breakdown of the heuristic score"""
    match_score: float
    explanation: str

class MatchOutput(BaseModel):
    """The final output of the /match endpoint"""
    baseline_score: ScoreInterpretation
    heuristic_score: HeuristicBreakdown