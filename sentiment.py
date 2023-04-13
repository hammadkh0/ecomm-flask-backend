import asyncio
from itertools import chain
import json
import torch
from transformers import (
    BertModel,
    BertTokenizer,
)
from torch import nn
import math
from concurrent.futures import as_completed

PRE_TRAINED_MODEL_NAME = "bert-base-cased"


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


def init_config():
    class_names = ["negative", "positive"]
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

    model = SentimentPredictor(len(class_names))
    model = model.to(device)

    model.load_state_dict(
        torch.load(
            "./models/best_model_state.bin",
            map_location=torch.device("cpu"),
        ))
    return tokenizer, model, class_names, device


def get_sentiment(reviews):

    split_val = math.floor(len(reviews) / 5)
    negative_reviews = []
    split_reviews = []
    tasks = []
    # e.g 40 reviews, split_val = 5, split_reviews = [[0:8], [9:16], [17:24],[25:32], [33:40]]

    tokenizer, model, class_names, device = init_config()
    for i in range(0, len(reviews), split_val):
        split_reviews.append(reviews[i:i + split_val])

    #write split_reviews to a json file
    # with open('./data-dump/split_reviews.json', 'w') as f:
    #     json.dump(split_reviews, f)

    # ----------------------------------- METHOD 1 ----------------------------
    for review in reviews:
        negative_review = calculate(review, tokenizer, model, class_names,
                                    device)
        if (negative_review is not None):
            negative_reviews.append(negative_review)
    return negative_reviews

    # ----------------------------------- METHOD 2 ----------------------------
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     results = executor.map(calculate, split_reviews, [tokenizer] * 5,
    #                            [model] * 5, [class_names] * 5, [device] * 5)
    #     negative_reviews = negative_reviews + list(chain(*results))

    # ----------------------------------- METHOD 3 ----------------------------
    # for chunk in split_reviews:
    #     task = asyncio.create_task(await asyncio.gather(*[
    #         calculate(review, tokenizer, model, class_names, device)
    #         for review in chunk
    #     ]))
    #     tasks.append(task)

    # # Wait for all tasks to complete and gather the results
    # results = []
    # for task in tasks:
    #     results.extend(await task)

    # negative_reviews = negative_reviews + list(chain(*results))
    # return negative_reviews

    # ----------------------------------- METHOD 4 (works) ----------------------------
    # results = {}
    # for i, batch in enumerate(split_reviews):
    #     tokenizer, model, class_names, device = init_config()

    #     results[i] = asyncio.create_task(
    #         process_review_batch(batch, tokenizer, model, class_names, device))
    # for i, result in results.items():
    #     results[i] = await result
    # final_results = []
    # for i in range(len(split_reviews)):
    #     final_results.extend(results[i])
    # return final_results

    # ----------------------------------- METHOD 5 ----------------------------
    # results = {}
    # for i, batch in enumerate(split_reviews):
    #     results[i] = asyncio.create_task(
    #         process_review_batch(batch, tokenizer, model, class_names, device))
    # results = await asyncio.gather(*results.values())
    # final_results = []
    # for i in range(len(split_reviews)):
    #     final_results.extend(
    #         [r for r in await asyncio.gather(results[i]) if r])
    # return final_results


# async def process_review_batch(reviews, tokenizer, model, class_names, device):
#     tasks = []
#     for review in reviews:
#         task = asyncio.create_task(
#             calculate(review, tokenizer, model, class_names, device))
#         tasks.append(task)
#     results = await asyncio.gather(*tasks)
#     return [r for r in results if r]


def calculate(review, tokenizer, model, class_names, device):
    nrs = []

    print("Review Id: " + str(review["id"]))
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
        # nrs.append(review)
        return review
    else:
        return None
    # return nrs
