# python -m unittest discover -s nlu/frame_extraction/tests -p "test_*.py"

import sys
src_path = 'c:\\...\\AIMLplus\\common\\frame_extraction'
if src_path not in sys.path:
    sys.path.append(src_path)

#for p in sys.path:
    #print(p)

import unittest
from frame_extractor import FrameExtractor
from frame_parser import FrameParser
from common.frame_extraction.t5_frame_extractor_handler import T5FrameExtractorHandler
import os

class TestFrameExtraction(unittest.TestCase):
    def test_slot_parser(self):
        output_text = "'VIP': 'no', 'Dialogue_act': 'Ta:setQuestion', 'Topic': 'FSA', 'Subtopic': 'Automata', 'explanation_type': 'Example explanation', 'slot_names': ['alphabet', 'input'], 'slot_values': [['0','1'], '110']"
        result = FrameParser.parse_output(output_text)
        self.assertEqual(result['VIP'], 'no')
        self.assertEqual(result['Dialogue_act'], 'Ta:setQuestion')
        self.assertEqual(result['Topic'], 'FSA')
        self.assertEqual(result['Subtopic'], 'Automata')
        self.assertEqual(result['explanation_type'], 'Example explanation')
        self.assertEqual(result['slot_names'], ['alphabet', 'input'])
        self.assertEqual(result['slot_values'], [['0','1'], '110'])

    def test_get_frame(self):
        model_path = f'models\\Flan-T5-Base-Frame-Extractor'

         # Verifica se il file/directory del modello esiste
        if not os.path.exists(os.path.abspath(model_path)):      
            self.fail(f"Il modello non è stato trovato nel percorso specificato: {model_path}")
        else:
            model_handler = T5FrameExtractorHandler(model_path, 'google/flan-t5-base')
            frame_extractor = FrameExtractor(model_handler)
            text = "esiste una transizione che va da q1 a q2?"
            dialogue_act, vip, topic, frame = frame_extractor.get_frame(text)
            self.assertIsNotNone(dialogue_act)
            self.assertIsNotNone(vip)
            self.assertIsNotNone(topic)
            self.assertIsNotNone(frame)

if __name__ == "__main__":
    unittest.main()