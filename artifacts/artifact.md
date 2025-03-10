# Dota 2 Toxicity Detection Artifacts

## 1. Research Papers
We have gathered multiple research papers that analyze toxicity in gaming and explore different AI-based methods for detecting it.

### Goal
- Gain insights into state-of-the-art methods for toxicity detection in gaming.
- Identify key challenges and approaches used in existing research.

### Outcome
- Summarized findings on the most effective ML techniques.
- A structured plan for selecting an appropriate method for our own model.
- A list of potential experts or authors we can reach out to for guidance.

### Next Steps
1. Read and summarize key findings from each paper.
2. Extract and compare methodologies used in different studies.
3. Identify and contact at least one expert in the field to discuss potential approaches.

Sources:
- [Toxicity Detection in Online Games - arXiv](https://arxiv.org/pdf/2403.15458v1)
- [A Review of Toxicity Detection in Online Gaming - QUT](https://eprints.qut.edu.au/227450/1/104448192.pdf)
- [Detecting Toxicity in Online Communities - arXiv](http://arxiv.org/pdf/2310.18330)

---

## 2. Datasets
We have identified some datasets from gaming environments, but we need to review them to assess the level of contextual information they provide.

### Goal
- Find a dataset that includes in-game context and toxicity labels.
- Assess the dataset quality, structure, and usability for training our ML model.

### Outcome
- A comparative analysis of dataset features.
- A decision on which dataset(s) to use for training.
- A plan for augmenting the dataset if necessary (e.g., adding contextual tags).

### Next Steps
1. Download and inspect dataset formats.
2. Check for missing or inconsistent data.
3. Identify contextual variables that are available and those that need to be derived.

Sources:
- [Dota 2 Toxic Chat Data - Papers with Code](https://paperswithcode.com/dataset/dota-2-toxic-chat-data)
- [CONDA: Context-Aware Dataset for Toxicity Detection - GitHub](https://github.com/usydnlp/CONDA)

---

## 3. Dota 2 API Investigation & Cost Analysis
We have found the Dota 2 API and need to review its functionality and relevance for our project.

### Goal
- Determine whether the API can provide in-game context data alongside chat logs.
- Assess whether real-time or post-match data extraction is feasible.
- Evaluate the cost implications of making API requests and storing match data.

### Outcome
- A documented API review including key endpoints.
- A decision on whether we will integrate API data into our dataset.
- A prototype script to fetch and process Dota 2 match chat logs.
- A cost estimation based on API request frequency and data storage.

### Next Steps
1. Review API documentation and test available endpoints.
2. Investigate how to retrieve match data programmatically (match ID, player usernames, chat logs).
3. Write a sample script to retrieve and process chat logs.
4. Evaluate how API data aligns with dataset needs.
5. Cost Calculation: Estimate API costs based on request frequency and data storage needs.

Sources:
- [Dota 2 API - OpenDota Docs](https://docs.opendota.com/#section/Introduction)

---

## 4. Usage Scenarios

### Goal
- Define different real-world usage scenarios for the system.
- Illustrate how individual users, organizations, and gaming platforms could interact with the toxicity detection API.

### Scenarios

#### 1. Individual Use (Player Analysis)
- Context: A player wants to analyze their past Dota 2 matches for fun or self-reflection.
- Steps:
  1. The user accesses the API via a web app or script.
  2. They provide their username and select a match ID.
  3. The API retrieves the chat log from OpenDota.
  4. The system analyzes the chat using the trained toxicity model.
  5. The user receives a toxicity breakdown of the chat.
  6. They share the results (as a meme or for self-improvement).

- Alternative Flow:
  - If the match data is unavailable, the user is notified with an error message.

- Outcome:
  - The player gets an objective toxicity score and insights into chat behavior.

---
#### 2. Organization Use (Player Evaluation)
- Context: Esports teams, coaches, or tournament organizers use the tool to evaluate player behavior.
- Steps:
  1. The organization submits a list of players and match IDs for assessment.
  2. The API retrieves and processes chat logs for multiple matches.
  3. The system generates a toxicity report for each player.
  4. The results are stored in a database or exported as a report.
  5. Coaches or analysts use the reports to make informed decisions.

- Alternative Flow:
  - If a player has insufficient matches in the dataset, an alternative dataset is suggested.

- Outcome:
  - Organizations can assess player behavior objectively before recruitment or tournament participation.

---

#### 3. Integration with Dota 2 (Long-term Vision)
- Context: The ultimate goal is for this system to be integrated into Dota 2 itself.
- Steps:
  1. During or after a match, the game automatically submits chat logs to the API.
  2. The system evaluates the messages in real-time.
  3. Players receive immediate feedback on toxicity levels.
  4. If necessary, reports are generated for moderation or player improvement.
  
- Alternative Flow:
  - Players can choose to receive feedback privately or as a report after each match.

- Outcome:
  - The tool contributes to a healthier gaming environment with automated toxicity detection.

---

## Final Additions
- We will try to contact an expert in the field of toxicity detection in gaming to get guidance on the best approach(Rodion Khvorostov is happy to help us).
- We will create a structured learning path, listing topics to study (e.g., NLP models for toxicity detection, context-aware classification techniques).
- By the next deadline, we aim to have a list of best practices and steps to follow in developing our model.

---