import unittest
from somali_spelling_correction import SomaliSpellingCorrector

class TestSomaliSpellingCorrector(unittest.TestCase):
    def setUp(self):
        self.corrector = SomaliSpellingCorrector()

    def test_single_word(self):
        self.assertEqual(self.corrector.correction('shaliy'), 'shalay')
        self.assertEqual(self.corrector.correction('wxaan'), 'waxaan')

    def test_sentence(self):
        sentence = 'shaliy waxaan aady suuqa bkaaraha'
        corrected = 'shalay waxaan aaday suuqa bakaaraha'
        self.assertEqual(self.corrector.sentence_corrector(sentence), corrected)

if __name__ == "__main__":
    unittest.main()
