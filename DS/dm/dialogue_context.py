class DialogueContext:
    def __init__(self):
        self.context = {
            "user_input": None,
            "intent": None,
            "argument": None,
            "dialogue_act": None,
            "frame": {},
        }

    def update_context(self, updates):
        """
        Aggiorna il contesto con nuove informazioni.
        """
        for key, value in updates.items():
            self.context[key] = value

    def get_context(self):
        """
        Restituisce il contesto corrente.
        """
        return self.context

    def clear_context(self):
        """
        Resetta il contesto (es. per un nuovo dialogo).
        """
        self.context = {
            "user_input": None,
            "intent": None,
            "argument": None,
            "dialogue_act": None,
            "frame": {},
        }
