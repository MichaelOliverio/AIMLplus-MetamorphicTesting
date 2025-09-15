from fastapi import FastAPI
from pydantic import BaseModel
import os
import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Optional

from aiml_parser.parser import AIMLParser
from common.frame_extraction.frame_extractor import FrameExtractor
from common.frame_extraction.causal_lm_frame_extractor_handler import CausalLMFrameExtractorHandler
from nlu.nlu import NLU
from dm.dm import DM

# ========================
# Setup iniziale
# ========================
load_dotenv()

app = FastAPI(title="NoVAGraphS-Pepper API")

# Verifica AIML
test_folder = "./aiml_data"
if not os.path.exists(os.path.abspath(test_folder)):
    raise RuntimeError("AIML non trovati/o")

parser = AIMLParser()
parser.load_from_folder(test_folder)

# CUDA check
cuda = torch.cuda.is_available()
print("CUDA available" if cuda else "CUDA not available")

# Modello LLaMA
model_name = "meta-llama/Llama-3.2-3B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cuda" if cuda else "cpu",
    torch_dtype="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Frame extractor
if cuda:
    frame_extractor_model_path = "./models/frame_extractor/Llama-3.2-3B-Instruct-Frame-Extractor"
    if not os.path.exists(os.path.abspath(frame_extractor_model_path)):
        raise RuntimeError("Frame Extractor Model non trovati/o")
    frame_extractor = FrameExtractor(
        CausalLMFrameExtractorHandler(fine_tuned_model_path=frame_extractor_model_path)
    )
else:
    raise RuntimeError("Serve CUDA per eseguire il Frame Extractor")

# NLU e DM
nlu = NLU(frame_extractor)
dm = DM(parser.categories, uncertainty_threshold=0.3)

# ========================
# Schema input/output
# ========================
class ChatRequest(BaseModel):
    user_input: str

class SvgElement(BaseModel):
    style_name: Optional[str] = None
    style_value: Optional[str] = None
    symbol: Optional[str] = None

class ChatResponse(BaseModel):
    nlu_output: dict
    response: str
    svg_elements: List[SvgElement] = []
    image: Optional[str] = None

# ========================
# Endpoint API
# ========================
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    nlu_output = nlu.extraction(request.user_input, model, False)
    #nlu_output = {
    #    'user_input': 'tell me about automaton',
    #    'intent': 'fsa-practical',
    #    'argument': 'transition',
    #    'dialogue_act': 'Ta:request',
    #    'frame': {'transitions':  [['q1','q2','0']]}
    #}
    action, already_asked_index = dm.process_input(nlu_output)
    system_output = action.template
    dm.update_state_tracker_with_system_response(system_output)

    return ChatResponse(
        nlu_output=nlu_output,
        response=system_output,
        svg_elements=action.svg_elements,  # presi da Category
        image=action.image                 # preso da Category
    )
