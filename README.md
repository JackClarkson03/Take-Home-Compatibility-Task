# Take-Home-Compatibility-Task
Quantifying compatibility between users from audio files.

## Project Approach
My goal for this project is to build an end-to-end pipeline which produces a live, testable demo, in an intelligent and thoughtful way. Due to the tight time constraints of the project, I will first create a working pipeline, and then continue making improvements. After each model iteration, I will test each section on using the interaction demo, and use these results to determine what is included in the next iteration of the model. The full, detailed modifications of each iteration are explained below.

<details>
  <summary> First Model Iteration: Working Iteration using Whispter, keyBERT, LLMs, and Three-Stage Heuristic Approach</summary>
  
During the first pass throguh the d=project, I planned, and successfully implemented the following techniques:
- Transcription: I used Whisper, since it is highly accurate and easy to implement. Inspection of the transcription verifies this works well.
- Topic Extraction: I used KeyBERT because it is simple, and easy to use. I noticed the repetative nature of some of the key words it chose.
- Vectorisation: I used gpt-3.5-turbo-1106 and prompt engineering to automate vectorisation of the extracted topic words. Specifically, the LLM was tasked with scoring the set of key words (0-1) on how much it accociates these topics words with each of the personality   traits (openness, conscientiousness, extraversion agreeableness, and neuroticism). This creates a vector representation of how the topics are associated with the personality traits.
- Fusion: These topics vectors and the personality vectors can then combined using a weighted average. I defaulted to weighing the personality vectors as being more important than the topics, giving it a 0.7 weighting.
- Baseline Compatability: This was computed by first fusing each users personality vectors with the conversation topic vectors, and then calculating a compatibility score between the two using cosine similarity. Each fused vector represents a user's contextual   personality profile for that specific conversation. It can be thought of as a profile based mainly on the users core personality, but pulled in the direction of the conversations topics. The baseline compatibility represents how similar the users are within that specific conversational context.





My first attempt at the heuristic compatibility score is based on my approach at answering the question, "what is compatibility?" My approach was three-pronged, though only two-prongs were implemented due to the heavy computational cost, and increased data requirements for the third. The three types of compatibility I considered were:
  - "Birds of a feather flock together" - these are metrics of similarity. People who share common interests, communication styles, personality traits, and potentially even physicological baseline stats, are compatible. In my first heuristic function, I used three of these types of metrics: Cosine similarity of the personality vectors, the minimum interest between a pair in a topic (computed by taking the minimum cosine similarity between personality and topic vectors), and a measure of how similar users are in certain personality traits (openness and agreeability). I used a weighted sum of these three metrics.
  - "Opposites attract" - these are metrics of complementory nature. Pairs of people whose differences lead to a balanced relationship are compatible. This can be differences in communication style, topic interests, and wider personality traits. In my first heuristic function, I used a weighted sum of how different their specific personality traits are. Specifically, I looked at the difference between their extraversion, conscientiousness, and neuroticism as a positive. The idea is that the extravert-intravert, spontaneous-disciplined, and stable-sensitive pairs would balance out each other, leading to more compatibility.
  - "In sync" - these are matrics of how people subconsciously mirror people they are compatible with. People may begin mirroring speech patterns like pitch, tempo, and laughter style, and may even start to align biometrically when they are around people they are compatible with. Furthermore, other subconcious patterns like tonal inflections, etc. would be interesting to include, but outside the scope of this short project.





Some flaws with my initial heuristic similarity function that I looked to improve included:
  - Repartition: there are multiple metrics of how similar users personality vectors are.
  - No indication of preferable character traits - while someone with a high neuroticism score may be prefer someone with a low neuroticism score to act as a stable presence, the opposite it not necessarily true. I need to flesh-out my reasoning for different personality traits preferring others. People with lower neuroticism may be more compatible with people in general, for example. The current symmetrical nature of my personality trait comparison similarities and differences means a pair who both have high agreeableness are scored equally (on this metric) to pairs with los agreeableness.


  My second pass at the task set out to fix some of the flaws realised in my initial approach:
- Can I improve the topic extraction method? The topics it chose were "starships mars", "land mars", "flight mars", "mars flight" and "spaceship mars". These are all very similar, and not all neccessary.
- Tidy up the "birds of a feather approach" to avoid repartition. Can we validate the choice of weighting?
- Fix the oversimplication of "opposites attract". The assumption that differences are always good is risky, as they sometimes lead to conflict. Similar is true for the "birds of a feather" approach - two people with high neuroticism and low agreeableness should not be scored as highly compatible. Also need to validate the choice of weights for this part of th heuristic scoring.
- Create edge case personalities which we expect to get along really well or really poorly and test the results.
</details>



<details>
  <summary>Second Model Iteration: High-Level LLM Topic Summary, (API-Key-less) Backup Function, Indpendent Personality Trait Heuristic Approach</summary>
  
  The changes I made during my second interation are:
  
  - My first attempt at extracting more insightful topics was to summarise the text into a shorter paragraph and use keyBERT to extract the topics from that. My logic was that the summarised paragraph itself would be higher-level, allowing keyBERT to more easily extract more subtle topics. I also increased the maximum length of summary topics keyBERT could suggest. This approach did not work: the model produced the summary ['mars end year', 'mars orbit synchronisation', 'mars orbit', 'earth mars orbit', 'hopefully starship mars']. To enable high-level topic analysis, I decide to use gpt-3.5-turbo-1106. This is a far more powerful model and, while that comes with downsides, I was already using it from the topic vecotorisation, so I didn't lose much by editing the prompt from the vectorisation stage to produce both the list of topics, and the corresponding vector. When I used this model, the output was ["Space exploration and colonization", "Risk assessment and mitigation", "Human Survival and civilization", "Technological advancement and limitations", "Societal and demongraphic challenges"], which much more accurately summarises the topics of the conversation.
  - In light of this new model, which required further use of API keys, I added a mock function which outputted realistic topics and topic vectors which can be used when testing other parts of the code without using any budget on API keys. The proect is very small though, with an estimated cost of under 20 cents total.
  - My heuristic scoring function was also restructured to reduce redundency and differetiate the impact different personality traits have on compatibility. I kept the minimum similarity between personality vector and topic weighting as a metric, but changed the personality trait scores. Similar, and high openness and conscientiousness are rewarded, complementary extraversion scores are rewarded, high agreeablness score are rewarded, and low neuroticism scores are rewarded. A weighted sum of the scores for different personality traits and the topic interest vector were used for the final score, with agreeableness and neuroticism scores being the biggest determining factors of compatibility. The reason for this is that generally, pairs of strongly disagreeable or neurotic people are less compatible with people. It's worth mentioning that my measure of "compatibility" is quite vauge. The scores for different combinations of personality traits will depend greatly on the deployment goal. If we are measure compatibility between friends, business partners, or romantic partners, the weights and functions associated with each personality trait will differ drastically.


Testing my second iteration model revealed some potential improvements:

- Using only the LLM-extracted topics to create the topic vector could be improved. Lots of information prevenlant in the conversation is not captured by the topic summaries, such as the conversational and social cues. For instance, the neuroticism of a conversation topic may not be fully captured. "Human survival and civilisation" could have been talked about from a positive, optimistic perspective, or a negative one. This would impact the neuroticism score given to topic vector.
- The use of cosine similarity between topic vectors and personality vectors causes misleading results. As cosine similarity is a measure of the angle, not the distance, vectors (0.1,...,0.1) and (0.9,...,0.9) produce the same score. This is terribly misleading, as they represent opposing topics. For that reason, cosine similarity was replaced by a scaled euclidean similairty measure.
- There were problems in the distribution of different scores:
- <img width="1147" height="638" alt="image" src="https://github.com/user-attachments/assets/99e6bb67-8598-46ae-96e2-e1ca4e4d3220" /> I plotted these histograms by running 1000 random pairing of personality vectors, and then calculating the scores for each personality trait and the topic interest, and overall score. As is clear in the image, the agreeable and neurotisicm scores are using a penalty that overpenalises bad compatibility. This was fixed by reducing the weight of the penalty from 0.5 to 0.25. Furthermore, there is clearly a thin peak regarding the topic interest vector. It is caused by the use of minimum interest in the conversation, but I feel this is important to use instead of average because people are not compatible if one person dominates the conversation with a topic only they are interested in. Linear scaling in applied to fix this problem.
- By observing a few small cases of carefull engineered pairs of personality traits, I carefully adjusted the weights of different similarity scores in order to ensure they more closely align with my expectations. This involved slightly turning up the weight of the agreeability and openness scores, and turning down the neuroticism score.



My Third iteration will make the following changes:
- It will attemp to incorporate social cues to better understand the interest of the people in the topics. This could be done by incorporating it into the topic vector itself, meaning the topic vector would have richer information about whether people are compatible based on the actual conversation, not just the topics covered by their conversation. Another option is to add a metric quantifying the engagement of the people in the conversation to the topic_interest score. This is the method I will use because it will maintain explainability, as there will be separate scores for the engagement of users in the conversation based on the social cues found in the conversation, and the engagement based on the topics discussed.
  
</details>










The future work on this proejct would involve taking a step back and looking at the deployment goals and thinking about what makes the most sense to predict, and what infromation we could feasibly gain access to.
