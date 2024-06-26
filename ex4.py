# ###################################################
# # Exercise 4 - Natural Language Processing 67658  #
# ###################################################

import numpy as np
import plotly.express as px
import plotly.io as pio

# subset of categories that we will use
category_dict = {'comp.graphics': 'computer graphics',
                 'rec.sport.baseball': 'baseball',
                 'sci.electronics': 'science, electronics',
                 'talk.politics.guns': 'politics, guns'
                 }


def get_data(categories=None, portion=1.):
    """
    Get data for given categories and portion
    :param portion: portion of the data to use
    :return:
    """
    # get data
    from sklearn.datasets import fetch_20newsgroups
    data_train = fetch_20newsgroups(categories=categories, subset='train', remove=('headers', 'footers', 'quotes'),
                                    random_state=21)
    data_test = fetch_20newsgroups(categories=categories, subset='test', remove=('headers', 'footers', 'quotes'),
                                   random_state=21)

    # train
    train_len = int(portion * len(data_train.data))
    x_train = np.array(data_train.data[:train_len])
    y_train = data_train.target[:train_len]
    # remove empty entries
    non_empty = x_train != ""
    x_train, y_train = x_train[non_empty].tolist(), y_train[non_empty].tolist()

    # test
    x_test = np.array(data_test.data)
    y_test = data_test.target
    non_empty = np.array(x_test) != ""
    x_test, y_test = x_test[non_empty].tolist(), y_test[non_empty].tolist()
    return x_train, y_train, x_test, y_test


# Q1
def linear_classification(portion=1.):
    """
    Perform linear classification
    :param portion: portion of the data to use
    :return: classification accuracy
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    tf = TfidfVectorizer(stop_words='english', max_features=1000)
    x_train, y_train, x_test, y_test = get_data(categories=category_dict.keys(), portion=portion)

    # Add your code here
    logistic_regression = LogisticRegression().fit(tf.fit_transform(x_train), y_train)
    logistic_regression_acc = accuracy_score(y_test, logistic_regression.predict(tf.transform(x_test)))
    return logistic_regression_acc


# Q2
def transformer_classification(portion=1.):
    """
    Transformer fine-tuning.
    :param portion: portion of the data to use
    :return: classification accuracy
    """
    import torch

    class Dataset(torch.utils.data.Dataset):
        """
        Dataset object
        """

        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    from datasets import load_metric
    metric = load_metric("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return metric.compute(predictions=predictions, references=labels)

    from transformers import Trainer, TrainingArguments
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained('distilroberta-base', cache_dir=None)
    model = AutoModelForSequenceClassification.from_pretrained('distilroberta-base',
                                                               cache_dir=None,
                                                               num_labels=len(category_dict),
                                                               problem_type="single_label_classification")

    x_train, y_train, x_test, y_test = get_data(categories=category_dict.keys(), portion=portion)
    training_args = TrainingArguments(output_dir="./Finetuning_results",
                                      learning_rate=2e-5,
                                      per_device_train_batch_size=16,
                                      per_device_eval_batch_size=16,
                                      num_train_epochs=3,
                                      evaluation_strategy="epoch",
                                      logging_strategy="epoch", )
    train_dataset = Dataset(tokenizer(x_train, padding=True, truncation=True), y_train)
    test_dataset = Dataset(tokenizer(x_test, padding=True, truncation=True), y_test)
    trainer = Trainer(model=model, args=training_args,
                      train_dataset=train_dataset, eval_dataset=test_dataset,
                      compute_metrics=compute_metrics, )
    trainer.train()
    return trainer.evaluate()

# Q3
def zeroshot_classification(portion=1.):
    """
    Perform zero-shot classification
    :param portion: portion of the data to use
    :return: classification accuracy
    """
    from transformers import pipeline
    from sklearn.metrics import accuracy_score
    import torch
    x_train, y_train, x_test, y_test = get_data(categories=category_dict.keys(), portion=portion)
    clf = pipeline("zero-shot-classification", model='cross-encoder/nli-MiniLM2-L6-H768',
                   device=torch.device('cuda:0' if torch.cuda.is_available() else "cpu"))
    candidate_labels = list(category_dict.values())
    results = clf(x_test, candidate_labels)
    acc = accuracy_score(y_test, [candidate_labels.index(res['labels'][0]) for res in results])
    return acc

def plot(graph_title, accuracy_res):
    portions = [0.1, 0.5, 1]
    fig = px.line(x=portions, y=accuracy_res, title=graph_title)
    fig.update_layout(xaxis_title="portion", yaxis_title="accuracy",
                      xaxis=dict(tickvals=list(portions), tickmode='array'))
    pio.write_image(fig, f'{graph_title}.png')
    fig.show()

if __name__ == "__main__":
    portions = [0.1, 0.5, 1.]

    # Q1
    print("Logistic regression results:")
    linear_acc = []
    for p in portions:
        print(f"Portion: {p}")
        accuracy = linear_classification(p)
        linear_acc.append(accuracy)
        print(accuracy)
    plot(f"Logistic regression accuracy", linear_acc)

    # Q2
    print("\nFinetuning results:")
    transformer_acc = []
    for p in portions:
        print(f"Portion: {p}")
        accuracy = transformer_classification(portion=p)
        transformer_acc.append(accuracy['eval_accuracy'])
        print(accuracy)
    plot(f"Finetuning accuracy", transformer_acc)

    # Q3
    print("\nZero-shot result:")
    print(zeroshot_classification())