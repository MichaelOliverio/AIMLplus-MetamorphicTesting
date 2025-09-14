import sys
src_path = 'c:\\...\\AIMLplus\\aiml_parser'
if src_path not in sys.path:
    sys.path.append(src_path)

src_path = 'c:\\...\\AIMLplus\\common\\sentence_embedding'
if src_path not in sys.path:
    sys.path.append(src_path)

import unittest
from parser import AIMLParser
import os

class TestAIMLParser(unittest.TestCase):
    def test_load_from_aiml(self):
        """Test per caricare un file AIML e verificare il contenuto delle categorie"""
        # check if the file exists
        parser = AIMLParser() 
        test_file = "NoVAAIMLInterpreter\\aiml_parser\\tests\\example.aiml"
        if not os.path.exists(os.path.abspath(test_file)):     
            self.fail(f"Il modello non è stato trovato nel percorso specificato: {test_file}")

        parser.load_from_aiml(test_file)
        
        # Verifica che due categorie siano state caricate
        self.assertEqual(len(parser.categories), 32)

        # Verifica il primo oggetto categoria
        category = parser.categories[0]

        self.assertEqual(category.pattern, "* LANGUAGE *")
        self.assertEqual(category.input, "language accepted automaton")
        #self.assertEqual(category.template, "The language accepted by this automaton is made of zero or more words formed by a sequence of a triple of 1s followed by a pair of 0s")
        self.assertEqual(category.dialogue_acts_list, ['Ta:request'])
        self.assertEqual(category.frame, {'subtopic': 'alphabet'})

    def test_load_from_folder(self):
        """Test per caricare una cartella di file AIML e verificare il contenuto delle categorie"""
        # check if the folder exists
        parser = AIMLParser()
        test_folder = "NoVAAIMLInterpreter\\aiml_parser\\tests\\examples"
        if not os.path.exists(os.path.abspath(test_folder)):     
            self.fail(f"La cartella non è stata trovata nel percorso specificato: {test_folder}")

        parser.load_from_folder(test_folder)
        
        # Verifica che due categorie siano state caricate
        self.assertEqual(len(parser.categories), 33)        

if __name__ == "__main__":
    unittest.main()
