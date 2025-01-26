import re
from collections import Counter
import os

# Load the dataset and create word frequency Counter
dataset_path = os.path.join(os.path.dirname(__file__), 'Dataset_Spelling.csv')
file = open(dataset_path).read()

# Tokenize words
def words(text):
    return re.findall(r'\w+', text.lower())

WORDS = Counter(words(file))

def P(word, N=sum(WORDS.values())):
    return WORDS[word] / N if word in WORDS else 0

def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    insertion = [L + c + R for L, R in splits for c in letters]
    deletion = [L + R[1:] for L, R in splits if R]
    substitution = [L + c + R[1:] for L, R in splits if R for c in letters]
    transpose = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    return set(insertion + deletion + substitution + transpose)

def edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

def known(words):
    return set(w for w in words if w in WORDS)

def correction(word):
    candidates = known([word]) or known(edits1(word)) or known(edits2(word)) or [word]
    return max(candidates, key=P)

def sentence_corrector(sentence):
    sentence = sentence.lower()
    tokens = sentence.split()
    corrected_sentence = []
    for token in tokens:
        corrected_token = correction(token)
        corrected_sentence.append(corrected_token)
    return " ".join(corrected_sentence)
