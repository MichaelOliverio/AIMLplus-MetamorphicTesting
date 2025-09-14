# https://journals.uic.edu/ojs/index.php/dad/article/view/10729/9497

class StateTracker:
    def __init__(self):
        self.state = {
            "user_input_history": [],
            "intent_history": [],
            "argument_history": [],
            "dialogue_act_history": [],
            "frame_history": [],
            "system_action_history": [], # category hitstory (se in passato è già apparsa si potrebbe rispondere in maniera diversa)
            "system_response_history": [],
            "current_context": {},
        }

        self.dialogue_state = {} #todo p.10 juraawsky
        # The dialogue-state is not just the slot-fillers in the current sentence; it includes the entire state of the
        # frame at this point, summarizing all of the user’s constraints
        
        #self.common_ground = {} #todo

    def update_state(self, user_input=None, intent=None, argument=None, dialogue_act=None, frame=None, system_action=None, system_response=None, current_context=None):
        """
        Aggiorna lo stato del dialogo con l'input dell'utente, l'azione del sistema, e il contesto corrente.
        """
        if user_input:
            self.state["user_input_history"].append(user_input)
        if intent:
            self.state["intent_history"].append(intent)
        if argument:
            self.state["argument_history"].append(argument)
        if dialogue_act:
            self.state["dialogue_act_history"].append(dialogue_act)
        if frame:
            self.state["frame_history"].append(frame)
        if system_action:
            self.state["system_action_history"].append(system_action)
        if system_response:
            self.state["system_response_history"].append(system_response)
        if current_context:
            self.state["current_context"] = current_context

    def get_state(self):
        """
        Restituisce lo stato corrente del dialogo.
        """
        return self.state
    
    def get_system_response_by_index(self, index: int):
        """
        Ottiene la risposta del sistema in base all'indice.
        """
        if 0 <= index < len(self.state["system_response_history"]):
            return self.state["system_response_history"][index]
        return None
