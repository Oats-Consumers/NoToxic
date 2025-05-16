from transformers import PreTrainedModel, RobertaTokenizer
from transformers.models.roberta.configuration_roberta import RobertaConfig
from transformers.models.roberta.modeling_roberta import RobertaEmbeddings
import torch
import torch.nn as nn
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers.models.roberta.modeling_roberta import RobertaModel, RobertaEncoder, RobertaPooler
from transformers.modeling_outputs import BaseModelOutputWithPoolingAndCrossAttentions


class RobertaWithSpeakerSegmentationConfig(RobertaConfig):
    def __init__(self,
                 player_ID_vocab_size=147,   # 0=special token + 146 different heroes
                 team_ID_vocab_size=3,      # 0=special token + 2 teams
                 message_context_vocab_size=3,  # 0=special token + 2 tokens (context, not-context)
                 **kwargs):
        super().__init__(**kwargs)
        self.player_ID_vocab_size = player_ID_vocab_size
        self.team_ID_vocab_size = team_ID_vocab_size
        self.message_context_vocab_size = message_context_vocab_size
        self.player_embedding_scale = 0.1  # or nn.Parameter(torch.tensor(0.1))


class RobertaWithSpeakerSegmentationEmbeddings(RobertaEmbeddings):
    def __init__(self, config):
        super().__init__(config)

        self.player_ID_embeddings = nn.Embedding(config.player_ID_vocab_size, config.hidden_size)
        self.team_ID_embeddings = nn.Embedding(config.team_ID_vocab_size, config.hidden_size)
        self.message_context_embeddings = nn.Embedding(config.message_context_vocab_size, config.hidden_size)
        self.player_embedding_scale = config.player_embedding_scale

    def __set_default_if_none(self, attribute_ids, attribute_name, seq_length, input_shape):
        if attribute_ids is not None:
            return attribute_ids
        if not hasattr(self, attribute_name):
            return torch.zeros(input_shape, dtype=torch.long, device=self.position_ids.device)
        buffered_attribute_ids = getattr(self, attribute_name)[:, :seq_length]
        return buffered_attribute_ids.expand(input_shape[0], seq_length)

    def forward(
        self,
        input_ids=None,
        token_type_ids=None,
        position_ids=None,
        player_ids=None,
        team_ids=None,
        message_context_ids=None,
        inputs_embeds=None,
        past_key_values_length=0,
    ):
        if input_ids is not None:
            input_shape = input_ids.size()
        else:
            input_shape = inputs_embeds.size()[:-1]

        seq_length = input_shape[1]

        if position_ids is None:
            position_ids = self.position_ids[:, past_key_values_length: seq_length + past_key_values_length]

        token_type_ids = self.__set_default_if_none(token_type_ids, "token_type_ids", seq_length, input_shape)
        player_ids = self.__set_default_if_none(player_ids, "player_ids", seq_length, input_shape)
        team_ids = self.__set_default_if_none(team_ids, "team_ids", seq_length, input_shape)
        message_context_ids = self.__set_default_if_none(message_context_ids, "message_context_ids", seq_length, input_shape)

        if inputs_embeds is None:
            inputs_embeds = self.word_embeddings(input_ids)

        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        player_embeddings = self.player_ID_embeddings(player_ids) * self.player_embedding_scale
        team_embeddings = self.team_ID_embeddings(team_ids)
        message_context_embeddings = self.message_context_embeddings(message_context_ids)

        embeddings = (inputs_embeds + token_type_embeddings
                      + player_embeddings
                      + team_embeddings
                      + message_context_embeddings
                      )

        if self.position_embedding_type == "absolute":
            position_embeddings = self.position_embeddings(position_ids)
            embeddings += position_embeddings

        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings



class RobertaWithSpeakerSegmentationModel(PreTrainedModel):
    config_class = RobertaWithSpeakerSegmentationConfig
    base_model_prefix = "roberta_with_speaker_segmentation"

    def __init__(self, config, add_pooling_layer=True):
        super().__init__(config)

        self.embeddings = RobertaWithSpeakerSegmentationEmbeddings(config)
        self.encoder = RobertaEncoder(config)
        self.pooler = RobertaPooler(config) if add_pooling_layer else None

        self.post_init()

    def __replace_if_none(self, value, replacement):
        return value if value is not None else replacement

    def __set_default_if_none(self, attribute_ids, attribute_name, seq_length, input_shape, device):
        if attribute_ids is not None:
            return attribute_ids
        if not hasattr(self.embeddings, attribute_name):
            return torch.zeros(input_shape, dtype=torch.long, device=device)
        buffered_attribute_ids = getattr(self.embeddings, attribute_name)[:, :seq_length]
        return buffered_attribute_ids.expand(input_shape[0], seq_length)

    def get_input_embeddings(self):
        return self.embeddings.word_embeddings

    def set_input_embeddings(self, new_embeddings):
        self.embeddings.word_embeddings = new_embeddings

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        player_ids=None,
        team_ids=None,
        message_context_ids=None,
        head_mask=None,
        inputs_embeds=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        past_key_values=None,
        use_cache=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = self.__replace_if_none(return_dict, self.config.use_return_dict)
        output_attentions = self.__replace_if_none(output_attentions, self.config.output_attentions)
        output_hidden_states = self.__replace_if_none(output_hidden_states, self.config.output_hidden_states)
        use_cache = self.config.is_decoder and self.__replace_if_none(use_cache, self.config.use_cache)

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")

        batch_size, seq_length = input_shape
        device = input_ids.device if input_ids is not None else inputs_embeds.device

        past_key_values_length = past_key_values[0][0].shape[2] if past_key_values is not None else 0

        if attention_mask is None:
            attention_mask = torch.ones((batch_size, seq_length + past_key_values_length)).to(device)

        token_type_ids = self.__set_default_if_none(token_type_ids, "token_type_ids", seq_length, input_shape, device=device)
        player_ids = self.__set_default_if_none(player_ids, "player_ids", seq_length, input_shape, device=device)
        team_ids = self.__set_default_if_none(team_ids, "team_ids", seq_length, input_shape, device=device)
        message_context_ids = self.__set_default_if_none(message_context_ids, "message_context_ids", seq_length, input_shape, device=device)

        extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape).to(device)

        if self.config.is_decoder and encoder_hidden_states is not None:
            encoder_batch_size, encoder_sequence_length, _ = encoder_hidden_states.size()
            encoder_hidden_shape = (encoder_batch_size, encoder_sequence_length)
            if encoder_attention_mask is None:
                encoder_attention_mask = torch.ones(encoder_hidden_shape, device = device)
            encoder_extended_attention_mask = self.invert_attention_mask(encoder_attention_mask)
        else:
            encoder_extended_attention_mask = None

        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)

        embedding_output = self.embeddings(
            input_ids=input_ids,
            position_ids=position_ids,
            token_type_ids=token_type_ids,
            player_ids=player_ids,
            team_ids=team_ids,
            message_context_ids=message_context_ids,
            inputs_embeds=inputs_embeds,
            past_key_values_length=past_key_values_length,
        )

        encoder_outputs = self.encoder(
            embedding_output,
            attention_mask=extended_attention_mask,
            head_mask=head_mask,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_extended_attention_mask,
            past_key_values=past_key_values,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None

        if not return_dict:
            return (sequence_output, pooled_output) + encoder_outputs[1:]

        return BaseModelOutputWithPoolingAndCrossAttentions(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            past_key_values=encoder_outputs.past_key_values,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
            cross_attentions=encoder_outputs.cross_attentions,
        )



class RobertaWithSpeakerSegmentationForSequenceClassification(PreTrainedModel):
    config_class = RobertaWithSpeakerSegmentationConfig
    base_model_prefix = "roberta_with_speaker"

    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.roberta_with_speaker = RobertaWithSpeakerSegmentationModel(config, add_pooling_layer=True)
        classifier_dropout = config.classifier_dropout if config.classifier_dropout is not None else config.hidden_dropout_prob
        self.dropout = nn.Dropout(classifier_dropout)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        player_ids=None,
        team_ids=None,
        message_context_ids=None,
        head_mask=None,
        inputs_embeds=None,
        labels=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        outputs = self.roberta_with_speaker(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            player_ids=player_ids,
            team_ids=team_ids,
            message_context_ids=message_context_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        # ---------------------------------------
        # last_hidden = outputs.last_hidden_state  # [batch_size, seq_len, hidden_dim]
        # attention_mask = attention_mask.unsqueeze(-1)  # [batch_size, seq_len, 1]
        # masked_hidden = last_hidden * attention_mask  # mask out padding tokens
        # sum_hidden = masked_hidden.sum(dim=1)  # sum over sequence
        # token_counts = attention_mask.sum(dim=1).clamp(min=1e-9)  # avoid divide by 0
        # mean_pooled = sum_hidden / token_counts  # [batch_size, hidden_dim]
        # ---------------------------------------

        # TODO try attention pooling
        # TODO try bert instead

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

