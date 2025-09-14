import sys

src_paths = [
    'c:\\...\\AIMLplus\\',
]

for src_path in src_paths:
    if src_path not in sys.path:
        sys.path.append(src_path)

import unittest
from unittest.mock import MagicMock
from nlu.nlu import NLU
from common.clear_sentence.clear_sentence import ClearSentence
from common.sentence_embedding.sentence_embedder import SentenceEmbedder
from common.frame_extraction.frame_extractor import FrameExtractor

class TestNLU(unittest.TestCase):
    def setUp(self):
        """
        Configura le dipendenze con oggetti mock prima di ogni test.
        """
        # Mock delle dipendenze
        self.mock_clear_sentence = MagicMock(spec=ClearSentence)
        self.mock_sentence_embedder = MagicMock(spec=SentenceEmbedder)
        self.mock_frame_extractor = MagicMock(spec=FrameExtractor)

        # Creazione di un'istanza di NLU con i mock
        self.nlu = NLU(
            clear_sentence=self.mock_clear_sentence,
            sentence_embedder=self.mock_sentence_embedder,
            frame_extractor=self.mock_frame_extractor,
        )

    def test_extraction(self):
        """Testa il metodo extraction della classe NLU."""
        # Input di test
        input_text = "Hello, how are you?"

        # Configura i comportamenti dei mock
        self.mock_clear_sentence.clear.return_value = "hello how are you"
        self.mock_sentence_embedder.encode.return_value = [0.1, 0.2, 0.3]
        self.mock_frame_extractor.get_frame.return_value = (
            "greeting",  # Dialogue Act
            None,       # Placeholder for unused value
            "conversation",  # Topic
            {"slot1": "value1"},  # Frame
        )

        # Esegui il metodo
        preprocessed_input, embedding, dialogue_act, frame = self.nlu.extraction(input_text)

        # Asserzioni sui risultati
        self.assertEqual(preprocessed_input, "hello how are you")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])
        self.assertEqual(dialogue_act, "greeting")
        self.assertEqual(frame, {"slot1": "value1"})

        # Verifica che i mock siano stati chiamati correttamente
        self.mock_clear_sentence.clear.assert_called_once_with(input_text)
        self.mock_sentence_embedder.encode.assert_called_once_with(input_text)
        self.mock_frame_extractor.get_frame.assert_called_once_with(input_text)

if __name__ == "__main__":
    unittest.main()
