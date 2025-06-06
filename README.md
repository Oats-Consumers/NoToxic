# Toxicity Ward

A concise overview of our work on detecting toxic language in Dota 2 chat.

## Data
- **Source**: Pulled in-game chat messages (text, player, hero, timestamp, match ID) from the OpenDota API.
- **Filtering**: Ran a Gemma 3 (27B) classifier to keep only English lines.
- **Labeling**:  
  1. Prompted the OpenAI API (ChatGPT‐style) to pre‐label “TOXIC” vs. “NON‐TOXIC.”  
  2. Manually reviewed ~20 % of those labels to correct edge cases.
- **Final Split**: 10 000 messages (5 400 TOXIC, 4 600 NON‐TOXIC).

## Models
- **RoBERTa base (cased)**  
  - **Baseline** (single‐message): F1 ≈ 0.78 (no context).  
  - **Contextual Version**: Included previous messages in the input, gold/exp advantages of the team, heroes of the players, time when message was send, who send the message and the message itself. 
  - **Results (test split)**:  
    - Precision (Toxic): 0.84  
    - Recall (Toxic): 0.855
    - **F1-score: 0.85**

## 📝 Presentation
For detailed methodology, sample prompts, hyperparameters, metrics breakdown, and plots, please refer to our full slide deck:
[View the Presentation](https://docs.google.com/presentation/d/1i_apdbjdXuyAdbNkS0eOnOCtx8_fs4z/edit?usp=sharing&ouid=110563569340235059001&rtpof=true&sd=true)
