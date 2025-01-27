import sys
import re
import time
import datetime
import os
import numpy as np
import regex as re
from .tokenizer import KinTokenizer

from multiprocessing import Pool, cpu_count



def train_kin_tokenizer(text, vocab_size=276, save=False, tokenizer_path=None, retrain=False):
    """
    Function for training the tokenizer
    params:
        text: the string text that will be used for training the tokenizer
        vocab_size: the final size of the voacabulary for the tokenizer
        save: boolean to indicate if tokenizer has to be saved after training for future use
        tokenizer_path: the path to which the tokenizer will be saved if save is True
    Returns:
        returns tokenizer object after training
    """
    tokenizer = KinTokenizer()
    start_merge_iter = 0
    if retrain:
        tokenizer.load(os.path.join(tokenizer_path, "kin_tokenizer.pkl"))
        start_merge_iter = max(list(tokenizer.vocab.keys()))
    if len(text) < vocab_size or type(text) != str:
        raise ValueError("length of text should be greater or equal to vocab_size, vocab_size should be at least 256 and text should be a string")
    
    if save == True:
        if tokenizer_path is None:
           tokenizer_path = os.path.join("kin_tokenizer", "data")
        
        tokenizer.train(text, vocab_size, start_merge_iter=start_merge_iter, tokenizer_path=tokenizer_path)
        tokenizer.save(tokenizer_path)
    else:
        tokenizer.train(text, vocab_size, start_merge_iter=start_merge_iter)

    return tokenizer


def create_sequences(tokens, seq_len, step=None):
    """
    Function for creating sequences for next word prediction
    params:
        tokens: list of tokens(integers)
        seq_len: the length for each sequence to be created
    returns:
        the list of sequences(list of tokens with length of seq_len)
    """
    tokens_len = len(tokens)
    sources, targets = [], []
    if step is None:
        factor = seq_len / 1024
        step = int((seq_len * 25 / factor) / 3200)
    for i in range(tokens_len):
        sequence = tokens[i: i + seq_len + 1]
        
        if len(sequence) < seq_len + 1:
            break

        source = sequence[:-1]
        target = sequence[-1]

        sources.append(source)
        targets.append(target)

        i = i * step

    return sources, targets



def create_sequences_batch(args):
    """ 
    Helper function to create sequences for a batch of tokens. 
    args:
        is the tuple of (tokens_chunck, seq_len, step)
        in the order listed
    """
    index, tokens, seq_len, step = args
    if step is None:
        factor = seq_len / 1024
        step = int((seq_len * 25 / factor) / 3200)

    sources, targets = [], []
    for i in range(len(tokens)):
        sequence = tokens[i: i + seq_len + 1]
        
        if len(sequence) < seq_len + 1:
            break

        source = sequence[:-1]
        target = sequence[-1]

        sources.append(source)
        targets.append(target)

        i = i * step

    return index, sources, targets


def preprocess_text(text):
    text = re.sub("’", "'", text) # repacle ’ with '
    text = re.sub("‘", "'", text) # repacle ‘ with '
    text = re.sub("“", '"', text) # repacle “ with "
    text = re.sub("”", '"', text) # repacle ” with "

    text = re.sub('â', 'a', text) # replace â with a
    text = re.sub('ê', 'e', text) # replace ê with e
    text = re.sub('î', 'i', text) # replace î with i
    text = re.sub('ô', 'o', text) # replace ô with o
    text = re.sub('û', 'u', text) # replace û with u
    
    
    
    text = re.sub(r'(\n){3,}', '\n\n', text).strip() # Removing whitespace which are not followed by non-white space characters, remove new lines(empty lines)
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])([aeiouAEIOU])+', r'\1\2', text)  # Keep only two consecutive vowels
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])([^A-Za-z])+', r'\1\3', text)  # If there are still two consecutive vowels followed by non-letter remove the second vowel
    text = re.sub(r'([aeiouAEIOU])([aeiouAEIOU])', r'\1 \2', text) # Add a space between two vowels following each other(e.g aa -> a a
    text = re.sub(r'([aeiou])([A-Z])', r'\1 \2', text) # When a small vawel is followed by capital letter, add space between them(e.g uRwanda -> u Rwanda)
    text = re.sub(r'\s([.,!?;:])', r'\1', text) # remove the space before a punctuation mark
    text = re.sub(r'(?<![.,!?;:])([\'\"])\s+', r'\1', text) # remove the space after a single or double quotes when there is no punctuation mark before
    text = text.lower()

    return text


def create_dataset(text_file_path: str, nbr_processes: int, sequence_length: int, destination_dir: str, step_size:int=None):
    """
    Function for creation arrays of sequences you can use for training your language model
    params:
        text: is the filename path which contains the text to be used for creating sequences
        nbr_processes: is the number of processes to run in parallel for multi-cpu machine
        sequence_length: is the number of tokens each sequence will have
        destination_dir: is the location folder/directory where the final sequences created will be saved
        step_size: is the number of tokens to skip/overlap for the next sequence
    """
    training_start_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = time.time()
    total_time = time.time() - start_time

    tokenizer = KinTokenizer() # instantiating the tokenizer
    tokenizer.load() # loading the state for the tokenizer

    if not os.path.exists(text_file_path) or not os.path.isfile(text_file_path):
        raise ValueError("The text file path should be valid like folder/text.txt")
        sys.exit(1)
    
    if not os.path.exists(destination_dir) or not os.path.isdir(destination_dir):
        raise ValueError("The destination folder/directory should be valid and exist")
        sys.exit(1)
    
    if step_size is None:
        step_size = sequence_length // 2
    

    with open(text_file_path, "r",  encoding='UTF-8', errors="ignore") as f:
        text = f.read()
    f.close()
    
    text = preprocess_text(text)

    print("Sample text:\n\n", text[: sequence_length])
    print("\n========================================================================================================================\n")
    print("\nEncoding.........")
    encoded_text = tokenizer.encode(text, nbr_processes=nbr_processes)

    print(f"\nEncoding completed!\nCreating sequences with sequence length of {sequence_length}\n")

    print(f"\n{len(encoded_text)} tokens to be processed\n")
    
    # Preparing arguments for each process
    total_tokens = len(encoded_text)
    total_seqs = total_tokens / sequence_length
    cpu_seqs = total_seqs / nbr_processes
    chunk_size = int(cpu_seqs * sequence_length)

    rem__size = int(((cpu_seqs * sequence_length) - chunk_size) * nbr_processes)

    args = []
    for i in range(nbr_processes):
        start_index = i * chunk_size
        
        if i != (nbr_processes -1):
            end_index = (i + 1) * chunk_size
        else:
            end_index = ((i + 1) * chunk_size)+ rem__size
        args.append((i, encoded_text[start_index: end_index], sequence_length, step_size))

    print(f"\nTotal tokens chunks: {len(args)}\n")
    # Create sequences using multiprocessing
    print(f"Creating sequences with sequence length of {sequence_length}")
    print(f"\nEach process has {chunk_size} tokens to process")
    print(f"Last process has {chunk_size + rem__size} tokens\n")
    with Pool(processes=nbr_processes) as pool:
        results = pool.map(create_sequences_batch, args)
    
    print("\nCreating sequences completed. Going to merge results from different processes")

    # Sort results by index and merge them
    print("\nSorting squences by index before merging")
    sorted_results = sorted(results, key=lambda x: x[0])

    # Combine results from each process
    X, y = [], []
    for _, sources, targets in sorted_results:
        X.extend(sources)
        y.extend(targets)

    print("\nCreating sequences completed!")
    print(f"\n{len(X)} sequences created\n")

    print("\nWriting data into numpy file\n")
    file_path = os.path.join(destination_dir, "sequences.npz")

    np.savez_compressed(file_path, sources=np.array(X), targets=np.array(y))

    print("Writing data completed\n")

    total_time = time.time() - start_time
    training_end_time = datetime.datetime.now(datetime.timezone.utc)

    months, remaining = int(total_time // (3600 * 24 * 30)), total_time % (3600 * 24 * 30)
    days, remaining = int(remaining // (3600 * 24)), remaining % (3600 * 24)
    hours, remaining = int(remaining // 3600), remaining % 3600
    minutes, seconds = int(remaining // 60), int(remaining % 60)

    if months > 0:
        months = f"{months} months "
    else:
        months = ""
    
    if days > 0:
        days = f"{days} days "
    else:
        days = ""
    
    if hours > 0:
        hours = f"{hours} hours "
    else:
        hours = ""
    
    if minutes > 0:
        minutes = f"{minutes} minutes "
    else:
        minutes = ""
    
    if seconds > 0:
        seconds = f"{seconds} seconds"
    else:
        seconds = ""
    
    total_time = f"{months}{days}{hours}{minutes}{seconds}".strip()

    print(f"Sequences creation started on {training_start_time.strftime('%d-%m-%Y %H:%M:%S')} UTC\nSequences Creation ended on {training_end_time.strftime('%d-%m-%Y %H:%M:%S')} UTC\nTook: {total_time}\n\n")






