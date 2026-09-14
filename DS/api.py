import xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException
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
import ast

import re

# ========================
# Setup iniziale
# ========================
load_dotenv()

app = FastAPI(title="NoVAGraphS-Pepper API")

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

# ========================
# Utilità per frame automa
# ========================
def carica_automa_da_svg(nome_file: str, layer_id: str = "layer1") -> dict:
    """
    Legge un file SVG e restituisce un automa come dizionario:
    {
        "initialState": str,
        "finalStates": List[str],
        "states": List[str],
        "transitions": List[List[str, str, str|None]]
    }
    
    Args:
        nome_file: percorso del file SVG
        layer_id: id del layer che contiene l'automa (default "layer1")
        
    Returns:
        automa: dict con struttura dati dell'automa
    """
    try:
        tree = ET.parse(nome_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File SVG '{nome_file}' non trovato")
    except ET.ParseError:
        raise HTTPException(status_code=400, detail=f"File SVG '{nome_file}' non valido")

    root = tree.getroot()

    # Trova il layer contenente l'automa
    automa_layer = None
    for child in root:
        if child.attrib.get('id') == layer_id:
            automa_layer = child
            break

    if automa_layer is None:
        raise RuntimeError(f"Layer '{layer_id}' non trovato nel SVG")

    stati = []
    finalStates = []
    transizioni = []
    initialState = None

    for child in automa_layer:
        elem_id = child.attrib.get('id', '')
        if 'title' in elem_id:
            continue

        # Stato iniziale
        if elem_id.startswith('start-'):
            initialState = elem_id.replace('start-', '')

        # Stati e stati finali
        elif elem_id.startswith('stato-'):
            stato = elem_id.replace('stato-', '')
            if stato.endswith('-finale'):
                stato = stato.replace('-finale', '')
                if stato not in finalStates:
                    finalStates.append(stato)
            if stato not in stati:
                stati.append(stato)

        # Transizioni
        elif elem_id.startswith('transizione-'):
            parts = elem_id.replace('transizione-', '').split('-')
            if len(parts) < 2:
                continue
            sorgente, destinazione = parts[0], parts[1]
            simboli = []

            # Trova i simboli associati alla transizione
            for child2 in child:
                if 'valore' in child2.attrib.get('id', ''):
                    for child3 in child2:
                        simboli.append(child3.text)

            # Se non ci sono simboli, la transizione ha None
            if simboli:
                for s in simboli:
                    transizioni.append([sorgente, destinazione, s])
            else:
                transizioni.append([sorgente, destinazione, None])

    # Costruzione struttura dati finale
    automa = {
        "initialState": initialState,
        "finalStates": finalStates,
        "states": stati,
        "transitions": transizioni
    }

    return automa

def filtra_automa(automa: dict, ids: List[str]) -> dict:
    """
    Costruisce un frame a partire dagli ID (query), usando i dati reali dell'automa.
    - Se c'è un valore-qX-qY, prende il valore reale dall'automa
    - Se c'è solo transizione-qX-qY, mette '?'
    """
    frame = {
        "initialState": None,
        "finalStates": [],
        "states": [],
        "transitions": []
    }

    valori = {}          # (src,dst) -> valore reale
    transizioni_tmp = {} # (src,dst) -> True se presente transizione

    # mappa delle transizioni dell'automa per recuperare il valore reale
    automa_transitions_map = {}
    for t in automa.get("transitions", []):
        automa_transitions_map[(t[0], t[1])] = t[2]

    # loop sugli ID della query
    for elem in ids:
        if elem.startswith("start-"):
            stato = elem.replace("start-", "")
            if stato == automa.get("initialState"):
                frame["initialState"] = stato

        elif elem.startswith("stato-"):
            stato = elem.replace("stato-", "")
            if stato.endswith("-finale"):
                stato = stato.replace("-finale", "")
                if stato in automa.get("finalStates", []) and stato not in frame["finalStates"]:
                    frame["finalStates"].append(stato)
            if stato in automa.get("states", []) and stato not in frame["states"]:
                frame["states"].append(stato)

        elif elem.startswith("valore-"):
            match = re.match(r"valore-(q\d+)-(q\d+)", elem)
            if match:
                src, dst = match.groups()
                if (src, dst) in automa_transitions_map:
                    valori[(src, dst)] = automa_transitions_map[(src, dst)]

        elif elem.startswith("transizione-"):
            match = re.match(r"transizione-(q\d+)-(q\d+)", elem)
            if match:
                src, dst = match.groups()
                if (src, dst) in automa_transitions_map:
                    transizioni_tmp[(src, dst)] = True

    # costruzione transizioni: valori reali hanno priorità
    all_keys = set(list(transizioni_tmp.keys()) + list(valori.keys()))
    for k in all_keys:
        src, dst = k
        if k in valori:
            frame["transitions"].append([src, dst, valori[k]])
        else:
            frame["transitions"].append([src, dst, "?"])

    return frame

def merge_frames(frame1: dict, frame2: dict) -> dict:
    """
    Unisce due frame di automa:
    - initialState: priorità a frame1 se presente
    - finalStates, states, transitions: unione senza duplicati
    - '?' viene rimosso se ci sono valori reali per lo stesso elemento
    - scarta elementi vuoti o nulli
    """
    merged = {}

    # =========================
    # initialState
    # =========================
    initial = frame1.get("initialState") or frame2.get("initialState")
    if initial is not None:
        merged["initialState"] = initial

    # =========================
    # finalStates
    # =========================
    final_values = set(frame1.get("finalStates", [])) | set(frame2.get("finalStates", []))
    if "?" in final_values and len(final_values) > 1:
        final_values.remove("?")
    if final_values:
        merged["finalStates"] = list(final_values)

    # =========================
    # states
    # =========================
    state_values = set(frame1.get("states", [])) | set(frame2.get("states", []))
    if "?" in state_values and len(state_values) > 1:
        state_values.remove("?")
    if state_values:
        merged["states"] = list(state_values)

    # =========================
    # transitions
    # =========================
    transitions_map = {}
    for t in frame1.get("transitions", []) + frame2.get("transitions", []):
        key = (t[0], t[1])
        transitions_map.setdefault(key, set()).add(t[2])

    final_transitions = []
    for (s, d), vals in transitions_map.items():
        if len(vals) > 1 and "?" in vals:
            vals.remove("?")
        for v in vals:
            if v is not None and v != "":  # scarta valori nulli o vuoti
                final_transitions.append([s, d, v])

    if final_transitions:
        merged["transitions"] = final_transitions

    return merged

# ========================
# Schema input/output
# ========================
class ChatRequest(BaseModel):
    user_input: str
    query: Optional[List[str]] = None
    file_name: str

class SvgElement(BaseModel):
    style_name: Optional[str] = None
    style_value: Optional[str] = None
    symbol: Optional[str] = None

class ChatResponse(BaseModel):
    nlu_output: dict
    best_frame: dict
    certainty_score: Optional[float]
    response: str
    svg_elements: List[SvgElement] = []
    image: Optional[str] = None

# ========================
# Endpoint API
# ========================
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    nome_file_svg = f"./svg_files/{request.file_name}.svg"
    if not os.path.exists(nome_file_svg):
        raise HTTPException(status_code=404, detail=f"File SVG '{nome_file_svg}' non trovato")

    automa = carica_automa_da_svg(nome_file_svg)
    print("automa caricato")

    aiml_path = f"./aiml_data/{request.file_name}.aiml"
    if not os.path.exists(aiml_path):
        raise HTTPException(status_code=404, detail=f"File AIML '{aiml_path}' non trovato")

    parser = AIMLParser()
    parser.load_from_aiml(aiml_path)
    print("AIML caricati")

    dm = DM(parser.categories, uncertainty_threshold=0)
    print("DM inizializzato")

    # Estrazione NLU
    MAX_RETRIES = 10

    for attempt in range(MAX_RETRIES):
        try:
            nlu_output = nlu.extraction(request.user_input, model, False)
            break
        except (KeyError, SyntaxError, ValueError) as e:
            print(f"Tentativo {attempt+1}: {e}")
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(500, detail=str(e))

    #nlu_output = nlu.extraction(request.user_input, model, False)

    print("NLU output:", nlu_output)

    #nlu_output = {
    #    'user_input': 'tell me about automaton',
    #    'intent': 'fsa-practical',
    #    'argument': 'transition',
    #    'dialogue_act': 'Ta:request',
    #    'frame': {'states':['?'], 'transitions':  [['q1','q2','?']]}
    #}

    #nlu_output = {
    #    "user_input": "tell me about this",
    #    "intent": "fsa-practical",
    #    "argument": None,
    #    "dialogue_act": "AutoF:autoNegative",
    #    "frame": {
    #        "states": [
    #            "q1"
    #        ]
    #    },
    #}

    # Merge frame con query (se presente)
    if request.query:
        frame_from_query = filtra_automa(automa, request.query)

        if "frame" in nlu_output and isinstance(nlu_output["frame"], dict):
            nlu_output["_raw_frame"] = nlu_output["frame"]
            nlu_output["frame"] = merge_frames(nlu_output["frame"], frame_from_query)
        else:
            nlu_output["frame"] = frame_from_query

    # DM
    action, already_asked_index, certainty_score, best_frame = dm.process_input(nlu_output)
    system_output = action.template
    dm.update_state_tracker_with_system_response(system_output)

    if best_frame is not None and not isinstance(best_frame, dict):
        best_frame = best_frame.__dict__

        filtered_best_frame = {
            "intent": best_frame.get("intent"),
            "argument": best_frame.get("argument"),
            "dialogue_acts_list": best_frame.get("dialogue_acts_list"),
            "correctedFrame": best_frame.get("correctedFrame"),
        }
    else:
        filtered_best_frame = {}

    return ChatResponse(
        nlu_output=nlu_output,
        best_frame=filtered_best_frame,
        certainty_score=certainty_score,
        response=system_output,
        svg_elements=action.svg_elements,  # presi da Category
        image=action.image                 # preso da Category
    )


@app.post("/chat_nlu", response_model=ChatResponse)
def chat(request: ChatRequest):
    nome_file_svg = f"./svg_files/automa1.svg"
    if not os.path.exists(nome_file_svg):
        raise HTTPException(status_code=404, detail=f"File SVG '{nome_file_svg}' non trovato")

    automa = carica_automa_da_svg(nome_file_svg)
    print("automa caricato")

    aiml_path = f"./aiml_data/{request.file_name}.aiml"
    if not os.path.exists(aiml_path):
        raise HTTPException(status_code=404, detail=f"File AIML '{aiml_path}' non trovato")

    parser = AIMLParser()
    parser.load_from_aiml(aiml_path)
    print("AIML caricati")

    dm = DM(parser.categories, uncertainty_threshold=0)
    print("DM inizializzato")

    # Estrazione NLU
    nlu_output = ast.literal_eval(request.user_input)
    print("NLU output:", nlu_output)

    # Merge frame con query (se presente)
    if request.query:
        frame_from_query = filtra_automa(automa, request.query)

        if "frame" in nlu_output and isinstance(nlu_output["frame"], dict):
            nlu_output["_raw_frame"] = nlu_output["frame"]
            nlu_output["frame"] = merge_frames(nlu_output["frame"], frame_from_query)
        else:
            nlu_output["frame"] = frame_from_query

    # DM
    action, already_asked_index, certainty_score, best_frame = dm.process_input(nlu_output)
    system_output = action.template
    dm.update_state_tracker_with_system_response(system_output)

    if best_frame is not None and not isinstance(best_frame, dict):
        best_frame = best_frame.__dict__

        filtered_best_frame = {
            "intent": best_frame.get("intent"),
            "argument": best_frame.get("argument"),
            "dialogue_acts_list": best_frame.get("dialogue_acts_list"),
            "correctedFrame": best_frame.get("correctedFrame"),
        }
    else:
        filtered_best_frame = {}

    return ChatResponse(
        nlu_output=nlu_output,
        best_frame=filtered_best_frame,
        certainty_score=certainty_score,
        response=system_output,
        svg_elements=action.svg_elements,  # presi da Category
        image=action.image                 # preso da Category
    )
