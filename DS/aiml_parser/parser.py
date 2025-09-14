import sys

src_paths = [
    'c:\\...\\AIMLplus\\',
]

for src_path in src_paths:
    if src_path not in sys.path:
        sys.path.append(src_path)

import xml.etree.ElementTree as ET
from aiml_parser.category import Category

class AIMLParser:
    def __init__(self):
        self.categories = []
        self.global_slots = set()

    def load_from_aiml(self, filepath: str) -> None:
        """
        Carica le categorie da un file AIML e le inserisce nella lista delle categorie.
        """
        tree = ET.parse(filepath)
        root = tree.getroot()

        if len(self.categories) == 0:
            category_id = 0
        else:
            category_id = self.categories[-1].id + 1

        # Itera su tutti i nodi <category> dell'AIML
        for category_element in root.findall('category'):
            argument = category_element.get('argument')
            intent = category_element.get('intent')

            # Estrae il template
            template_element = category_element.find('template')
            template = ''.join(template_element.itertext()).strip() if template_element is not None else ""

            # Estrae gli atti dialogici
            dialogue_acts_list = []
            acts_element = category_element.find('acts')
            if acts_element is not None:
                for act in acts_element.findall('act'):
                    dialogue_acts_list.append(act.text)

            # Estrae il frame
            frame = {}
            correctedFrame = {}
            frame_element = category_element.find('frame')
            if frame_element is not None:
                for slot in frame_element.findall('slot'):
                    slot_name = slot.get('name')

                    if not slot_name:
                        continue

                    # Caso 1: attributi diretti (value / correctedValue)
                    slot_value = slot.get('value')
                    slot_corrected_value = slot.get('correctedValue')

                    if slot_value:
                        if not slot_corrected_value:
                            slot_corrected_value = slot_value
                        frame[slot_name] = slot_value
                        correctedFrame[slot_name] = slot_corrected_value
                        continue

                    # Caso 2: lista semplice di <slot-value>
                    slot_values = slot.findall('slot-value')
                    if slot_values:
                        frame[slot_name] = []
                        correctedFrame[slot_name] = []
                        for value in slot_values:
                            v = value.get('value')
                            cv = value.get('correctedValue') or v
                            frame[slot_name].append(v)
                            correctedFrame[slot_name].append(cv)
                        continue

                    # Caso 3: lista di <slot-values> (liste di liste)
                    slot_values_groups = slot.findall('slot-values')
                    if slot_values_groups:
                        frame[slot_name] = []
                        correctedFrame[slot_name] = []
                        for group in slot_values_groups:
                            group_values = []
                            group_corrected = []
                            for value in group.findall('slot-value'):
                                v = value.get('value')
                                cv = value.get('correctedValue') or v
                                group_values.append(v)
                                group_corrected.append(cv)
                            frame[slot_name].append(group_values)
                            correctedFrame[slot_name].append(group_corrected)

            # Crea la nuova categoria
            category = Category(
                id=category_id,
                intent=intent,
                argument=argument,
                dialogue_acts_list=dialogue_acts_list,
                frame=frame,
                correctedFrame=correctedFrame,
                template=template,
            )

            self.categories.append(category)
            category_id += 1
            
        self.print_summary()

    def load_from_folder(self, folderpath: str) -> None:
        """
        Carica le categorie da una cartella contenente più file AIML e le inserisce nella lista delle categorie.
        """
        import os
        for filename in os.listdir(folderpath):
            if filename.endswith(".aiml"):
                self.load_from_aiml(os.path.join(folderpath, filename))

    def print_summary(self) -> None:
        """
        Stampa un sommario delle categorie caricate.
        """
        print(f"Total categories loaded: {len(self.categories)}")
        for category in self.categories:
            print(category)
            print()