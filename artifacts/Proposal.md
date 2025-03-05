# Toxic Chat Detector for Dota 2

## Idea

Develop a machine learning-based tool to automatically detect toxic messages in **Dota 2** game chats. The tool will analyze chat messages in real-time and classify them as toxic or non-toxic based on context and linguistic patterns. This would help automate the moderation process, reducing the reliance on manual player reports.

## Problem

Currently, detecting toxic behavior in **Dota 2** chats is primarily a **manual process**, relying on player reports. This approach is slow, inconsistent, and prone to bias. Many offensive messages go unreported, and some reports may be false positives due to frustration rather than actual toxicity. Additionally, context matters: some words may be toxic in some cases but harmless in others.

## Product Results

- **Automated Toxicity Detection**: Classifies chat messages as toxic or non-toxic using a trained ML model.
- **Context-aware Analysis**: Considers game events (kills, Roshan, runes, etc.) to detect patterns of toxicity. A big amount of toxic messages occurs right after some event in Dota, since it is a very dynamic game, this is expected.
- **Real-time Processing**: Flags messages during matches for immediate detection. *(Depends on OpenDota API and Dota 2 in general).*
- **Multi-language Support**: Detects toxicity across different languages commonly used in the game.
- **Integration with Dota 2 Data**: Uses **OpenDota API** or replay logs to correlate chat toxicity with in-game events.
- **Customizable Moderation Rules**: Allows defining thresholds for different toxicity levels.
- **Analytics Dashboard**: Displays statistics on detected toxic messages and trends over time.

## Learning Value

- **Machine Learning & NLP**: Implementation of text classification models, potentially using **BERT, RoBERTa, or LSTMs** for sentiment and toxicity analysis.
