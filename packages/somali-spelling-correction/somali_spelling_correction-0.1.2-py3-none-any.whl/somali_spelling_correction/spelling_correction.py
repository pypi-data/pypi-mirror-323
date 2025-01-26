import re
from collections import Counter
from pathlib import Path
import importlib.resources

class SomaliSpellingCorrector:
    def __init__(self):
        # Dynamically load the dataset
        with importlib.resources.open_text('somali_spelling_correction.data', 'dataset.csv') as file:
            self.dataset = file.read()

        # Tokenize and create the word frequency Counter
        self.WORDS = Counter(self.words(self.dataset))

    def words(self, text):
        return re.findall(r'\w+', text.lower())

    def P(self, word, N=None):
        N = N or sum(self.WORDS.values())
        return self.WORDS[word] / N if word in self.WORDS else 0

    def edits1(self, word):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        insertion = [L + c + R for L, R in splits for c in letters]
        deletion = [L + R[1:] for L, R in splits if R]
        substitution = [L + c + R[1:] for L, R in splits if R for c in letters]
        transpose = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        return set(insertion + deletion + substitution + transpose)

    def edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def known(self, words):
        return set(w for w in words if w in self.WORDS)

    def correction(self, word):
        candidates = self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word]
        return max(candidates, key=self.P)

    def sentence_corrector(self, sentence):
        tokens = sentence.lower().split()
        corrected_sentence = [self.correction(token) for token in tokens]
        return " ".join(corrected_sentence)
