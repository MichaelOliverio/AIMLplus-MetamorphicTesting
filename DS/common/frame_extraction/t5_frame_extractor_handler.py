       
from transformers import T5ForConditionalGeneration, T5Tokenizer
from common.frame_extraction.base_frame_extractor_handler import BaseFrameExtractorHandler

class T5FrameExtractorHandler(BaseFrameExtractorHandler):
    """Gestore per il modello T5."""
    
    def __init__(self, model_path: str, tokenizer_name: str):
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.tokenizer = T5Tokenizer.from_pretrained(tokenizer_name)
    
    def generate_output(self, text: str) -> str:
        """Genera output dal modello T5."""
        input_ids = self.tokenizer.encode(text, return_tensors="pt")
        output_ids = self.model.generate(input_ids, max_length=128)
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
