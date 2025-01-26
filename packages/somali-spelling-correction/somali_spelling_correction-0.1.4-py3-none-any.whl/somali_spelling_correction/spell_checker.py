import re
from collections import Counter

# Reading the dataset and creating word frequency Counter
file = open('Dataset_Spelling.csv').read()

# Function to tokenize words
def words(text):
    return re.findall(r'\w+', text.lower())

# Tokenize the dataset and calculate word frequencies
WORDS = Counter(words(file))

# Function to calculate the probability of a word
def P(word, N=sum(WORDS.values())):
    return WORDS[word] / N if word in WORDS else 0

# Function to generate edits that are 1 edit distance away
def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    insertion = [L + c + R for L, R in splits for c in letters]
    deletion = [L + R[1:] for L, R in splits if R]
    substitution = [L + c + R[1:] for L, R in splits if R for c in letters]
    transpose = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    return set(insertion + deletion + substitution + transpose)

# Function to generate edits that are 2 edit distances away
def edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

# Function to filter known words from a list of candidates
def known(words):
    return set(w for w in words if w in WORDS)

# Function to generate the best candidate correction
def correction(word):
    # Prioritize candidates with 1 edit distance, then 2, then the original word
    candidates = known([word]) or known(edits1(word)) or known(edits2(word)) or [word]
    return max(candidates, key=P)

# Function to correct an entire sentence
def sentence_corrector(sentence):
    sentence = sentence.lower()
    tokens = sentence.split()
    corrected_sentence = []
    for token in tokens:
        corrected_token = correction(token)
        corrected_sentence.append(corrected_token)
    return " ".join(corrected_sentence)
