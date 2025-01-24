import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import tqdm
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder
from transformers import DistilBertModel, DistilBertTokenizer
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
import math
import os
import collections
import pandas as pd
import pyarrow
import dask.dataframe as dd
import numpy as np
from collections import Counter
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


#V1- Team Member 1 and team Member 2 
class FullyConnected(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(FullyConnected, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)

    def forward(self, x):
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)

        x = self.maxpool(x)
        x = x.view(x.size(0), -1)

        x = self.dropout(x)
        x = self.fc2(x)
        return x

class MLPsoftmax(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers):
        super(MLPsoftmax, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(p=0.1)
        self.maxpool = nn.MaxPool1d(kernel_size=2, stride=2)
        pooled_output_size = hidden_size // 2
        self.fc2 = nn.Linear(pooled_output_size, num_layers)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = torch.flatten(x, 1).float()
        x = F.relu(self.fc1(x))
        x = x.unsqueeze(1)

        x = self.maxpool(x)
        x = x.view(x.size(0), -1)

        x = self.dropout(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x
    
class ESCIDataset(Dataset):
    def __init__(self, embeddings, labels):
        self.embeddings = embeddings.values

        print(f'Shape of embeddings: {self.embeddings.shape}')
        self.labels = labels

    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.embeddings[idx], self.labels[idx]
    
def generate_embeddings(texts, model, tokenizer, device):
    batch_size = 128  # Adjust this size
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch.tolist(), return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        embeddings.append(batch_embeddings)

    return np.vstack(embeddings)

def process_partition(partition):
    query_embeddings = generate_embeddings(partition['query'])
    product_title_embeddings = generate_embeddings(partition['product_title'])

    combined = torch.cat((torch.tensor(query_embeddings), torch.tensor(product_title_embeddings)), dim=1).numpy()
    
    print(f'Combined shape: {combined.shape}')  # expecting (n, 1536)

    result = pd.DataFrame(combined, index=partition.index, columns=[f'embedding_{i}' for i in range(combined.shape[1])])

    return result

def train_model(model, train_loader, criterion, optimizer, device, num_epochs=4):
    model.train()  # set model to training mode
    for epoch in range(num_epochs):
        epoch_loss = 0
        for batch_idx, (embeddings, labels) in enumerate(train_loader):
            embeddings, labels = embeddings.to(device), labels.to(device)

            optimizer.zero_grad()  # Clear previous gradients
            outputs = model(embeddings.float())  # Forward pass
            # converting the labels to long in order to 
            labels = labels.long()
            # calculate the loss 
            loss = criterion(outputs, labels) 
            # backpropogation 
            loss.backward() 
            # updating the weights 
            optimizer.step()  
            # add up the loss 
            epoch_loss += loss.item()  

        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss / len(train_loader):.4f}")

def evaluate_model(test_loader, model, device):
    model = model.float()
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device).float()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # evaluate on the f1 score with micro averages
    return f1_score(all_labels, all_preds, average='micro')

def evaluate_and_capture_mismatches(test_loader, model, task_2_test, device):
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.float().to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # convert task_2_test to pandas df if it's a dask df
    if hasattr(task_2_test, 'compute'):
        test_df = task_2_test[['query', 'product_title', 'encoded_labels']].compute()
    else:
        test_df = task_2_test[['query', 'product_title', 'encoded_labels']]

    test_df['predicted_label'] = all_preds
    test_df['true_label'] = all_labels
    
    mismatch_df = test_df[test_df['true_label'] != test_df['predicted_label']]
    
    # added test to make the confusion matrix 
    return test_df, mismatch_df


def train_model_without_loss(model, train_loader, device, num_epochs=4):
    model.train()  # Set model to training mode

    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        
        for batch_idx, (embeddings, labels) in enumerate(train_loader):
            # Move embeddings and labels to the device
            embeddings = embeddings.to(device).float()
            
            # Forward pass to get probabilities
            outputs = model(embeddings)  # Outputs are softmax probabilities
            
            # Store or analyze the probabilities
            # For example, you can print the first batch probabilities
            if batch_idx == 0:
                print(f"Batch {batch_idx + 1} probabilities:\n{outputs[:5]}") 
                
# cross encoder training 
def custom_collate_fn(batch):
    texts = [item["texts"] for item in batch]
    labels = [item["label"] for item in batch]
    return {"texts": texts, "label": labels}


def train_model_cross(model, dataloader, device, optimizer, epochs=3):
    model.model.train()

    for epoch in range(epochs):
        total_loss = 0

        # using tqdm for ipynb progress bars
        for batch in tqdm(dataloader, desc=f"Epoch {epoch + 1}"):
            # batch sentences as list of lists
            sentences = batch["texts"]
            labels = torch.tensor(batch["label"]).to(device)

            inputs = model.tokenizer(
                sentences,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=128  # Adjust based on your data
            ).to(device)

            outputs = model.model(**inputs, labels=labels)
            loss = outputs.loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1} completed. Average Loss: {total_loss / len(dataloader):.4f}")


#Domain Pretraining 

# Create function to tokenize text
def preprocess_function(examples, tokenizer):
    return tokenizer(examples['text'],
                     truncation=True,
                     max_length=512)
    
def group_texts(examples, chunk_size):
    # Concatenate all texts
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    # Compute length of concatenated texts
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    # We drop the last chunk if it's smaller than chunk_size
    total_length = (total_length // chunk_size) * chunk_size
    # Split by chunks of max_len
    result = {
        k: [t[i : i + chunk_size] for i in range(0, total_length, chunk_size)]
        for k, t in concatenated_examples.items()
    }
    # Create a new labels column
    result["labels"] = result["input_ids"].copy()
    return result

def compute_metrics(eval_pred):
    # The eval_pred object contains predictions and label_ids (true labels).
    logits, labels = eval_pred.predictions, eval_pred.label_ids
    
    # Compute predictions from logits by selecting the highest scoring label for each sample
    predictions = np.argmax(logits, axis=-1)
    
    # Calculate the evaluation loss
    loss = eval_pred.metrics["eval_loss"]  # Get the evaluation loss
    
    # Compute accuracy and F1 score
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="weighted")  # Weighted F1 score for multi-class
    perplexity = math.exp(loss)  # Compute perplexity from loss
    return {
        "perplexity": perplexity,
        "accuracy": accuracy,
        "f1": f1
    }
    
# Function to filter out duplicates in the final output
def get_unique_replacements(text, top_tokens, tokenizer):
    seen_replacements = set()
    results = []

    for token in top_tokens:
        decoded_token = tokenizer.decode([token]).strip()
        # Check if this replacement has already been used
        if decoded_token not in seen_replacements:
            seen_replacements.add(decoded_token)
            # Replace the mask token and store the result
            result = text.replace(tokenizer.mask_token, decoded_token)
            results.append(result)

    return results
    
# Create a function to generate predictions
def generate_predictions(queries, product_titles, k, batch_size, tokenizer, device, model):
    all_results = []  # This will hold the final results

    # Process each query
    for query in queries:
        query_results = []  # Store results for the current query
        seen_titles = set()  # Track seen product titles

        # Prepare input texts for the current query in batches
        for i in range(0, len(product_titles), batch_size):
            batch_titles = product_titles[i:i + batch_size]
            input_texts = [f"{query} <mask> {title}" for title in batch_titles]
            inputs = tokenizer(input_texts, padding=True, truncation=True, return_tensors='pt')

            # Move inputs to the appropriate device
            inputs = {key: val.to(device) for key, val in inputs.items()}

            # Make sure to use the model in evaluation mode
            model.eval()

            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
            
            # Process each title's predictions for the current batch
            for j in range(len(batch_titles)):
                mask_index = (inputs['input_ids'][j] == tokenizer.mask_token_id).nonzero(as_tuple=True)[0]

                if mask_index.numel() == 0:  # Check if mask token was found
                    print(f"No mask token found for input: {input_texts[j]}")
                    continue  # Skip this input if no mask token was found
                
                mask_logits = logits[j, mask_index.item()]
                
                # Get the top_k predictions
                top_k_indices = torch.topk(mask_logits, k).indices
                predicted_tokens = tokenizer.convert_ids_to_tokens(top_k_indices)

                # Ensure the product title is unique for this query
                product_title = batch_titles[j]
                if product_title not in seen_titles:
                    seen_titles.add(product_title)  # Mark this title as seen
                    query_results.append({
                        'query': query,
                        'product_title': product_title,
                        'predicted_tokens': predicted_tokens,
                        'logits': mask_logits  # Store logits for sorting
                    })
        
        # Sort query results based on the relevance (logits) and limit to top k unique results
        query_results.sort(key=lambda x: x['logits'].max().item(), reverse=True)  # Sort by max logit
        top_k_results = []  # To collect unique results for this query

        for result in query_results:
            if len(top_k_results) < k:  # Limit to k results
                if result['product_title'] not in {r['product_title'] for r in top_k_results}:
                    top_k_results.append(result)

        # Append the unique results for this query to the overall results
        all_results.extend(top_k_results[:k])  # Ensure only top k are taken

    return all_results

def process_text(batch, puncts):
    # batch['text'] is a list of strings, process each string in the list
    processed_texts = [''.join(ch for ch in str(text) if ch not in puncts) for text in batch['text']]
    return {'processed_text': processed_texts}

def tokenize_function(examples, tokenizer):
    result = tokenizer(examples["processed_text"])
    if tokenizer.is_fast:
        result["word_ids"] = [result.word_ids(i) for i in range(len(result["input_ids"]))]
    return result

def whole_word_masking_data_collator(features):
    for feature in features:
        word_ids = feature.pop("word_ids")

        # Create a map between words and corresponding token indices
        mapping = collections.defaultdict(list)
        current_word_index = -1
        current_word = None
        for idx, word_id in enumerate(word_ids):
            if word_id is not None:
                if word_id != current_word:
                    current_word = word_id
                    current_word_index += 1
                mapping[current_word_index].append(idx)

        # Randomly mask words
        mask = np.random.binomial(1, (len(mapping),))
        input_ids = feature["input_ids"]
        labels = feature["labels"]
        new_labels = [-100] * len(labels)
        for word_id in np.where(mask)[0]:
            word_id = word_id.item()
            for idx in mapping[word_id]:
                new_labels[idx] = labels[idx]
                input_ids[idx] = tokenizer.mask_token_id
        feature["labels"] = new_labels

    return default_data_collator(features)

def generate_embeddings_finetuned(texts, device, tokenizer_ft, model_ft):
    batch_size = 64  # Adjust this size
    embeddings = []

    for i in range(0, len(texts), device, batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer_ft(batch.tolist(), return_tensors='pt', padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model_ft(**inputs, output_hidden_states=True)
            # Access the last hidden state using hidden_states[-1]
            last_hidden_state = outputs.hidden_states[-1]

        # Extract the [CLS] token embeddings from the last hidden state
        batch_embeddings = last_hidden_state[:, 0, :].cpu().numpy()
        embeddings.append(batch_embeddings)
        # Clear GPU cache after each batch
        torch.cuda.empty_cache()

    return np.vstack(embeddings)
