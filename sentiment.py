import torch
from transformers import (
    BertModel,
    BertTokenizer,
)
from torch import nn

class_names = ["negative", "positive"]
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
PRE_TRAINED_MODEL_NAME = "bert-base-cased"
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
max_length = 1000


class SentimentPredictor(nn.Module):

    def __init__(self, n_classes):
        super(SentimentPredictor, self).__init__()
        self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME,
                                              return_dict=False)
        self.drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(input_ids=input_ids,
                                     attention_mask=attention_mask)
        output = self.drop(pooled_output)
        return self.out(output)


model = SentimentPredictor(len(class_names))
model = model.to(device)

model.load_state_dict(
    torch.load(
        "./best_model_state.bin",
        map_location=torch.device("cpu"),
    ))


def get_sentiment(reviews):
    negative_reviews = []
    for review in reviews:
        review_txt = review["body"]

        encoded_review = tokenizer.encode_plus(
            review_txt,
            max_length=350,
            add_special_tokens=True,
            return_token_type_ids=False,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
        )

        input_ids = encoded_review["input_ids"].to(device)
        attention_mask = encoded_review["attention_mask"].to(device)

        output = model(input_ids, attention_mask)
        _, prediction = torch.max(output, dim=1)

        print(f"Sentiment  : {class_names[prediction]}")
        if (class_names[prediction] == "negative"):
            negative_reviews.append(review)
    return negative_reviews
