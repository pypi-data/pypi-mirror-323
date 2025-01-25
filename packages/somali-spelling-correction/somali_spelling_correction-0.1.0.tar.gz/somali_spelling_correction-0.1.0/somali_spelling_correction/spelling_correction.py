import re
from collections import Counter
from pathlib import Path

class SomaliSpellingCorrector:
    def __init__(self, dataset_path=None):
        # Set default dataset path
        if dataset_path is None:
            dataset_path = Path(__file__).parent / "data/dataset.csv"
        self.dataset = Path(dataset_path).read_text(encoding="utf-8")
        self.WORDS = Counter(self.words(self.dataset))
    
    @staticmethod
    def words(text):
        return re.findall(r'\w+', text.lower())

    def P(self, word, N=None):
        # Probability of `word`
        if N is None:
            N = sum(self.WORDS.values())
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
        candidates = (
            self.known([word]) or 
            self.known(self.edits1(word)) or 
            self.known(self.edits2(word)) or 
            [word]
        )
        return max(candidates, key=self.P)

    def sentence_corrector(self, sentence):
        tokens = sentence.lower().split()
        corrected_sentence = [self.correction(token) for token in tokens]
        return " ".join(corrected_sentence)
