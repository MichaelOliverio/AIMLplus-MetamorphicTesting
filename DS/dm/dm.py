import sys
from dm.dialogue_context import DialogueContext
from dm.policy_manager import PolicyManager
from dm.state_tracker import StateTracker
from aiml_parser.category import Category
from typing import List, Optional, Any

class DM:
    def __init__(self, categories: List[Category] = None, uncertainty_threshold=0):
        if uncertainty_threshold < 0 or uncertainty_threshold > 1:
            raise ValueError("uncertainty_threshold deve essere un valore compreso tra 0 e 1")

        self.dialogue_context = DialogueContext()
        self.state_tracker = StateTracker()
        self.policy_manager = PolicyManager(categories, uncertainty_threshold)

    def process_input(self, nlu_output):
        """
        Processo principale del Dialogue Manager:
        1. Aggiorna lo stato del dialogo.
        2. Aggiorna il contesto del dialogo.
        3. Decide l'azione successiva tramite il Policy Manager.
        4. Restituisce l'azione da passare al modulo di NLG.
        """
        # Estrai informazioni dall'output di NLU
        user_input = nlu_output['user_input']
        intent = nlu_output['intent']
        argument = nlu_output['argument']
        dialogue_act = nlu_output['dialogue_act']
        frame = nlu_output['frame']

        # Step 1: Aggiorna il contesto del dialogo
        self.dialogue_context.update_context({
            "user_input": user_input,
            "intent": intent,
            "argument": argument,
            "dialogue_act": dialogue_act,
            "frame": frame,
        })

        # Step 2: Decidi l'azione successiva
        system_action, already_asked = self.policy_manager.select_action(
            self.dialogue_context.get_context(),
            self.state_tracker.get_state()
        )

        # Step 3: Aggiorna lo stato del dialogo
        self.state_tracker.update_state(
            user_input=user_input,
            intent=intent,
            argument=argument,
            dialogue_act=dialogue_act,
            frame=frame,
            system_action=system_action,
            current_context=self.dialogue_context.get_context(),
        )

        # step 4: Aggiorna il common ground
        # self.state_tracker.update_common_ground({})

        # Step 5: Restituisci l'azione (es. domanda o risposta)
        return system_action, already_asked
    
    def update_state_tracker_with_system_response(self, system_response):
        """
        Aggiorna lo stato del tracker con la risposta del sistema.
        """
        self.state_tracker.update_state(
            system_response=system_response,
        )

    def get_system_response_by_index(self, index: int) -> Optional[str]:
        """
        Ottiene la risposta del sistema in base all'indice.
        """
        if index >= 0:
            return self.state_tracker.get_system_response_by_index(index)
        return None