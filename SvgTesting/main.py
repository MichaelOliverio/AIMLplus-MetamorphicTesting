import csv
import os

import re
from metamorph_utils import *
from test import *
from utils import extract_couples
import config

start = 0

def multiple_question(question, index, domain = True):
    print("\nTest case: " + question + "\n____________________")
    metamorphed_qs = []
    if domain:
        file_path = "res/corpus.txt"

        tmp_q = question
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    question2 = line.strip()
                    if i != index and random.random() < 0.2:
                        tmp_q += " " + question2
                        print("Follow-up: " + tmp_q)
                        metamorphed_qs.append((question2, tmp_q))
                        tmp_q = question

        except FileNotFoundError:
            print(f"file '{file_path}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")

    else:
        file_path = "res/corpus.csv"

        tmp_q = question
        with open(file_path, newline="", encoding="latin1") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            i = 0
            for row in reader:
                participant = row[3]
                question2 = row[4]
                if participant == "U":
                    i += 1
                    if i != index and i not in config.EXCLUDE and random.random() < 0.01 and len(metamorphed_qs) < 2:
                        tmp_q += ". " + question2
                        print("Follow-up: " + tmp_q)
                        metamorphed_qs.append((question2, tmp_q))
                        tmp_q = question

    return metamorphed_qs


def test_multiple_questions(question, i, domain = True):
    metamorphed_qs = multiple_question(question, i, domain)

    if domain:
        test_case1 = get_dialogue_answer(question)
    else:
        test_case1 = get_dialogue_answer_states(question)

    if test_case1[0] == "Potresti essere più specifico?":
        config.EXCLUDE.append(i)
    else:

        print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format("text1", "multi1", "text2", "multi2","text_cnc", "multi_cnc"))
        print("-" * 70)

        for q2, m in metamorphed_qs:
            #print(question + "____" + q2)
            if domain:
                test_case2 = get_dialogue_answer(q2)
            else:
                test_case2 = get_dialogue_answer_states(q2)
            if domain:
                follow_up = get_dialogue_answer(m)
            else:
                follow_up = get_dialogue_answer_states(m)


            compare_multiple(test_case1, test_case2, follow_up, question, q2, m)


def test_mr_6():
    n = 1
    svg_path = f"res/esempio{n}.svg"
    for couple in extract_couples(svg_path):
        test_same(couple[0], [couple[1]], n)


def main():
    print("Start SVG-AIML testing\n")

    #ask_llama("Rendi questa frase passiva, rispondi solo con la frase: \"Cosa vuol dire \"A\" e \"B\" sopra i cerchi?\"")

    file_path = "res/corpus.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question = line.strip()
                # print(f" {i}: {question}")
                # get_dialogue_answer(question)

                # 1: filler words
                #test_same(question, get_metamorphed_questions(question, 1))

                # 3: sentence inversion / anastrophe
                # test_same(question, get_metamorphed_questions(i, 3))
                # 5: active passive sentence
                # test_same(question, get_metamorphed_questions(i, 5))

                # 7: synonyms
                # test_same(question, get_metamorphed_questions(question, 7))
                # 8: mistakes
                #test_same(question, get_metamorphed_questions(question, 8))

                # 10: multiple questions
                #test_multiple_questions(question, i)

    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")


    # 6: domain/codomain
    #test_mr_6()


def get_last_value(path_csv):
    with open(path_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=";")
        righe = list(reader)

        if not righe:  # se il file è vuoto
            print("File vuoto.")
            return None

        ultima_riga = righe[-1]

        if not ultima_riga or not ultima_riga[0].isdigit():
            print("Nessun intero valido nella prima colonna.")
            return None

        print(int(ultima_riga[0]))
        return int(ultima_riga[0])


def test_mr(file_path, file_name, mr, corpus_type):
    #config.FILE_NAME = file_name
    config.TEST_RELATION = mr

    path_csv = "res/results/" + str(config.TEST_RELATION) + ".csv"
    global start
    start = 0
    if not os.path.isfile(path_csv):
        with open(path_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                ["TEST_CASE_NUMBER", "TEST CASE", "FOLLOW UP", "TEST CASE TEXT", "TEST CASE MULTI", "FOLLOW UP TEXT",
                 "FOLLOW UP MULTI", "COMPARE TEXT", "COMPARE MULTI"])
    else:
        start = get_last_value(path_csv)


    with open(file_path, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            config.TEST_CASE_NUMBER = row[0]
            question = row[1]
            mrs = row[2]
            if int(config.TEST_CASE_NUMBER) > start and corpus_type in mrs:
                test_same(question, [question], domain = False, file_name = file_name)


def create_follow(follow_up, ids):
    #ids = json.loads(ids)
    ids = [ids]

    for id in ids:
        follow_up = re.sub(r"(this|that|theese|those)", id, follow_up, count=1)

    follow_up = follow_up.replace("stato", "state")
    follow_up = follow_up.replace("valore", "transition value")
    follow_up = follow_up.replace("-", " ")
    follow_up = follow_up.replace("transizione", "transition")

    print(follow_up)

    return follow_up

def main_states():
    path_csv = "res/results/" + str(config.TEST_RELATION) + ".csv"
    global start
    start = 0
    if not os.path.isfile(path_csv):
        with open(path_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["TEST_CASE_NUMBER", "TEST CASE", "FOLLOW UP", "TEST CASE TEXT", "TEST CASE MULTI", "FOLLOW UP TEXT", "FOLLOW UP MULTI", "COMPARE TEXT", "COMPARE MULTI"])

        #with open(path_csv, "w", newline="", encoding="utf-8") as file:
        #    writer = csv.writer(file, delimiter=";")
        #    writer.writerow(["TEST_CASE_NUMBER", "TEST CASE1", "TEST CASE2", "FOLLOW UP", "TEST CASE TEXT1", "TEST CASE MULTI1", "TEST CASE TEXT2", "TEST CASE MULTI2", "FOLLOW UP TEXT", "FOLLOW UP MULTI", "COMPARE TEXT1", "COMPARE MULTI1", "COMPARE TEXT2", "COMPARE MULTI2", "COMPARE COMBO", "COMPARE COMBO"])


    else:
        start = get_last_value(path_csv)

    file_path = "res/corpus.csv"

    with open(file_path, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        i = 0
        for row in reader:
            participant = row[3]
            question = row[4]
            if participant == "U":
                i += 1
                if i > start:
                    config.TEST_CASE_NUMBER = i

                    print(i.__str__() + ";" + question + ";")
                    #get_dialogue_answer_states(question)

                    # 1: filler words
                    # test_same(question, get_metamorphed_questions(question, 1), domain=False)

                    # 2: sentence inversion / anastrophe
                    # test_same(question, get_metamorphed_questions(i, 3), domain=False)

                    # 3: active passive sentence
                    # test_same(question, get_metamorphed_questions(i, 5), domain=False)

                    # 4: synonyms
                    # test_same(question, get_metamorphed_questions(question, 7), domain=False)
                    # 5: mistakes
                    # test_same(question, get_metamorphed_questions(question, 8), domain=False)

                    # 6: multiple questions
                    # test_multiple_questions(question, i, domain=False)

    with open("res/corpus7.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            config.TEST_CASE_NUMBER = row[0]
            question = row[1]
            follow_up = "Explain to me what this is"
            ids = row[2]
            follow_up = create_follow(follow_up, ids)
            test_same(question, [follow_up], ids = [ids], domain = False)


def check_mr_res():
    test_cases = 0
    total = 0
    errors = 0
    multi_errors = 0
    number = 0
    with open("res/results/7.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            if row[0].isdigit() and number != row[0]:
                test_cases += 1
            number = row[0]
            question = row[1]
            follow_up = row[2]
            test_case_text = row[3]
            follow_text = row[5]
            compare_text = row[7]
            compare_multi = row[8]

            #test_case_text = row[4]
            #follow_text = row[8]
            #compare_text = row[14]
            #compare_multi = row[15]
            if number.isdigit():
                #if follow_up != "[NOT TRANSFORMABLE]":
                    #if not("Potresti essere" in follow_text or "Potresti essere" in test_case_text):
                        total += 1
                        if compare_text == "False":
                            errors += 1
                        if compare_multi == "False":
                            multi_errors += 1

    print(test_cases)
    print(errors)
    print(multi_errors)
    print(total)
    print(errors / total)
    print(multi_errors / total)

if __name__ == "__main__":
    #main()
    #main_states()

    #test_mr("res/corpus8.csv", "rules_9a", 91, "C")
    #test_mr("res/corpus8.csv", "rules_9b", 92, "C")

    #test_mr("res/corpus8.csv", "rules_10a", 101, "S")
    #test_mr("res/corpus8.csv", "rules_10b", 102, "S")

    #test_mr("res/corpus8.csv", "rules_11", 11, "C")

    #test_mr("res/corpus8.csv", "rules_12", 12, "V")

    #test_mr("res/corpus8.csv", "rules_13a", 131, "E")
    #test_mr("res/corpus8.csv", "rules_13b", 132, "E")
    
    check_mr_res()