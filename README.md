# Toxicity Ward

A concise overview of our work on detecting toxic language in Dota 2 chat.

## Data
- **Source**: Pulled in-game chat messages (text, player, hero, timestamp, match ID) from the OpenDota API.
- **Filtering**: Ran a Gemma 3 (27B) classifier to keep only English lines.
- **Labeling**:  
  1. Prompted the OpenAI API (ChatGPT‐style) to pre‐label “TOXIC” vs. “NON‐TOXIC.”  
  2. Manually reviewed ~20 % of those labels to correct edge cases.
- **Final Split**: 10 000 messages (5 400 TOXIC, 4 600 NON‐TOXIC), with an 80 / 10 / 10 train/val/test split. We also retained up to two preceding lines as context for each target message.

## Models
- **RoBERTa base (cased)**  
  - **Baseline** (single‐message): F1 ≈ 0.87 (no context).  
  - **Contextual Version**: Included two previous messages in the input; applied label smoothing (ϵ = 0.1), dynamic token masking, and stratified batch sampling.  
  - **Results (test split)**:  
    - Precision (Toxic): 0.93  
    - Recall (Toxic): 0.91  
    - **F1-score: 0.92**

## 📝 Presentation
For detailed methodology, sample prompts, hyperparameters, metrics breakdown, and plots, please refer to our full slide deck:
[View the Presentation](https://docs.google.com/presentation/d/1i_apdbjdXuyAdbNkS0eOnOCtx8_fs4Jz/edit?usp=sharing&ouid=110563569340235059001&rtpof=true&sd=true)
