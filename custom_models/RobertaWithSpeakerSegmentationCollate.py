from transformers import PreTrainedTokenizer
import torch

class RobertaWithSpeakerSegmentationCollate:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_length=512):
        """
        tokenizer_name: name or path for pretrained tokenizer
        """
        self.tokenizer = tokenizer

        # Initialize special tokens → assuming they were added beforehand
        self.section_token_ids = {
            "GAME_STATE": self.tokenizer.convert_tokens_to_ids("[GAME_STATE]"),
            "KILLED": self.tokenizer.convert_tokens_to_ids("[KILLED]"),
            "KILLED_BY": self.tokenizer.convert_tokens_to_ids("[KILLED_BY]"),
            "MSG": self.tokenizer.convert_tokens_to_ids("[MSG]"),
            "PREVIOUS": self.tokenizer.convert_tokens_to_ids("[PREVIOUS]")
        }
        self.slash_token_id = self.tokenizer.convert_tokens_to_ids("|")
        self.separator_token_id = self.tokenizer.convert_tokens_to_ids("<SEP>")
        self.max_length = max_length
        self.cls_token_id = self.tokenizer.convert_tokens_to_ids("[CLS]")


    def __mark_tokens_constant_section(self, section_starts_idx, section_end_idx, section_name, meta_dict, ids, player_ids, team_ids, msg_context_ids):
        if section_starts_idx is None:
            return
        if section_end_idx is None:
            section_end_idx = len(ids)
        meta = meta_dict[section_name]
        for i in range(section_starts_idx + 1, section_end_idx):
            if ids[i] == self.separator_token_id or ids[i] == self.cls_token_id:  # <SEP> no need to mark it specially
                continue
            player_ids[i] = meta["hero_id"]
            team_ids[i] = meta["team"]
            msg_context_ids[i] = meta["is_context"]

    def __mark_tokens_variable_section(self, section_starts_idx, section_end_idx, section_name, meta_dict, ids, player_ids, team_ids, msg_context_ids):
        if section_starts_idx is None:
            return
        if section_end_idx is None:
            section_end_idx = len(ids)
        metas = meta_dict[section_name]
        pos = 0
        for i in range(section_starts_idx + 1, section_end_idx):
            if ids[i] == self.separator_token_id or ids[i] == self.cls_token_id:  # <SEP> no need to mark it specially
                continue
            if ids[i] == self.slash_token_id:  # here we detect | so we need to change the position in metas
                pos += 1
                continue
            if pos < len(metas):
                meta = metas[pos]
                player_ids[i] = meta["hero_id"]
                team_ids[i] = meta["team"]
                msg_context_ids[i] = meta["is_context"]


    def __call__(self, batch):
        """
        batch: list of dicts → each dict: {'input_text': str, 'label': int, 'metadata': dict}
        """

        input_texts = [item["input_text"] for item in batch]
        labels = torch.tensor([item["label"] for item in batch], dtype=torch.long)
        metadata_list = [item["metadata"] for item in batch]

        encoding = self.tokenizer(
            input_texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        input_ids = encoding["input_ids"]
        attention_mask = encoding["attention_mask"]

        batch_player_ids = []
        batch_team_ids = []
        batch_msg_context_ids = []

        for batch_idx in range(len(batch)):
            ids = input_ids[batch_idx].tolist()

            player_ids = [0] * len(ids)
            team_ids = [0] * len(ids)
            msg_context_ids = [0] * len(ids)

            section_starts = {}
            for name, token_id in self.section_token_ids.items():
                try:
                    section_starts[name] = ids.index(token_id)
                except ValueError:
                    continue  # section not found

            # → fill GAME_STATE tokens

            gs_start = section_starts.get("GAME_STATE")
            killed_start = section_starts.get("KILLED")

            self.__mark_tokens_constant_section(gs_start, killed_start, "game_state", metadata_list[batch_idx], ids, player_ids, team_ids, msg_context_ids)

            # → fill KILLED tokens

            killed_by_start = section_starts.get("KILLED_BY")

            self.__mark_tokens_variable_section(killed_start, killed_by_start, "killed", metadata_list[batch_idx], ids, player_ids, team_ids, msg_context_ids)

            # → fill KILLED_BY tokens
            msg_start = section_starts.get("MSG")

            self.__mark_tokens_variable_section(killed_by_start, msg_start, "killed_by", metadata_list[batch_idx], ids, player_ids, team_ids, msg_context_ids)

            # → fill MSG tokens
            prev_start = section_starts.get("PREVIOUS")

            self.__mark_tokens_constant_section(msg_start, prev_start, "message", metadata_list[batch_idx], ids, player_ids, team_ids, msg_context_ids)

            # → fill PREVIOUS tokens

            self.__mark_tokens_variable_section(prev_start, len(ids), "previous_messages", metadata_list[batch_idx], ids, player_ids, team_ids, msg_context_ids)

            batch_player_ids.append(player_ids)
            batch_team_ids.append(team_ids)
            batch_msg_context_ids.append(msg_context_ids)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
            "player_ids": torch.tensor(batch_player_ids),
            "team_ids": torch.tensor(batch_team_ids),
            "message_context_ids": torch.tensor(batch_msg_context_ids),
        }
