import re
import xml.etree.ElementTree as ET

exclude_words = ["essere"]



def substitute(i, synonyms_list, question):
    metamorphed_qs = []
    print(synonyms_list)
    for syn in synonyms_list:
        metamorphed_q = ""
        for index, word in enumerate(question.split()):
            if i == index:
                metamorphed_q += syn + " "
            else:
                metamorphed_q += word + " "
        metamorphed_qs.append(metamorphed_q)
        print("Follow-up: " + metamorphed_q)
    return metamorphed_qs


def metamorph_sentence_synonyms_simple(question):
    synonyms_list = [["cerchio", "tondo", "circonferenza", "anello", "insieme", "gruppo", "disco"],
                     ["cerchi", "tondi", "circonferenze", "anelli", "insiemi", "gruppi", "dischi"],
                     ["freccia", "vettore", "indicatore", "puntatore"],
                     ["frecce", "vettori", "indicatori", "puntatori"],
                     ["connesso", "collegato", "unito", "associato"],
                     ["connessa", "collegata", "unita", "associata"],
                     ["connessi", "collegati", "uniti", "associati"],
                     ["descrivi", "spiega", "racconta"],
                     ["descrivimi", "spiegami", "raccontami"],
                     ["automaton", "finite automaton", "machine", "state machine"],
                     ["describe", "specify", "define", "outline"],
                     ["transition", "state transition", "arc"],
                     ["state", "configuration"],
                     ["cycle", "loop"],
                     ["final", "goal", "end"]
                     ]

    metamorphed_qs = []
    word_count = len(question.split())
    i = 0
    for i in range(0, word_count):
        tmp_word = re.sub(r'[^\w\s]', '', question.split()[i].lower())

        for syns in synonyms_list:
            if tmp_word in syns:
                for syn in syns:
                    if syn != tmp_word:
                        metamorphed_qs.append(" ".join(question.split()[:i]) + " " + syn + " " + " ".join(question.split()[i + 1:]))
                        #print(" ".join(question.split()[:i]) + " " + syn + " " + " ".join(question.split()[i + 1:]))
        i+=1

    return metamorphed_qs


def extract_couples(svg_path):
    links = get_svg_link_ids(svg_path)
    couples = []

    for link in links:
        tmp = link.split("-")
        if check_couple(tmp[1], tmp[2], links):
            couples.append([f"A cos'è connesso l'elemento {tmp[1]}", f"A cos'è connesso l'elemento {tmp[2]}"])

    return couples


def get_svg_link_ids(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    ids = []
    for elem in root.iter():
        elem_id = elem.attrib.get("id")
        if elem_id and "link" in elem_id:
            ids.append(elem_id)
    return ids


def check_couple(param1, param2, links):
    domain = 0
    codomain = 0
    for link in links:
        if param1 in link:
            domain += 1
        if param2 in link:
            codomain += 1

    return domain == 1 and codomain == 1