from common.frame_extraction.base_frame_extractor_handler import BaseFrameExtractorHandler
from common.frame_extraction.frame_parser import FrameParser

class FrameExtractor:
    """Classe per generare frame utilizzando un modello di generazione."""
    
    def __init__(self, model_handler: BaseFrameExtractorHandler):
        self.model_handler = model_handler

    def get_frame(self, text: str, base_model, reload_model: bool) -> tuple:
        """Genera il frame dall'input testuale."""
        output_text = self.model_handler.generate_output(text, base_model, reload_model)

        if output_text:
            parsed_output = FrameParser.parse_output(output_text)
            print(parsed_output)

            intent = parsed_output['intent']
            argument = parsed_output['argument']
            dialogue_act = parsed_output['dialogue_act']

            frame = {}
            if parsed_output['slot_names'] and parsed_output['slot_values']:
                for i, slot_name in enumerate(parsed_output['slot_names']):
                    if i < len(parsed_output['slot_values']):
                        frame[slot_name] = parsed_output['slot_values'][i]

             # --- controllo specifico per 'transitions' ---
            if 'transitions' in frame:
                if isinstance(frame['transitions'], str):
                    frame['transitions'] = []
                elif not isinstance(frame['transitions'], list):
                    frame['transitions'] = []

        else:
            intent = None
            argument = None
            dialogue_act = None
            frame = {}

        return intent, argument, dialogue_act, frame
