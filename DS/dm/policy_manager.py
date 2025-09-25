import sys
from aiml_parser.category import Category
from typing import List, Optional, Any

# p.11 juraawsky
class PolicyManager:
    def __init__(self, categories: List[Category] = None, uncertainty_threshold=0):
        self.categories = categories
        self.uncertainty_threshold = uncertainty_threshold
        # Our systems might have a four-tiered level of confidence with
        # - three thresholds α, β, and γ:
        # < α low confidence reject
        # ≥ α above the threshold confirm explicitly
        # ≥ β high confidence confirm implicitly
        # ≥ γ very high confidence don’t confirm at all

    def select_action(self, context, state):
        """
        Seleziona l'azione successiva basandosi sul contesto.
        """

        # todo: se la vicinanza tra farme/embedding è bassa, si potrebbe attuare
        # qualche strategia di conferma (vedi jurawsky)

        # Trova le categorie che matchano con il dialogue act corrente
        categories = self.search_valid_categories(context, state)
        return self.frame_policy(context, state, categories)
        
    def frame_policy(self, context, state, categories) -> Optional[Category]:
        """
        Frame-based policy rule-based.
        """
        current_dialogue_act = context.get("dialogue_act")
        current_frame = context.get("frame")
        frame_history = state.get("frame_history")

        if current_dialogue_act in ["AutoF:autoNegative"]:
            previous_frame = frame_history[-1] if len(frame_history) > 1 else {}

            # merge current_frame with previous_frame
            merged_frame = previous_frame.copy()
            for slot in current_frame:
                if slot not in merged_frame:
                    merged_frame[slot] = current_frame[slot]

            frame = merged_frame
        else:
            frame = current_frame

        # controllo se esiste un frame uguale nel frame history (ultima occorrenza)
        already_asked_index = -1
        for i in range(len(frame_history) - 1, -1, -1):
            if frame_history[i] == frame:
                already_asked_index = i
                #print(f"Frame già presente nella storia dei frame all'ultima occorrenza all'indice {already_asked_index}.")
                break

        best_category, certainty_score = self.search_category_by_best_frame(categories, frame)
        print(f"Found {len(categories)} valid categories")
        print("best_category:", best_category)
        print("certainty_score:", certainty_score)

        if best_category: # and certainty_score >= self.uncertainty_threshold:
            print(f"Best category: {best_category.frame}, with score {certainty_score}")
            return best_category, already_asked_index
        else:
            return Category(
                id=None,
                intent=None,
                argument=None,
                dialogue_acts_list=None,
                frame=None,
                correctedFrame=None,
                template="Could you be more specific?",
            ), -1          
            
        
    def search_valid_categories(self, context, state) -> List[Category]:
        """
        Cerca le categorie che corrispondono all'argomento, all'intent del frame estratto nel turno corrente 
        e alla sequenza di atti dialogici avvenuti nella storia del dialogo
        """
        categories = []
        for category in self.categories:
            if context.get("argument") is None:
                categories.append(category)
            elif (category.intent == context.get("intent") or category.intent == None) and (category.argument == context.get("argument") or category.argument == None): # and self.match_dialogue_acts(category.dialogue_acts_list, context, state):
                categories.append(category)

        return categories
     
    def match_dialogue_acts(self, frame_dialogue_acts: List[str], context, state) -> bool:
        """
        Controlla se gli atti dialogici della categoria corrispondono alla storia recente degli atti dialogici.
        """

        history = state.get("dialogue_act_history", []).copy()
        current_act = context.get("dialogue_act")
        history.append(current_act)

        if len(frame_dialogue_acts) > len(history):
            return False

        # Confronta la fine della storia con i frame_dialogue_acts
        recent_history = history[-len(frame_dialogue_acts):]
        return recent_history == frame_dialogue_acts

    def search_category_by_best_frame(self, categories: List[Category], current_frame: Optional[dict] = None) -> Optional[Category]:
        """
        Cerca la categoria con il frame più simile all'input corrente.
        """
        best_category = None
        best_score = -1

        for category in categories:
            score = self.weighted_similarity(category.frame, current_frame)

            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category, best_score

    def weighted_similarity(self, frame1: dict, frame2: dict, weights: dict = {}, wildcard_weight: float = 0.2):
        """
        Calcola la similarità ponderata tra due frame, normalizzando il punteggio massimo a 1.
        
        - Una corrispondenza esatta 'chiave:valore' tra i frame contribuisce al peso pieno.
        - Una corrispondenza parziale (con valore '*') contribuisce con un peso ridotto.
        
        Parametri:
        - frame1, frame2: dizionari dei frame.
        - weights: dizionario dei pesi per ciascuna chiave.
        - wildcard_weight: peso da assegnare a corrispondenze con il jolly '*'.
        
        Restituisce:
        - La similarità normalizzata tra i due frame (valore tra 0 e 1).
        """
        total_weight = sum(weights.get(slot, 1) for slot in set(frame1.keys()).union(frame2.keys()))
        similarity = 0

        for slot in set(frame1.keys()).union(frame2.keys()):
            weight = weights.get(slot, 1)
            val1 = frame1.get(slot)
            val2 = frame2.get(slot)

            sim, _ = self.compare_values(val1, val2, weight, wildcard_weight)
            similarity += sim

        return min(similarity / total_weight, 1) if total_weight else 0
    

    def compare_values(self, val1, val2, weight, wildcard_weight):
        """
        Confronta due valori che possono essere scalari, liste o liste di liste.
        Restituisce (similarity, max_weight) così da normalizzare bene.
        """
        if val1 is None or val2 is None:
            return 0, weight

        # Caso scalare
        if not isinstance(val1, list) and not isinstance(val2, list):
            if val1 == val2:
                return weight, weight
            elif val1 == "*" or val2 == "*":
                return weight * wildcard_weight, weight
            else:
                return 0, weight

        # Caso lista
        if isinstance(val1, list) and isinstance(val2, list):
            min_len = min(len(val1), len(val2))
            max_len = max(len(val1), len(val2))
            sim = 0

            for i in range(min_len):
                sub_sim, sub_max = self.compare_values(val1[i], val2[i], weight, wildcard_weight)
                sim += sub_sim / max_len  # distribuisce il peso
            return sim, weight

        # Caso lista vs scalare → parziale
        return weight * wildcard_weight, weight
