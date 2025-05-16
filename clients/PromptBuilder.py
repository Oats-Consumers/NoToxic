import json


class PromptBuilder:
    class LanguageCheckPrompt:
        def build_is_english_prompt(self, text):
            return f"""You're analyzing short in-game chat messages from a Dota 2 match.

Your task: determine whether a message is written in English or not.

- Messages may contain slang, typos, game terms, or symbols like ":)", "??", "b", or "xd".
- Ignore hero names, map calls, or gibberish that appears English-like.
- Do NOT classify short or ambiguous symbols as non-English unless you're certain they belong to another language.
- If you are unsure whether something is another language, assume it is English.
- Many valid English messages are short, chaotic, or emotional — keep that in mind.
- If a message mixes languages, mark it as non-English only if it's mostly non-English.

Examples:
English → "omg techies why"
English → "go mid noob"
English → "gg wp"
English → "lol report"
English → "push bot"
English → "asd fghj"
English → ":)"
English → ":("
English → "b"
English → "Ezi"
English → "?"
English → "x"

Not English → "hola amigo"
Not English → "vamos al mid"
Not English → "el jungla no gankea"
Not English → "por que feed"
Not English → "was machen wir"
Not English → "venite top"
Not English → "io prendo mid"
Not English → "ya nichego ne mogu sdelat"
Not English → "ya picknu carrya"
Not English → "net wardov"

Now evaluate the following message:

Message: "{text}"

Answer with one word only: Yes or No."""

    class LabelDataPrompt:
        def build_label_data_prompt(self, entry):
            previous = "\n  ".join(entry["previous_messages"]) or "None"
            kills = json.dumps(entry.get("killed_before_time", {}), ensure_ascii=False)
            deaths = json.dumps(entry.get("killed_by_before_time", {}), ensure_ascii=False)

            return f"""
You are a language model assisting in the classification of in-game Dota 2 chat messages based on their toxicity.

Each message must be labeled as one of the following:

---

TOXIC  
Use this label if the message includes any of the following:  
- Insults or personal attacks  
- Harassment or repeated antagonism  
- Flaming, excessive blame, passive-aggressive behavior  
- Sarcasm or provocation intended to demoralize, mock, or ridicule  
- Lack of sportsmanship (e.g., "gg end" — telling others to give up, showing defeatist or dismissive attitude toward teammates or opponents)  
- Spamming or repeating phrases, especially in **ALL CAPS**, as it often signals aggression or mocking  
- Sarcasm that is clearly and unmistakably hostile or mocking in tone

Even short or ambiguous messages (like "?", "b", or "xD") should be labeled TOXIC if the surrounding context indicates hostility or provocation.

---

NON-TOXIC  
Use this label if the message is:  
- Neutral, informative, or strategic (e.g., map calls, item timings)  
- Cooperative, supportive, or encouraging  
- Expressive but harmless (e.g., friendly emoticons, inoffensive jokes)  
- Emotional without hostility

---

UNSURE  
Use this label if:
- The message could reasonably be interpreted as either TOXIC or NON-TOXIC depending on player intent or tone  
- Contextual clues are contradictory, limited, or do not clearly support one classification  
- Sarcasm is present but its intent cannot be confidently judged  
- The speaker was previously toxic, but the current message seems unusually positive or praising (raising doubt about sincerity)  
- The evaluating message is unclear, confusing, or does not make sense in context  
- You feel uncertain or conflicted about how to label the message

⚠️ When in doubt, prefer the UNSURE label over an inaccurate classification.

---

Use the full context provided — including game state, hero performance, and recent chat — to make a well-informed judgment.

Below are several examples of labeled chat messages. Use these as a guide to understand what constitutes a TOXIC, NON-TOXIC, or UNSURE label.

Example 1:
- Game Time (MM:SS): 10:50
- Radiant Gold Advantage: -2656 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -1979 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{}}
- Heroes That Killed This Player Before This Message: {{"Tidehunter": 2, "Queen of Pain": 1}}
- Previous Messages From Players (most recent last):
  Tidehunter (Dire): Make sure to follow my instagram @johnwgw
  Tidehunter (Dire): GLHF
- Team of the Player: Radiant
- Player's Hero: Medusa
- Message To Be Assessed: "WD AFK"

Label: NON-TOXIC
Explanation: "WD" likely refers to Witch Doctor. "AFK" means "Away From Keyboard" — a neutral observation. The player is informing others that WD is not playing.


Example 2:
- Game Time (MM:SS): 8:48
- Radiant Gold Advantage: 2760 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 4030 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{}}
- Heroes That Killed This Player Before This Message: {{"Kez": 2, "Invoker": 1}}
- Previous Messages From Players (most recent last):
  Winter Wyvern (Dire): report sven
- Team of the Player: Dire
- Player's Hero: Sven
- Message To Be Assessed: "gg wp"

Label: NON-TOXIC
Explanation: "Good game, well played" is a respectful way to end a match, regardless of the context.

Example 3:
- Game Time (MM:SS): 10:44
- Radiant Gold Advantage: 3294 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 1080 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{}}
- Heroes That Killed This Player Before This Message: {{"Oracle": 1, "Anti-Mage": 1}}
- Previous Messages From Players (most recent last):
  Anti-Mage (Radiant): oops
- Team of the Player: Dire
- Player's Hero: Techies
- Message To Be Assessed: "xD"

Label: NON-TOXIC
Explanation: "xD" is a harmless emoticon. There's no indication of it being used sarcastically in this context.


Example 4:
- Game Time (MM:SS): 47:25
- Radiant Gold Advantage: 7732 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 2325 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Lifestealer": 4, "Treant Protector": 2, "Queen of Pain": 2, "Tidehunter": 3}}        
- Heroes That Killed This Player Before This Message: {{"Tidehunter": 5, "Winter Wyvern": 1, "Lifestealer": 5, "Queen of Pain": 3}}
- Previous Messages From Players (most recent last):
  Tidehunter (Dire): Make sure to follow my instagram @johnwgw
  Tidehunter (Dire): GLHF
  Medusa (Radiant): WD AFK
  Medusa (Radiant): HAHAAH
  Tidehunter (Dire): Doesnt matter you got handled bot
  Vengeful Spirit (Radiant): can we say mid diff ?
  Vengeful Spirit (Radiant): 9-0 vs 1-3
  Medusa (Radiant): HAHA
  Medusa (Radiant): COME ON IN
  Medusa (Radiant): ?
  Tidehunter (Dire): ggwp
  Medusa (Radiant): HAHA
  Queen of Pain (Dire): welp
  Medusa (Radiant): EZZZ MEDUSA
- Team of the Player: Radiant
- Player's Hero: Centaur Warrunner
- Message To Be Assessed: "gg"

Label: NON-TOXIC
Explanation: Despite earlier heated comments, this message alone is a standard way to end a game.


Example 5:
- Game Time (MM:SS): 40:37
- Radiant Gold Advantage: -29793 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -59868 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Vengeful Spirit": 3, "Beastmaster": 4, "Shadow Fiend": 2, "Invoker": 1, "Shadow Shaman": 4}}
- Heroes That Killed This Player Before This Message: {{"Shadow Fiend": 1, "Beastmaster": 6}}
- Previous Messages From Players (most recent last):
  Beastmaster (Radiant): ?
  Beastmaster (Radiant): ))
  Troll Warlord (Dire): ez
  Troll Warlord (Dire): ez win
- Team of the Player: Dire
- Player's Hero: Troll Warlord
- Message To Be Assessed: "EEEEEZZZZZ"

Label: TOXIC
Explanation: This exaggerated form of "EZ" (easy) is used to mock the opponents, especially after winning. It's a form of gloating.


Example 6:
- Game Time (MM:SS): 49:22
- Radiant Gold Advantage: -11254 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -41305 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Phantom Assassin": 2, "Tiny": 2, "Earthshaker": 1, "Ancient Apparition": 2}}
- Heroes That Killed This Player Before This Message: {{"Phantom Assassin": 3, "Dawnbreaker": 1, "Tiny": 1, "Earthshaker": 2}}
- Previous Messages From Players (most recent last):
  Tiny (Dire): EZZ NOOOB  DOGGG
  Tiny (Dire): EZ MID AF NOOOB
  Dawnbreaker (Dire): GG EZ
  Tiny (Dire): FUCKING DOG
  Phantom Assassin (Dire): useless tiny
  Tiny (Dire): EZ MID
  Phantom Assassin (Dire): got carried
  Tiny (Dire): USELES  DOG DISRUPTTT
  Dark Seer (Radiant): HAHAHA useless tiny
- Team of the Player: Radiant
- Player's Hero: Dark Seer
- Message To Be Assessed: "XD"

Label: TOXIC
Explanation: While "XD" is often innocent, here it's used after calling another player useless. It's part of a sarcastic and mocking tone.


Example 7:
- Game Time (MM:SS): 50:59
- Radiant Gold Advantage: 6706 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 7873 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Invoker": 1, "Monkey King": 1}}
- Heroes That Killed This Player Before This Message: {{"Monkey King": 1, "Arc Warden": 5, "Magnus": 4, "Kunkka": 1, "Invoker": 4}}
- Previous Messages From Players (most recent last):
  Tinker (Dire): xd /
  Bristleback (Dire): gg
  Magnus (Radiant): lol
  Invoker (Radiant): bb retard
  Tinker (Dire): x d
  Razor (Dire): nice 1 vs 5
  Magnus (Radiant): nice positioning
  Kez (Dire): bristle soft back is alive
  Kez (Dire): or not
  Razor (Dire): xd
  Monkey King (Radiant): our magnus is a gay
  Magnus (Radiant): so gay i find mks mom hot
  Magnus (Radiant): super gay
  Invoker (Radiant): we will win bc of feeder bb ty
  Tinker (Dire): x d
  Tinker (Dire): really ulting me huh ?
  Magnus (Radiant): ez
  Tinker (Dire): x d
  Razor (Dire): ?
  Magnus (Radiant): CHOO CHOOO
  Magnus (Radiant): wipeddddddddddd
  Windranger (Dire): GG
  Magnus (Radiant): ez game
  Magnus (Radiant): lol
  Windranger (Dire): lit
  Magnus (Radiant): my team is chaotic
  Magnus (Radiant): love it
  Magnus (Radiant): lol
  Kez (Dire): 2/16 hits different
  Razor (Dire): ????????????????????????
  Tinker (Dire): ???
  Magnus (Radiant): LOL
  Tinker (Dire): braindead
  Magnus (Radiant): 2 rax
  Invoker (Radiant): gg
  Magnus (Radiant): nice game
  Windranger (Dire): GG
  Tinker (Dire): FUCKIGN OMEGA EZ
  Bristleback (Dire): gg
  Magnus (Radiant): cumback
  Monkey King (Radiant): men BB so good
  Monkey King (Radiant): We lost cos BB
  Tinker (Dire): EZ MAGNUS
  Tinker (Dire): where u at?
  Magnus (Radiant): looool
  Magnus (Radiant): im here
  Magnus (Radiant): so salty lmao
  Razor (Dire): ez
  Bristleback (Dire): nice tips
  Magnus (Radiant): ez game
  Magnus (Radiant): hahaha
  Tinker (Dire): keep ulting me
  Magnus (Radiant): ty
- Team of the Player: Dire
- Player's Hero: Bristleback
- Message To Be Assessed: "tip early lose late"

Label: TOXIC
Explanation: Refers to in-game tipping (often used mockingly). Here, it's a sarcastic response to being tipped earlier, implying revenge.


Example 8:
- Game Time (MM:SS): 76:07
- Radiant Gold Advantage: 7357 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -3388 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Tidehunter": 1, "Storm Spirit": 1}}
- Heroes That Killed This Player Before This Message: {{"Death Prophet": 2, "Muerta": 2, "Storm Spirit": 4, "Tidehunter": 1}}
- Previous Messages From Players (most recent last):
  Tinker (Dire): almost
  Ursa (Dire): ???
  Queen of Pain (Dire): lol
  Queen of Pain (Dire): storm is keeping you in game for so long
  Tinker (Dire): tip me?
  Tinker (Dire): of all people?
  Tidehunter (Radiant): )
  Queen of Pain (Dire): ty gaben
  Tinker (Dire): you think im the guy to tip?
  Tinker (Dire): :D
  Tinker (Dire): gg ez
  Undying (Dire): gg wp all
- Team of the Player: Dire
- Player's Hero: Tinker
- Message To Be Assessed: "tip me more tide"

Label: TOXIC
Explanation: The player is mocking someone who previously tipped them, with a sarcastic challenge. This is provocation.


Example 9:
- Game Time (MM:SS): 41:59
- Radiant Gold Advantage: -19442 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -35832 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Ancient Apparition": 3, "Ursa": 2, "Tidehunter": 1}}
- Heroes That Killed This Player Before This Message: {{"Invoker": 3, "Ancient Apparition": 1}}
- Previous Messages From Players (most recent last):
  Invoker (Radiant): mid will be ez
  Invoker (Radiant): i call it
  Clockwerk (Dire): k
  Invoker (Radiant): guys i lied why u guys predict
  Invoker (Radiant): u good bro? so tilted lol
  Silencer (Dire): yeah im good
  Invoker (Radiant): auyooo
  Invoker (Radiant): dont get mad guys
  Invoker (Radiant): farm first
  Clockwerk (Dire): INJOKER ALL TALK
- Team of the Player: Dire
- Player's Hero: Clockwerk
- Message To Be Assessed: "NO SKILL"

Label: TOXIC
Explanation: This is a direct insult implying the enemy (Invoker) has no talent. Especially toxic when part of a larger mocking conversation.


Example 10:
- Game Time (MM:SS): 21:23
- Radiant Gold Advantage: 15479 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 17926 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Ancient Apparition": 1, "Drow Ranger": 1}}
- Heroes That Killed This Player Before This Message: {{"Shadow Shaman": 1, "Invoker": 1, "Drow Ranger": 2}}
- Previous Messages From Players (most recent last):
  Lion (Dire): gg
  Lion (Dire): come end mid
  Windranger (Dire): nice acc buyer lina on the team XD
- Team of the Player: Dire
- Player's Hero: Lina
- Message To Be Assessed: "0 6 lion"

Label: TOXIC
Explanation: This publicly calls out a teammate's bad stats (0 kills, 6 deaths). It's blaming and shaming behavior.


Example 11:
- Game Time (MM:SS): 38:11
- Radiant Gold Advantage: 4205 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: 3120 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Juggernaut": 2, "Skywrath Mage": 1}}
- Heroes That Killed This Player Before This Message: {{"Juggernaut": 3, "Lina": 2}}
- Previous Messages From Players (most recent last):
  Crystal Maiden (Dire): lol imagine feeding this hard
  Crystal Maiden (Dire): jugg diff honestly
  Crystal Maiden (Dire): our carry is braindead
  Crystal Maiden (Dire): uninstall pls
- Team of the Player: Dire
- Player's Hero: Crystal Maiden
- Message To Be Assessed: "gj team, nice fight"

Label: UNSURE
Explanation: Although the message "gj team, nice fight" appears supportive, it follows a sequence of toxic and mocking messages from the same player. The sudden positive shift raises doubt about sincerity — it may be sarcastic or manipulative. Due to this contradiction and ambiguity, the message is labeled UNSURE.


Example 12:
- Game Time (MM:SS): 27:19
- Radiant Gold Advantage: -8230 (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: -11540 (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {{"Mars": 1, "Zeus": 2}}
- Heroes That Killed This Player Before This Message: {{"Drow Ranger": 2, "Zeus": 1}}
- Previous Messages From Players (most recent last):
  Mars (Radiant): lol ez  
  Zeus (Radiant): keep feeding mid  
  Phantom Assassin (Dire): chill guys focus objectives  
- Team of the Player: Dire
- Player's Hero: Phantom Assassin
- Message To Be Assessed: "GOOD TIMING, BUYBACK, EVERYTHING UNDERCONTORLE, YES THANK YOU"

Label: UNSURE
Explanation: The message appears to be a random or nonsensical sequence of words that does not convey any clear meaning all together. It is not obviously hostile or supportive, and without any recognizable context or intent, it cannot be confidently labeled as TOXIC or NON-TOXIC. This uncertainty makes UNSURE the appropriate label.



The context below describes the state of the match **at the exact moment the message was sent**:

- Game Time (MM:SS): {entry['time_str']}
- Radiant Gold Advantage: {entry['radiant_gold_adv']} (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: {entry['radiant_xp_adv']} (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {kills}
- Heroes That Killed This Player Before This Message: {deaths}
- Previous Messages From Players (most recent last):
  {previous}
- Team of the Player: {entry['team']}
- Player's Hero: {entry['hero_name']}
- Message To Be Assessed: "{entry['msg']}"

Classify the message based on the context above. Respond with a single word: TOXIC, NON-TOXIC or UNSURE.
""".strip()
