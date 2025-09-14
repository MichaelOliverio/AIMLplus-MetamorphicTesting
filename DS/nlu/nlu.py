from common.frame_extraction.frame_extractor import FrameExtractor

class NLU:
    def __init__(self, frame_extractor: FrameExtractor):
        self.frame_extractor = frame_extractor

    def extraction(self, user_input: str, base_model, reload_model: bool) -> None:
        """
        Processo di comprensione del linguaggio naturale (NLU). Manipola e analizza l'utterance dell'utente.
        """
        intent, argument, dialogue_act, frame = self.frame_extractor.get_frame(user_input, base_model, reload_model) # estrazione frame

        return {
            'user_input': user_input,
            'intent': intent,
            'argument': argument,
            'dialogue_act': dialogue_act,
            'frame': frame
        }