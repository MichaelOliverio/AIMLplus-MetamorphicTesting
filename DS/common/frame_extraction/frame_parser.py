import re
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrameParser:
    """Parser per analizzare l'output del modello."""
    
    @staticmethod
    def parse_output(output_text: str) -> dict:
        """Analizza l'output e restituisce un dizionario con i valori estratti."""

        mapData = {
            'ar' : 'argument',
            'da' : 'dialogue_act',
            'et' : 'intent',
            'sn' : 'slot_names',
            'sv' : 'slot_values'
        }

        result = {}

        convertedOutput = ast.literal_eval(output_text)
        if convertedOutput:
            for key, value in convertedOutput.items():
                if isinstance(value, str):
                    if re.match(r"^\[.*\]$", value):
                        try:
                            value = ast.literal_eval(value)
                            result[mapData[key]] = value
                        except Exception:
                            pass
                    else:
                        result[mapData[key]] = value

        else:
            #patterns = {
            #    'intent': r"'intent':\s*'([^']+)'",
            #    'argument': r"'argument':\s*'([^']+)'",
            #    'dialogue_act': r"'dialogue_act':\s*'([^']+)'",
            #    'slot_names': r"'slot_names':\s*\[([^\]]+)\]",
            #    'slot_values': r"'slot_values':\s*(\[[^\]]*\].*)"
            #}
            patterns = {
                'intent': r"'et':\s*'([^']+)'",
                'argument': r"'ar':\s*'([^']+)'",
                'dialogue_act': r"'da':\s*'([^']+)'",
                'slot_names': r"'sn':\s*\[([^\]]+)\]",
                'slot_values': r"'sv':\s*(\[[^\]]*\].*)"
            }
            arguments = [
                'alphabet',
                'automaton',
                'language',
                'state',
                'transition',
                'pattern',
            ]

            dialogue_acts = [
                'AutoF:autoNegative',
                'DS:opening',
                'DS:suggest',
                #'OCM:selfCorrection',
                'SOM:initGoodbye',
                #'SOM:returnGreeting',
                #'SOM:thanking',
                'Ta:answer',
                'Ta:checkQuestion',
                'Ta:propositionalQuestion',
                'Ta:request',
                'Ta:setQuestion',
                #'TuM:turnAccept',
            ]
           
            slot_names = {
                'alphabet': 'list',
                'input': 'str',
                'output': 'str',
                'numberOfStates': 'str',
                'numberOfFinalStates': 'str',
                'states': 'list',
                'initialState': 'str',
                'finalStates': 'list',
                'numberOfTransitions': 'str',
                'transition': 'triple_list',
                'automatonType': 'str',
                'languageType': 'str',
                'graphicRepresentation': 'str',
                'optimalSpatialRepresentation': 'str',
                'stateWithMostTransitions': 'str',
                'stateWithoutTransitions': 'str',
            }


            result = {}

            for key, pattern in patterns.items():
                match = re.search(pattern, output_text)
                if match:
                    if key == 'slot_values':
                        list_str = match.group(1).strip()
                        if list_str.startswith('[') and list_str.endswith(']'):
                            list_str = list_str.replace("'", '"')
                            try:
                                result[key] = eval(list_str)
                            except Exception as e:
                                logger.error(f"Errore nell'analizzare slot_values: {e}")
                                result[key] = []
                        else:
                            logger.warning("Formato errato per slot_values.")
                            result[key] = []
                    elif key == 'slot_names':
                        list_str = match.group(1).strip().replace("'", '"')
                        result[key] = ast.literal_eval(f"[{list_str}]")
                    else:
                        result[key] = match.group(1)
                else:
                    result[key] = None

            # post-processing
            if result['dialogue_act'] and result['dialogue_act'].lower() not in [d.lower() for d in dialogue_acts]:
                if 'prop' in result['dialogue_act'].lower():
                    result['dialogue_act'] = 'Ta:propositionalQuestion'
                else:
                    result['dialogue_act'] = 'Ta:request'

            if result['argument'] and result['argument'].lower() not in [a.lower() for a in arguments]:
                arg_lower = result['argument'].lower()
                if 'alph' in arg_lower:
                    result['argument'] = 'alphabet'
                elif 'auto' in arg_lower:
                    result['argument'] = 'automaton'
                elif 'lang' in arg_lower:
                    result['argument'] = 'language'
                elif 'stat' in arg_lower:
                    result['argument'] = 'state'
                elif 'tran' in arg_lower:
                    result['argument'] = 'transition'
                elif 'patt' in arg_lower:
                    result['argument'] = 'pattern'
                else:
                    result['argument'] = None

        if result['argument']:
            result['argument'] = result['argument'].lower()

        intent = [
            'fsa-theoretical',
            'fsa-practical',
        ]
        
        if result['intent'] and result['intent'].lower() not in [i.lower() for i in intent]:
            intent_lower = result['intent'].lower()
            if 'the' in intent_lower:
                result['intent'] = 'fsa-practical' # di base mettere theroetical
            elif 'prac' in intent_lower:
                result['intent'] = 'fsa-practical'
            elif result['dialogue_act'] == 'Ta:request':
                result['intent'] = 'fsa-practical'
            else:
                result['intent'] = None

        if result['intent'] == 'fsa-theoretical':
            result['intent'] = 'fsa-practical'

        result = FrameParser.convert_tuples_to_lists(result)
        return result
    
    @staticmethod
    def convert_tuples_to_lists(obj):
        """Ricorsivamente converte tutte le tuple in liste."""
        if isinstance(obj, tuple):
            return [FrameParser.convert_tuples_to_lists(x) for x in obj]
        elif isinstance(obj, list):
            return [FrameParser.convert_tuples_to_lists(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: FrameParser.convert_tuples_to_lists(v) for k, v in obj.items()}
        else:
            return obj