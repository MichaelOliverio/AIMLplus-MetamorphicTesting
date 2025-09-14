import os
from aiml_parser.parser import AIMLParser
from common.frame_extraction.frame_extractor import FrameExtractor
from common.frame_extraction.t5_frame_extractor_handler import T5FrameExtractorHandler
from common.frame_extraction.causal_lm_frame_extractor_handler import CausalLMFrameExtractorHandler
from nlu.nlu import NLU
from dm.dm import DM
import torch
from dotenv import load_dotenv

from transformers import AutoModelForCausalLM, AutoTokenizer

if __name__ == "__main__":
    load_dotenv() # load environment variables from .env file

    # check if AIML files are available
    test_folder = "DS/aiml_data"
    if not os.path.exists(os.path.abspath(test_folder)):
        print(f"AIML non trovati/o")
        exit()

    parser = AIMLParser()
    parser.load_from_folder(test_folder)

    # check if cuda available
    cuda = False
    if torch.cuda.is_available():
        cuda = True
        print("CUDA available")
    else:
        print("CUDA not available")

    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # frame extractor
    if cuda:
        print(f"Using LLaMA-3.2-3B for Frame Extraction")
        frame_extractor_model_path = f'DS/models/frame_extractor/Llama-3.2-3B-Instruct-Frame-Extractor'
        if not os.path.exists(os.path.abspath(frame_extractor_model_path)):
            print(f"Frame Extractor Model non trovati/o")
            exit()
        frame_extractor = FrameExtractor(CausalLMFrameExtractorHandler(fine_tuned_model_path=frame_extractor_model_path))
    else:
        exit()
    
    nlu = NLU(frame_extractor)
    dm = DM(parser.categories, uncertainty_threshold=0.3) # ricerca per frame

    '''nlu_output = {
        'user_input': 'tell me about automaton',
        'intent': 'fsa-practical',
        'argument': 'transition',
        'dialogue_act': 'Ta:request',
        'frame': {'transitions':  [['q1','q2','0']]}
    }
    nlu_output = {
        'user_input': 'What is the final state',
        'intent': 'fsa-practical',
        'argument': 'state',
        'dialogue_act': 'Ta:setQuestion',
        'frame': {'finalStates':  '?'}
    }
    action, already_asked_index = dm.process_input(nlu_output)
    print(f"response: {action.template}")
    dm.update_state_tracker_with_system_response(action.template)
    print(dm.get_system_response_by_index(already_asked_index))'''

    while True:
        input_text = input("input: ")
    
        nlu_output = nlu.extraction(input_text, model, False)
        print(f"nlu_output: {nlu_output}")
    
        action, already_asked_index = dm.process_input(nlu_output)
        system_output = action.template
        print(f"aiml+ response: {action}")
        print()
        dm.update_state_tracker_with_system_response(system_output)