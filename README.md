# Take-Home-Compatibility-Task
Quantifying compatibility between users from audio files.

## Project Approach
My goal for this project is to build an end-to-end pipeline which produces a live, testable demo, in an intelligent and thoughtful way. Due to the tight time constraints of the project, I will first create a working pipeline, and then continue making improvements. 

During the first pass through the project, I planned, and then successfully implemented the following techniques:
- Transcription: I used Whisper, since it is highly accurate and easy to implement. Inspection of the transcription verifies this works well.
- Topic Extraction: I used KeyBERT because it is simple, and easy to use. I noticed the repetative nature of some of the key words it chose.
- Vectorisation: I used gpt-3.5-turbo-1106 and prompt engineering to automate vectorisation of the extracted topic words. Specifically, the LLM was tasked with scoring the set of key words (0-1) on how much it accociates these topics words with each of the personality traits (openness, conscientiousness, extraversion agreeableness, and neuroticism). This creates a vector representation of how the topics are associated with the personality traits.
- Fusion: These topics vectors and the personality vectors can then combined using a weighted average. I defaulted to weighing the personality vectors as being more important than the topics, giving it a 0.7 weighting.
- Baseline Compatability: This was computed by first fusing each users personality vectors with the conversation topic vectors, and then calculating a compatibility score between the two using cosine similarity. Each fused vector represents a user's contextual personality profile for that specific conversation. It can be thought of as a profile based mainly on the users core personality, but pulled in the direction of the conversations topics. The baseline compatibility represents how similar the users are within that specific conversational context.

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
- Create edge case personalities which we expect to get along really well or really poorly and test the results





The future work on this proejct would involve taking a step back and looking at the deployment goals and thinking about what makes the most sense to predict, and what infromation we could feasibly gain access to.
