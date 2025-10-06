import csv

import requests
import json
from collections import Counter
import time

import config


def get_dialogue_answer(question, n = 3):
    url = f"http://localhost:3000/esempio{n}.html"

    payload = {
        "query": question
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    #print("Answer JSON:", response.json())

    return response.json()["answer"], (response.json()["image_link"], response.json()["id_elements"], response.json()["style_names"])


def get_dialogue_answer_states(question, ids = None, file_name = config.FILE_NAME):
    response = ""

    for tentativo in range(1, 6):
        try:
            url = "http://127.0.0.1:8000/chat"

            payload = {
                "user_input": question,
                "query": ids,
                "file_name": file_name
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)

            print("\n________________________________________________________")
            print(question)
            print(response.json()["response"])
            print(response.json()["svg_elements"])

            break

        except (requests.exceptions.JSONDecodeError, ValueError):
            print(f"Tentativo {tentativo} fallito: risposta non valida dal server.")

        except requests.exceptions.RequestException as e:
            print(f"Tentativo {tentativo} fallito: {e}")

        except Exception as e:  # fallback
            print(f"Tentativo {tentativo}: errore inatteso → {e}")

        if tentativo < 6:
            time.sleep(5)


    follow_up_answers = []
    for svg_element in response.json()["svg_elements"]:
        style_value = svg_element["style_value"]
        symbol = svg_element["symbol"]
        style_name = svg_element["style_name"]
        follow_up_answers.append((symbol, style_value, style_name))

    return response.json()["response"], follow_up_answers


def compare_answers(test_case_answer, follow_up_answers, question, follow_up_questions, expect):
    test_results = []

    for follow_up, follow_up_question in zip(follow_up_answers, follow_up_questions):
        text_test = test_case_answer[0] == follow_up[0]

        multimodal_test = Counter(test_case_answer[1]) == Counter(follow_up[1])

        if expect == "same":
            test_results.append((text_test, multimodal_test))
        else:
            test_results.append((not text_test, not multimodal_test))
        print("{:<8} {:<8} {:<80}".format(text_test, multimodal_test, " / " if test_case_answer[0] == follow_up[0] else follow_up[0]))

        with open("res/results/" + str(config.TEST_RELATION) + ".csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([str(config.TEST_CASE_NUMBER), question, follow_up_question, test_case_answer[0], test_case_answer[1], follow_up[0], follow_up[1], text_test, multimodal_test])


    return test_results


def compare_multiple(test_case1, test_case2, follow_up, tc1, tc2, foll):
    text_test1 = test_case1[0] == follow_up[0]
    multimodal_test1 = Counter(test_case1[1]) == Counter(follow_up[1])
    # multimodal_test1 = (test_case1[1][0] == follow_up[1][0]) and (test_case1[1][1] == follow_up[1][1]) and (test_case1[1][2] == follow_up[1][2])

    text_test2 = test_case2[0] == follow_up[0]
    multimodal_test2 = Counter(test_case2[1]) == Counter(follow_up[1])
    # multimodal_test2 = (test_case2[1][0] == follow_up[1][0]) and (test_case2[1][1] == follow_up[1][1]) and (test_case2[1][2] == follow_up[1][2])

    text_test_conc = test_case1[0] + " " + test_case2[0] == follow_up[0]
    multimodal_test_conc = Counter(test_case1[1] + test_case2[1]) == Counter(follow_up[1])

    print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format(text_test1, multimodal_test1, text_test2, multimodal_test2, text_test_conc, multimodal_test_conc))


    # "TEST_CASE_NUMBER", "TEST CASE1", "TEST CASE2", "FOLLOW UP", "TEST CASE TEXT1", "TEST CASE MULTI1", "TEST CASE TEXT2", "TEST CASE MULTI2", "FOLLOW UP TEXT", "FOLLOW UP MULTI", "COMPARE TEXT1", "COMPARE MULTI1", "COMPARE TEXT2", "COMPARE MULTI2", "COMPARE COMBO", "COMPARE COMBO"
    with open("res/results/" + str(config.TEST_RELATION) + ".csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([str(config.TEST_CASE_NUMBER), tc1, tc2, foll, test_case1[0], test_case1[1], test_case2[0], test_case2[1], follow_up[0], follow_up[1], text_test1, multimodal_test1, text_test2, multimodal_test2, text_test_conc, multimodal_test_conc])


def normalize(s: str) -> str:
    # tutto minuscolo
    s = s.lower()
    # togli spazi a inizio e fine
    s = s.strip()
    # tieni solo lettere e spazi
    s = ''.join(ch for ch in s if ch.isalpha() or ch.isspace())
    # sostituisci più spazi consecutivi con uno solo
    s = ' '.join(s.split())
    return s


def test_same(question, metamorphed_questions, n = 3, domain = True, ids=None, file_name = "automa2"):

    print(question)
    if not (any(metamorphed_questions) and any(any(sub) if isinstance(sub, list) else True for sub in metamorphed_questions)):
        return

    print("\n\ntest case: " + question)
    for follow_up in metamorphed_questions:
        print("follow_up: " + follow_up)


    if domain:
        test_case_answer = get_dialogue_answer(question, n)
    else:
        test_case_answer = get_dialogue_answer_states(question, ids)

    print("test case answer: ", test_case_answer[0])
    # print(f"Metamorphed questions: {metamorphed_questions}")

    print("{:<8} {:<8} {:<80}".format("text", "multi", "answer"))
    print("-" * 30)

    follow_up_answers = []
    for meta in metamorphed_questions:
        if domain:
            follow_up = get_dialogue_answer(meta, n)
        else:
            follow_up = get_dialogue_answer_states(meta, ids, file_name)

        follow_up_answers.append(follow_up)


    res = compare_answers(test_case_answer, follow_up_answers, question, metamorphed_questions, expect = "same")

    #print("testcase: " + question + "\n")
    #print(metamorphed_questions)
    #print(res)