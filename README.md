# Take-Home-Compatibility-Task
The goal of this project is to build a mini-pipeline for compatibility scoring based on conversation audio and psychometrics. With the focus being on clear thinking, trade-offs and testable endpoints, the pipeline is relatively simple, with the focus being on justificaiton of choices, and the writeup.


## Live Demo and Usage

Live URL - I made many attempts at getting the live demo link to work for my model, with no success. The available software online which automatically runs github repos was not successful, as my model requires API key inputs. With more time, I would have created an encrypted API key bank to automate this, but this is not feasible in the 48h window. Moreover, including an API key in the code is not possible as GitHub will delete any public repository containing an API key. I also attempted to bypass this issue using an azure Linux virtual machine, but this failed for other reasons. However, my model is easy to run locally using the following steps:

- First download the Github repo: use the following command in windows powershell or linux after navigating (using ls and cd) to the folder you want to download it to:

  - git clone https://github.com/JackClarkson03/Take-Home-Compatibility-Task.git

- Then navigate into the Github repo folder and use the command:

  - pip install -r requirements.txt
 
- Head over to https://platform.openai.com/settings/organization/api-keys and press "Create a new secret key". Copy the API key, and then run the command:

  - $env:OPENAI_API_KEY="this is where you insert your api key" (for powershell)
  - export OPENAI_API_KEY="this is where you insert your api key" (for linux)
 
 - Then run the command:

   - uvicorn src.main:app --reload
  
 - Then copy and paste "http://127.0.0.1:8000/docs" into your browser. This should take you to a website that looks like this:

   -<img width="1441" height="415" alt="image" src="https://github.com/user-attachments/assets/bf9e18c3-905f-4912-bbdf-1e05b9f52ad5" />

- From this site, you press "Try it out" in the /transcribe section and then upload the .wav file and press "Execute" to transcribe the audio, and then "try it out", and replace the "string" text with this transcribed audio in the /summarise and /match sections to get the topic vectors and compatability scores.


You can also run the unit and API tests in the following way:

 - Navigate into the project directory.
 - Run the command (either):

   - $env:OPENAI_API_KEY="this is where you insert your api key" (for powershell)
   - export OPENAI_API_KEY="this is where you insert your api key" (for linux)

  - And then the commands (both):

    - $env:PYTHONPATH = "$env:PYTHONPATH;."
    - pytest
   
  The project is organised into several key Python files within the src/ directory:

  - main.py: This defines the FastAPI application, exposes the API endpoints, and handles user requrests.
  - pipeline.py: This contains the core logic, including functions for audio trascription, calling the LLM, and running VADER sentiment analysis.
  - heuristics.py: This implements the custom compatability scoring logic, and also contains the baseline scoring function. This is where the projects "philosophy" of compatability is translated into code.
  - config.py: This is a centralised file for all model parameters and weights. It allows for easy tuning of the heuristic score based on personal beliefs.
  - schemas.py: This defines the Pydantic data models used for API request and reponse validation.

## Architecture & Design Decisions
This section justifies all architectural decision made about the pipeline. The first few steps are consistent for both the baseline compatibility model, and the matching heuristic model:

- Pre-Transcription (not implemented): While the quality of the provided audio file is high, this will not be generally true. As such, audio preprocessing techniques should generally be implemented to improve the quality of the audio. This includes use digital signal processing to reduce the noise, and cancel echos. Many other compatability metrics can be garnered by pre-transcription techniques, such as acoustic feature analysis and speaker diarisation for more granular analysis.
- Transcription: Audio transcription was done using OpenAI's whisper model (with the base version). The choice of transcription is crucial as the quality of every subsequent audio-based analysis technique implemented by my model was dependent on the quality of the transcript. Whisper is a SOTA model, and allows the transcription to run locally while achieving great results. While the larger Whisper models may perform better, they come at an increased cost, and the small size and high quality of the audio meant that the base model was sufficient. Visual inspection of the transcript verifies that this model does a perfect job of transcribing the file. Alternatives, such as Cloud STT services were ruled out due to increased complexity, and Whisper was chosen over other open-source ASR models due to its reliability and ease of implementation.
- Topic Extraction: Topic extraction was done using multi-task LLM prompting with structured outputs. The system utilises a sophisticated prompt to intruct an LLM to perform three distinct tasks: identify the 5 most important high-level topics or themes, based on these topics, analyse their association with the personality traits (openness, conscientiousness, extraversion, agreeability, neuoticism), and score the engagement of the participants in the conversation (only used for heuristic score). traditional topic modelling techniques are effective at identifying keywords, but fail to capture the abstract high-level themes, which are more closely linked the certain personality traits. By using a single, multi-task prompt, there is a trade-off between cost and complexity. Using a single prompt is significantly faster, but requires careful prompt engineering. The structured output commanded by the LLMs prompt is crucial for the robustness of the project, and consistently performs well. try-except blocks were used as a fallback to mitigate the damage of potential LLM failure. By mapping the topics to a topic vector in the same space as the personality vector, information from the transcript and the personalities of the participants can be seemlessly integrated. Traditional topic modelling techniques were initially used, before being rejected due to a lack of semantic understanding.

The baseline compatibility score fuses the topic and personality information differently to how the matching heuristic model uses this information. The baseline works in the following way:

- The model computes the topic personality vectors (the vectors outputted by the LLM when asked to quantify its association with the topics extracted from the model with respect to each of the personality traits). A weighted sum of each participant personality vector and the topic personality vector is used to create a profile of the participant in the context of the conversation. This is called the participants contextual personality vector (or weighted topic-personality vector). Cosine similarity is then used to measure how comparable the two participants contextual personality vectors are. The full architecture is seen below:
<img width="2427" height="674" alt="baseline_model" src="https://github.com/user-attachments/assets/113a895f-0fdc-45dd-83e8-f10a777d5d72" />

- The main decision require in this pipeline is in the choice of weights in the weighted sum of participant personality vectors and topic personality vectors. For this I chose to weight 75% towards the personality vector, and 25% towards the topic. This is due to the interpretation of the topic personality vector. The "personality traits" of a topic may impact peoples behaviour slightly, but they do not fundamentally change who they are. This weighting seems appropriate to capture the fact that in the 5-dimensional space representing the personality of the topic and participants, the nature of the topic slightly modifies a persons contexual personality, but their overall personality vector must remain the main source of thier nature.
- A problem with the baseline approach is that it makes too many simplifying assumptions. By weighing each participants personality vectors with the topic personaity vector, it creates a pwoerful profile of each participant in the context of the conversation. This is ok, but by then computing the cosine similarity of these two contextual personality vectors to calculate the score, it makes the assumption that similar contextual personality vectors equates to compatibility. In reality, two highly disagreeable and neurotic people will not get along, despite being scored as such.


The Heuristic compatibility score works to resolve this problem, and gives a more nauanced scoring system.

- The heuristic compatibility model implements a more advanced scoring system, based on a more nauanced definition of "compatability", using audio-based (measuring how compatible participants are based on evidence from the audio file) and psychometric-based (measureing how compatbile participants are based on psychometric scores) scoring systems. It is built on a set of specific beliefs about how different personality traits interact in conversatino, and is designed to be explainable, tunable, and aligned with a philosophical view.
- Three audio-based scores are used. Firstly, there is a measure of interest in the conversation based on topics discussed. After the transcrip is embedded into vectors in the same way as the base model, a scaled Euclidean similairty metric is used to score each persons personality vector to the topic vector. This assumes that people with certain personality traits prefer topics that align with these traits. The minimum of these two participants scores is used as a proxy for general interest in the conversation, and thus general compatability of participants. Secondly, the LLM-generated engagement score is used as a compatability score, as more engaged participants are likely to be more compatible. Thirdly, a VADER sentiment analysis model is used to reduce dependence on LLMs.
- The psychometric based scores are used in a custom scoring function that reflect the personal philosophy of the model user. Each individual personality trait can be scored by a different metric and weighed according to different levels of importance. For my particular functions, some are designed to reflect globally high traits, some are designed to reward complementary traits, and some are designed with a preference for similairty. The exact logic is discussed later, and can be see in heuristics.py and config.py.
  <img width="2439" height="1296" alt="heuristic_model" src="https://github.com/user-attachments/assets/7f3be488-67f4-47dd-8a4a-aa88b65f8d2f" />
- There are several weighting parameters in config.py, each with an explainable meaning which allows for the incorporation of beliefs about the importance of different types of compatability. My approach to adjusting the final weights was to more more rigourously define "compatability", write unit tests to check whether the model encorporated these beliefs about compatability, and then tweak the weights and the individual personality trait score functions accordingly until the model passes the test. General "compatability" is hard to define, but in the interest of narrowing the scope, and due to the nature of the conversation data given for this project, I will aim to define casual conversation compatability. That is, the potential for participants to achieve conversational flow, characterised by mutual ease, positive emotional tenor and sustained engagement. With relation to the personality traits provided, this can be summed up as follows.

 - Openness is generally positive for compatibility. A pair where both are high in openness is better than a pair where both are low in openness, but similar openness is better than a mixture. This is because shared curiosity or shared preference for routine leads to smoother conversatins, but high openness allows for an interest in a wider range of topics.
 - Similairty in conscinetiousness is positive, but less critical than other traits. Very high differences can cause friction, but moderate differences are usually compatible for friendly conversation.
 - Complementary is extraversion is positive. Two extreme extraverts are moderately compatible but there may be competition for speaking time. Pairs of introverts are least compatible due to difficulty in initiating and maintaining a conversation. Ambiverts should have neutral compatibility.
 - Agreeableness is a positive trait for casual conversation and is a strong predictor of compatability. Pairs where both are high on agreeableness are most compatable, followed by a mixture of agreeableness.
 - Neuroticism is a negative trait that inversely predicts compatability. Pairs where both are high are least compatabile due to potential for negativity spirals.
 - For trait importance, agreeableness and low neuroticism are the most important traits, followed by complementary extraversion, with openess and conscientiousness ranking least important. This is because a conversations pleasantness and flow are heavily influenced by how cooperative and emotionally stable the participatns are. Having a balance of talking and listening helps maintain engagement, and shared curiosity or conscientiousness are generally not as important.
 - Dynamic audio-based metrics provide important context about the compatability, but the pscyhometrics traits are what forms the foundation of compatability.
 - As the conversation length increases, the importance of the general audio-based metrics should increase. Longer conversations provide more context in determining whether people are compatible, and a high engagement score over a long conversation should outweight initial baseline compatability determined by scores across five personality trait metrics.
 - Across the audio-based metrics, the engagement score is most important, followed by the topic interest. The VADER sentiment ranks lowest, and is more of a backup to prevent fully relying on an LLM for engagement scores. Whether people seem engaged in the conversation is a very strong metric of how compatible they are in casual conversation.



To encode this, I wrote unit tests which measured some of these beliefs (others make more sense to directly set). For different beliefs about compatability, or a different type of compatability being measure, similar unit tests could be deployed to allow these assumptions to be tested. The organisation of my model (unit tests in test_heuristics.py and weights in config.py) helps people encode their personal assumptions about compatability using the method of adjusting the unit tests to reflect their views, and then adjusting the model weights to pass these tests. For example, if the deployment task is to find romantic compatability, consciensiousness might rank higher since organised people will value that more in a partner, but not find it necessary in a casual conversation. Similarly, weights and score functions can be adjusted for your own personal preference if trying to find someone you're compatible with. For my specific assumptions, the final weightings were used to pass the tests:

  - The **individual personality score weightings** are as follows: Openness:0.13, Conscienciousness:0.13, Extraversion:0.17, Agreeableness:0.34, Neuroticism:0.22. The function used to calculate each personality trait score can be found in heuristics.py.
  - The **weighting of audio-based vs psychometric-based** metrics was tuned to favour psychometric 100% during testing of the personality vector to ensure the topic vector does not impact the compatability scores. After the weights of the personality traits were determined, the personality-based metrics were tuned to contribute to to 70% of the overall compatability score to reflect my belief.
  - The **weightings of different audio-based metrics (topic interest, social cue (LLM) bonus, and VADER sentiment bonuse)** were set to 0.45 for the LLM bonus, and 0.1 for the VADER sentiment bonus to reflect the belief in the importance of the engagement of the participants in the conversation in determining compatability.
  - For the **audio transcript length bonus** I chose to add up to a 20% favouring of the audio compatibility score weight, and to have this maximum percentage achieved for transcripts with 1500 or more words. I chose this because it equates to roughly 10 minutes of audio. This means the compatibility scores for longer conversations will be determined more by the metrics relating to the audio transcript, than avergae, and the opposite for shorter conversations, the idea being that you can gauge more about compatibility based on a longer conversation. **add a diagram?


These unit tests could definitely use refining to encode more nauanced beliefs about compatability. My personal view on compatability is bound to be biased, and combining it with the view of others will lead to a much richer understanding of compatability, especially when combined with a more complex model that more adequately encodes these beliefs. To combine my views with others would be to discuss the subject of "what makes people compatible?" in depth, encorporating a wide range of peoples personal experiences to create a balanced perspective. Encorporating research on the topic will also give a more thorough understanding, and a more accurate model.


There are many advantages of the heuristic approach over the baseline. Firstly the trait-specific functions encode that not all traits are created equal. The separate personality trait scores reflects personal philosophies on these traits, stated earlier. It also provides dynamic contextual weightings. The standard topic interest score is boosted by a score dependent on the LLMs interpretation of engagement in the conversation, reflecting the belief that social cues in how people talk are often more important than what they talk about. The conversational length bonus also encodes the belief that the more data we have from a real interaction, the less we should rely on abstract personality profiles. A long, engaging conversation between a theoretically incompatible pair provides strong evidence that they are compatible in practice. Similarly, a long, angry conversation with negative social cues between to theoretically compatible people provides evidence of the opposite. The heuristic model is also far more flexible than the baseline model, due to the config.py file.





## Project Approach
This section details my approach to the project. My goal was to build an end-to-end pipeline which produces a live, testable demo, in an intelligent and thoughtful way. Due to the tight time constraint of the project, and my unfamiliarity with Fast API and Swagger UI, my approach was to first create a working pipeline, and then continue to make improvements. After each model iteration, I tested each section using the interactive demo, and used these results, as well as critical thinking about the way my model processed information, to determine what to adjust for the next iteration of the model. The full, detailed modifications of each iteration are explained below. ** These sections need checking over.

<details>
  <summary> Model Iteration 1.0: Working Iteration using Whisper, keyBERT, LLMs, and a Three-Stage Heuristic Approach</summary>

  My first model had the following carefuly planned structure:

  - Transcription: I used Whisper, as it is highly accurate and easy to implement. Inspection of the transcription verified that this works well.
  - Topic Extraction: I used KeyBERT, a simple and easy to use model for topic extraction.
  - Vectorisation: I used gpt-3.5-turbo-1106 and prompt engineering to automate vectorisation of the extracted topics. Specifically, the LLM was tasked with scoring the set of key words (0-1) on how much it accociates these topics words with each of the personality traits (openness, conscientiousness, extraversion agreeableness, and neuroticism). This creates a vector representation of how the topics are associated with the same feature space as the personality traits.
  - Fusion: These topics vectors and the personality vectors can then combined using a weighted average. I defaulted to weighing the personality vectors as being more important than the topics, giving it a 0.7 weighting.
  - Baseline Compatability: This was computed by first fusing each users personality vectors with the conversation topic vectors, and then calculating a compatibility score between the two using cosine similarity. Each fused vector represents a user's contextual personality profile for that specific conversation. It can be thought of as a profile based mainly on the users core personality, but pulled in the direction of the conversations topics. The baseline compatibility represents how similar the users are within that specific conversational context.
  - Heuristic Compatability: My first attempt at scoring compatability heuristically was based on my initial thoughts about the question, "what is compatability?" My approach considered two types of compatibility (although many parts of these were not implemented on account of heavy computational cost, and increased data requirements):

    - "Birds of a feather flock together" - these are metrics of similarity: people who share common interests, communication styles, personality traints, and potentially even physicological baseline stats, are compatible. My heuristic function considered similarity of this type using three different metrics: Cosine similarity of the personality vectors, the minimum interest between a pair in a topic (computed by taking the minimum cosine similarity between personality and topic vectors), and a measure of how similar users are in certain personality traits (openness and agreeability). I used a weighted sum of these three metrics. Subsconcious mirroring would also come under this class of compatibility. This is the idea that people may begin mirroring speech patterns like pitch, tempo, and laughter style, and may even start to align biometrically when they are around people they are compatible with. This is an interesting psychological fact and would be great to implement, but is outside the scope of the project, as there is only a short time, and a simple bit of data - seeing home someone changed subsconsciously around other people requires their baseline stats to be recorded.
    - "Opposite attract" - these are metrics of a complementory nature, with the idea that pairs of people whose differences lead to a balanced relationship are compatible. This can be differences in communication style, topic interests, and wider personality traits. My first heuristic function incorporated these metrics by scoring participants with opposing extraversion, conscinetiousness, and neuroticism as being more compatible. The idea is that the extravert-intravert, spontaneous-disciplined, and stable-sensitive pairs would balance out each other, leading to more compatibility.


  **Problems** I noticed during my first extraction:

  - My keyBERT topic extraction method was too simple. It choice of topics were very repetative. In fact, it chose topics, "starships mars", "land mars", "flight mars", "mars flight" and "spaceship mars". My second attempt set out to extract higher-level topics from the audio conversation.
  - On reflection, I noticed my heuristic method was very flawed. Firstly, there are multiple metrics benefiting having th same similar personality traits, which muddies the interpretation of the weights. Secondly, and most importantly, there is not indication of generally preferable character traits. While someone with a high neuroticism score may be prefer someone with a low neuroticism score to act as a stable presence, the opposite it not necessarily true. My second iteration needed to improve this, by taking a more nauanced view of personality traits. The symmetric nature of my initial heuristic model means that a pair who are both highly agreeable were equally compatible to a pair who are both less agreeable.
  - Another problem with my heuristic approach is its oversimiplified nature. There are some types of compatibility that don't fall into either category. For instance, subconscious patterns like tonal inflection, or general body-language ticks do not all into either. While these types of metrics are outside the scope of this 48h project, they would be interesting to study and include in future compatibility scoring problems.
</details>



<details>
  <summary>Model Iteration 2.0: High-Level LLM Topic Summary, (API-Key-less) Backup Function, Indpendent Personality Trait Heuristic Approach</summary>
  
  The **changes** I made during my second interation were:

  - An attempt to extract more insightful topucs. My first attemmpt was to summarise the text into a shorter paragraph and use keyBERT to extract the topics from that. My logic was that the summarised paragraph itself would be higher-level, allowing keyBERT to more easily extract more subtle topics. I also increased the maximum length of summary topics keyBERT could suggest. This approach did not work: the model produced the summary ['mars end year', 'mars orbit synchronisation', 'mars orbit', 'earth mars orbit', 'hopefully starship mars']. To enable high-level topic analysis, I decide to use gpt-3.5-turbo-1106. This is a far more powerful model and, while that comes with downsides, I was already using it from the topic vecotorisation, so I didn't lose much by editing the prompt from the vectorisation stage to produce both the list of topics, and the corresponding vector. When I used this model, the output was ["Space exploration and colonization", "Risk assessment and mitigation", "Human Survival and civilization", "Technological advancement and limitations", "Societal and demongraphic challenges"], which much more accurately summarises the topics of the conversation.
  - In light of this new model, which required further use of API keys, I added a mock function which outputted realistic topics and topic vectors which can be used when testing other parts of the code without using any budget on API keys. The proect is very small however, with an estimated cost of under 20 cents total.
  - My heuristic scoring function was also restructured to reduce redundency and differetiate the impact different personality traits have on compatibility. I kept the minimum similarity between personality vector and topic weighting as a metric, but changed the personality trait scores. Similar, and high openness and conscientiousness are rewarded, complementary extraversion scores are rewarded, high agreeablness score are rewarded, and low neuroticism scores are rewarded. A weighted sum of the scores for different personality traits and the topic interest vector were used for the final score. I temporarily weighted agreeableness and neuroticism scores as being the biggest determining factors of compatibility (thinking that these contribute the most to general "compatibility"), but I later took a more thoughtful look at compatibility and reweighted according to my beliefs. It's worth mentioning that my measure of "compatibility" is quite vauge. The scores for different combinations of personality traits will depend greatly on the deployment goal. If we are measure compatibility between friends, business partners, or romantic partners, the weights and functions associated with each personality trait will differ drastically.


There were still **problems** with my second model iteration:

- Using only LLM-extracted topic vectors to include information from the audio file is misleading. Lots of information prevelant in the conversation is not captured by the topic summaries, such as the conversational and social cues. For instance, the tone of a conversation topic may not be fully captured. "Human survival and civilisation" could have been talked about from an engaged, interested perspective, or a dull, uninterested one. This would impact the neuroticism score given to topic vector. My third model will attemp to rectify that by including a topic-based metric representing the engagement of participants in the conversation. There were a couple of potential methods I considered. One was to incorporate the social cues into the topic vector itself, i.e. how open/conscientious/... do the people in the conversation sound, making the topic vector richer in information about the conversation itself, not just the topic. The approach I ended up using was to ask the LLM to also return a score (0.0 - 1.0) quantifying the engagement of participants in the conversation. The idea is that the topic-based compatibility should be impacted by how engaged the participants are in the converation, not just how closely they match to the topics being talked about. I ended up deciding on this method, as it will maintain explainability, as there will be separate scores for the engagement of users in the conversation based on the social cues found in the conversation, and the engagement based on the topics discussed.
- Another problem in the model is the use of cosine similarity between personality vectors and topic vectors. As cosine similarity is a measure of the angle, not the distance, vectors (0.1,...,0.1) and (0.9,...,0.9) produce the same score. This is terribly misleading, as they represent opposing topics. For that reason, cosine similarity was replaced by a scaled euclidean similairty measure. This was something I noticed when testing the distribution of the different personality scores. Another problem I noticed during this is highlighted below:
- <img width="1147" height="638" alt="image" src="https://github.com/user-attachments/assets/99e6bb67-8598-46ae-96e2-e1ca4e4d3220" /> These histograms were plotted by running 1000 random pairing of personality vectors, and then calculating the scores for each personality trait and the topic interest, and overall score. As is clear in the image, the agreeable and neurotisicm scores are using a penalty that overpenalises bad compatibility. This was fixed by reducing the weight of the penalty from 0.5 to 0.25. Furthermore, there is clearly a thin peak regarding the topic interest vector. This is caused because I take the minimum interest score in the conversation. However, I feel this is important to use instead of average because people are not compatible if one person dominates the conversation with a topic only they are interested in. My third model includes linear scaling on this topic interest score to fix this narrow distribution.
  
</details>



<details>
  <summary>Model Iteration 3.0: Participant Engagement Scores</summary>

  As discussed in the "problems" section of my model 2 iteration, using a measure of engagment in the conversation is useful to understand how compatible the two participants are. When the two participants are thoroughly engaged in the conversation, this is a sign they are compatible. With more time for the project, participant engaement could be derived directly from the audio file in order to gauge the participants vocal reflections of their interest. The topic vector approach to participant interest is usful because it gives separate interest scores for each participant, with the interest score being recorded as the minimum of these two to ensure a high interest score means both participants are interested in the conversation. A similar thing could be done from the audio file with speech diarisation.

  I identified a couple of remaining **problems** of the model

  - Firstly, the code needed to be made more robust, and explainable, as this is the main emphasis of the project outlined by the task overview. This extends to my choice of weights, which have seemed arbitrary to this point. Once other problems in the model had been ironed out, my approach was to spend some time considering what I really mean by "compatible", then to design some unit tests which reflect this definition, and to tweak the weights of the model until the results fit my belief.
  - The use of a single LLM sentiment analysis model could also be improved to give a more rounded and robust metric of conversational engagement.

</details>




<details>
  <summary>Model Interation 4.0: Enhanced Explainability, Additional Sentiment Analysis, and Unit Tests</summary>

The Fourth iteration added a few small, but important changes to improve the overall quality of the code and ease of implementation. No major changes were added, but the quality of life when running the code has greatly improved, which is equally as important as changing the actual model.

- First, it added enhanced heuristic explainability and robustness, outputting the full score breakdown when testing compatibility.
- Secondly, configuration management was added for ease of weight adjustment and improved control.
- Thirdly, a second source of sentiment analysis was added in the form of VaderSentiment, an easy-to-use library which is used to analyse the engagement of participants from the given transcript. This was done to reduce the dependency on the LLM-quantified engagement source, making this more robust, sa discussed in the "problem" section of model iteration 3.0.
- Finally, a series of API and heuristic score tests were added. This will make the final re-wieghting of importance of different personality traits easier to do. I added single unit tests for compatibility of different personality traits, and overall comptability tests. The final re-weighting of importance will involve tweaking the weights in config.py, and then run the unit tests and check whether they pass.

</details>

<details>
  <summary>Model Iteration 5.0: Dynamic Psychometric-vs.-Audio Length of Transcript Weightings</summary>

  Model iteration 5.0 added a more dynamic and tunable approach to the weighting of psychometric-based compatibility, and audio-based compatibility. My heuristic method has two main metrics of compatability, which are averaged together using a weighted sum. These two approaches are psychometric-based (i.e. how do the two participants personality vectors indicate compatibility?), and audio-based (i.e. how does information from the audio transcript and a participants personality vector indicate compatibility?). Previous iterations of the model set a fixed weighting of 80% in favour of the psychometric-based approach, and 20% in favour of the topic-based approach. This seemed flawed to me: transcripts from a long conversation should be taken as a more meaningful representation of people compatibility compared to shorter ones. These long conversations have more information available, and should be weighted as such. My solution was to implement a piecewise linear curve to the weighint function. This curve calculates the bonus to the audio-based compatibility score based on the word count of the transcript.

  While problems in my heuristic approach still remain, many of them are outside the scope of what is feasible in 48h. In order to produce a well documented, and clear project, I have opted to discuss these further improvements I would make in "Model Limitations & Trade-offs", and "Future Steps". I considered implementing speech diarisation, but came to the conclusion that robustly implementing this would take up most of my remaining time, leaving little room to document my approach and fully explain the architecture of models.
</details>

<details>
  <summary>Model Iteration 6.0: Final Weight Tuning (via Human Backpropagation)</summary>

  This is the final update made to my model. It used a logically sound and thorough process to tune the weights of the model in absence of the data-driven methods traditional ML would use. First, my philosophical evaluation of "compatability" was more rigourously defined. Secondly the unit tests were modified to reflect these beliefs. Finally, the model weights were tweaked until the model passed all unit tests.
</details>



## Model Limitations & Trade-offs
** Achknowlegde the pragmatic shortcuts and inherent constraints of the current design. Show self awareness and strong engineering sense. Acknoweledge the subjective heuristic approach: I traded a more objective black box model for a fully tansparent, explainable and tunable expert system. This was a choice to meet project requirements. LLM reliability: project hinges on since API call. Tradeoff is performance and cost efficiency, avoiding complexity and chained API calls. mitigated using try-except. Current implementation runs entire pipelin wthin a single requrest: not suitable for high traffic. Design choice for simplicity and rapid devleopment appropriate for 48h task. Focus was not on scalable production-grade infrastructure.

## Future Steps
** propose concrete technical improvements. Speaker diarisation for individual engagement scores far more powerful. Use empirical data for heuristics, refactor pipeline.








The future work on this proejct would involve taking a step back and looking at the deployment goals and thinking about what makes the most sense to predict, and what infromation we could feasibly gain access to.
