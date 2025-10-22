# Write-up
(264 words)

## Model Evaluation (Reasonings and Trade-offs)
With no clear deployment goal, I set out to philosophically define a metric of compatibility, and then build an explainable, heuristic model founded on this philosophy. My goal was to score compatibility from the perspective of casual conversation, where stable personality traits act as the foundation, an in-the-moment social cues like engagement in the conversation prove compatibility. Without a labelled dataset, traditional evaluation metrics were not possible. My approach was to encode my philosophical beliefs about casual conversation compatibility into a series of unit tests. The models correctness was evaluated by its ability to pass these tests. My final heuristic model prioritised interpretability, tunability, and philosophical alignment over the improved predictive power of an unexplainable, data-driven model. This was a deliberate choice to meet the task's emphasis on clear thinking.


## Next Steps
To produce a better compatibility model, I would first take a step back and establish a firm deployment goal - are we predicting long-term romantic compatibility, professional cohesion, or casual friendship? The exact prediction goal would be established using expert opinion and empirical research grounded in the deployment goal. With an explicit prediction goal, the next step would be to understand how to best evaluate these predictions in a way that is meaningful for the project. The final, advanced model would be trained on a richer dataset, incorporating not just psychometrics, but also potentially biometric data, and a bank of conversations for each participant. This holistic, data-driven approach would allow the model to move beyond theoretical compatibility, and provide truly predictive, deployment-oriented analysis. The project README outlines some more immediate, concrete technical next steps.

