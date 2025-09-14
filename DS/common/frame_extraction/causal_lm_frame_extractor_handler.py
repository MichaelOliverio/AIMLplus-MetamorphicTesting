       
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from common.frame_extraction.base_frame_extractor_handler import BaseFrameExtractorHandler
import torch
from peft import PeftModel
import re

class CausalLMFrameExtractorHandler(BaseFrameExtractorHandler):
    """
    auto-regressive model handler
    """
    
    #def __init__(self, model_name:str, fine_tuned_model_path: str):
    def __init__(self, fine_tuned_model_path=None):
        """
        load the model and tokenizer
        """

        self.fine_tuned_model_path = fine_tuned_model_path
        self.pipe = None
        self.model = None
        self.tokenizer = None


        #base_model = AutoModelForCausalLM.from_pretrained(
        #    model_name,
        #    low_cpu_mem_usage=True,
        #    return_dict=True,
        #    torch_dtype=torch.float16,
        #    device_map="auto"
        #)

        # Carica il modello fine-tuned con i pesi LoRA dal percorso specificato
        # La funzione `from_pretrained` carica i pesi LoRA sopra il modello base
        #model = PeftModel.from_pretrained(base_model, fine_tuned_model_path)

        # Unisce i pesi LoRA nel modello base e rimuove i riferimenti a LoRA per ridurre l'uso della memoria
        #self.model = model.merge_and_unload()

        # Carica il tokenizer associato al modello fine-tuned
        # - `trust_remote_code=True` permette di eseguire codice personalizzato nel repository (se presente)
        #self.tokenizer = AutoTokenizer.from_pretrained(fine_tuned_model_path, trust_remote_code=True)
        #self.tokenizer.pad_token = self.tokenizer.eos_token
        #self.tokenizer.padding_side = "right"

    def merge_adapter(self, base_model):
        model = PeftModel.from_pretrained(base_model, self.fine_tuned_model_path)
        tokenizer = AutoTokenizer.from_pretrained(self.fine_tuned_model_path, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        return model, tokenizer
    
    def clear_output(self, output):
        match = re.search(r'\[ANW\](.*?)\[/ANW\]', output, re.DOTALL)
        return match.group(1) if match else None

    def generate_output(self, text: str, base_model, reload_model: bool) -> str:
        """
        output generation
        """
        if reload_model or self.model is None or self.tokenizer is None:
            self.model, self.tokenizer = self.merge_adapter(base_model)

        # check if pipe is available
        if self.pipe is None:
            self.pipe = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer, max_length=500)

        instruction = "Given the following input in (INPUT), you have to generate the corresponding json in (ANW)"
        result = self.pipe(f"<s> [INST] {instruction} [/INST] [INPUT] {text} [/INPUT] [ANW]")
        output = result[0]['generated_text']
        prediction = self.clear_output(output)
        print(prediction)

        if reload_model:
            del self.model
            del self.tokenizer
        
        return prediction
