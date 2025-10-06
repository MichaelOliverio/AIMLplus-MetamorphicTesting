import random
import unicodedata

import config
from utils import metamorph_sentence_synonyms_simple


def filler_words(question):
    word_count = len(question.split())
    filler_words = ["uhm", "eh", "mmm"]
    metamorphed_qs = []
    #print("\nTest case: " + question + "\n____________________")

    for i in range(1, word_count + 1):
        filler_pos = random.sample(range(0, word_count), i)

        tmp_q = ""
        for x in range(0, word_count):
            if x in filler_pos:
                tmp_q += random.choice(filler_words) + " "
            tmp_q += question.split()[x] + " "

        tmp_q = tmp_q[0].upper() + tmp_q[1:].lower()
        #print("Follow-up: " + tmp_q)

        metamorphed_qs.append(tmp_q)

    return metamorphed_qs


def add_random_accents(question):
    word_count = len(question.split())
    accents_pos = random.sample(range(0, word_count), min(word_count, 2))

    metamorphed_q = ""
    for i in range(0, word_count):
        tmp_word = question.split()[i]
        if i in accents_pos:
            if tmp_word[-1] == 'a':
                tmp_word = tmp_word[:-1] + 'à'
            elif tmp_word[-1] == 'e':
                tmp_word = tmp_word[:-1] + 'è'
            elif tmp_word[-1] == 'i':
                tmp_word = tmp_word[:-1] + 'ì'
            elif tmp_word[-1] == 'o':
                tmp_word = tmp_word[:-1] + 'ò'
            elif tmp_word[-1] == 'u':
                tmp_word = tmp_word[:-1] + 'ù'
            else:
                tmp_word = tmp_word

        metamorphed_q += tmp_word + " "
    return metamorphed_q


def remove_doubles(question):
    tmp_q = ""
    prev_char = ""
    for char in question:
        if char != prev_char:
            tmp_q += char
        prev_char = char

    return tmp_q


def mistakes(question):
    #print("\nTest case: " + question + "\n____________________")
    metamorphed_qs = []

    # no accents
    tmp_q = ''.join(
        c for c in unicodedata.normalize('NFD', question)
        if unicodedata.category(c) != 'Mn'
    )

    if tmp_q != question:
        print("Follow-up: " + tmp_q)
        metamorphed_qs.append(tmp_q)

    # add accents todo: not for english
    # tmp_q = add_random_accents(question)
    # print("Follow-up: " + tmp_q)
    # metamorphed_qs.append(tmp_q)

    # remove double consonants
    tmp_q = remove_doubles(question)
    if tmp_q != question:
        print("Follow-up: " + tmp_q)
        metamorphed_qs.append(tmp_q)

    return metamorphed_qs


def synonyms(question):
    # print("\nTest case: " + question + "\n____________________")
    #return metamorph_sentence_synonyms(question)
    return metamorph_sentence_synonyms_simple(question)


def active_passive(question_number):
    file_path = "res/active_passive_corpus_states.txt"

    metamorphed_qs = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                tmp_line = line.strip()
                question = tmp_line.split(";")[1].strip()
                number = int(tmp_line.split(";")[0].strip())
                if question_number == number and question != "[NON TRASFORMABILE]":
                    metamorphed_qs.append(question)

    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

    return metamorphed_qs


def inversion_anastrophe(question_number):
    file_path = "res/inversion_corpus_states.txt"
    metamorphed_qs = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                tmp_line = line.strip()
                question = tmp_line.split(";")[1].strip()
                number = int(tmp_line.split(";")[0].strip())
                if question_number == number:
                    metamorphed_qs.append(question)

    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

    return metamorphed_qs


def get_metamorphed_questions(question, num):

    match num:
        case 1:
            metamorphed_qs = filler_words(question)
        case 2:
            metamorphed_qs = []
        case 3:
            metamorphed_qs = inversion_anastrophe(question)
        case 4:
            metamorphed_qs = []
        case 5:
            metamorphed_qs = active_passive(question)
        case 6:
            metamorphed_qs = []
        case 7:
            metamorphed_qs = synonyms(question)
        case 8:
            metamorphed_qs = mistakes(question)
        case _:
            metamorphed_qs = []

    return metamorphed_qs