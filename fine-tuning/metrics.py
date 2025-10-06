import os
import ast
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import precision_score, recall_score, f1_score
import re

FALLBACK_DICT = {'ar': 'Nan', 'da': 'Nan', 'in': 'Nan', 'sn': [], 'sv': []}

def evaluate_predictions(file_path, save_path=None):
    df = pd.read_csv(file_path)

    y_true_cols = {f: [] for f in ["ar","da","in","sn","sv"]}
    y_pred_cols = {f: [] for f in ["ar","da","in","sn","sv"]}

    for _, row in df.iterrows():
        prediction = sanitize_dict(row['prediction'])
        actual = sanitize_dict(row['actual'])

        # accumula i valori per ogni colonna
        y_true_cols["ar"].append(actual["ar"])
        y_pred_cols["ar"].append(prediction["ar"])
        y_true_cols["da"].append(actual["da"])
        y_pred_cols["da"].append(prediction["da"])
        y_true_cols["in"].append(actual["in"])
        y_pred_cols["in"].append(prediction["in"])
        y_true_cols["sn"].append(safe_list(actual["sn"]))
        y_pred_cols["sn"].append(safe_list(prediction["sn"]))
        y_true_cols["sv"].append(safe_list(actual["sv"]))
        y_pred_cols["sv"].append(safe_list(prediction["sv"]))

    # --- METRICHE PER COLONNA ---
    results = {}
    for col in ["ar","da","in"]:
        results[col] = compute_metrics(y_true_cols[col], y_pred_cols[col], multilabel=False)

    for col in ["sn","sv"]:
        results[col] = compute_metrics(y_true_cols[col], y_pred_cols[col], multilabel=True)

    results_df = pd.DataFrame(results, index=["Precision","Recall","F1"]).T
    print("\n=== RISULTATI FINALI (per colonna) ===")
    print(results_df)

    # --- F1 MEDIO (stessa importanza per colonna) ---
    f1_avg = results_df["F1"].mean()
    print(f"\n=== F1 MEDIO (uguale peso per colonna) === {round(f1_avg,3)}")

    # --- SALVATAGGIO ---
    if save_path:
        results_df.loc["TOTAL"] = ["-", "-", round(f1_avg,3)]
        if save_path.endswith(".csv"):
            results_df.to_csv(save_path)
        elif save_path.endswith(".xlsx"):
            results_df.to_excel(save_path)
        else:
            print(f"Formato non supportato per il salvataggio: {save_path}. Usa .csv o .xlsx")
        print(f"\nRisultati salvati in {save_path}")


def sanitize_dict(raw_value):
    """
    Pulisce e normalizza la stringa di un dizionario (prediction/actual)
    in un dizionario con la struttura standardizzata.
    """
    if raw_value is None or str(raw_value).strip() == "":
        return FALLBACK_DICT.copy()
    
    # Step 1: prova a usare ast.literal_eval in sicurezza
    parsed = None
    try:
        parsed = ast.literal_eval(raw_value)
        if not isinstance(parsed, dict):
            parsed = None
    except Exception:
        parsed = None
    
    # Step 2: se parsing fallisce, prova a estrarre pattern tipo 'key': 'value'
    if parsed is None:
        parsed = {}
        matches = re.findall(r"'(\w+)'\s*:\s*'([^']*)'", raw_value)
        for k, v in matches:
            parsed[k] = v
    
    # Step 3: costruisci il risultato normalizzato
    result = FALLBACK_DICT.copy()
    
    # campi stringa
    for key in ["ar", "da", "in"]:
        if key in parsed and isinstance(parsed[key], str):
            result[key] = parsed[key]
    
    # campi lista
    for key in ["sn", "sv"]:
        if key in parsed:
            val = parsed[key]
            if isinstance(val, str):
                try:
                    evaluated = ast.literal_eval(val)
                    if isinstance(evaluated, list):
                        result[key] = evaluated
                except Exception:
                    result[key] = []
            elif isinstance(val, list):
                result[key] = val
    
    return result

def safe_list(val):
    """Garantisce che il campo sia una lista di stringhe (anche tuple diventano stringhe)."""
    if not isinstance(val, list):
        return []
    return [str(x) for x in val]


def compute_metrics(y_true, y_pred, multilabel=False):
    """Calcola precision, recall, f1 per colonne singole o multilabel."""
    if multilabel:
        mlb = MultiLabelBinarizer()
        y_true_bin = mlb.fit_transform(y_true)
        y_pred_bin = mlb.transform(y_pred)
    else:
        y_true_bin, y_pred_bin = y_true, y_pred
    
    p = precision_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
    r = recall_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
    f1 = f1_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
    return round(p,3), round(r,3), round(f1,3)


# open file in results
if __name__ == "__main__":
    results_file = "fine-tuning/results/"
    for file in os.listdir(results_file):
        if file.endswith(".csv"):
            print(f"\n--- Valutazione file: {file} ---")
            evaluate_predictions(
                os.path.join(results_file, file),
                save_path=os.path.join(results_file, f"eval/eval_{file}")
            )
