# Guida all'installazione e configurazione

## 1. Configurazione file `.env`
Nella cartella `DS`:
- Copiare il file `.env.example`
- Rinominarlo in `.env`
- Aggiungere la stessa chiave di Hugging Face sia a:
  - `HUGGINGFACE_API_KEY`
  - `HUGGINGFACE_FINE_TUNING_LLM_KEY`

---

## 2. Installazione librerie
Le librerie necessarie sono elencate nel file `requirements.txt`.

Per installarle:
```bash
pip install -r requirements.txt
````

### Consiglio: creare un ambiente virtuale

Per evitare conflitti con altre librerie, si consiglia di lavorare in un ambiente virtuale.

* Su **Windows**:

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

* Su **Linux/Mac**:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

---

## 3. Problemi comuni con PyTorch

Alla prima esecuzione di:

```bash
pip install -r requirements.txt
```

potrebbero verificarsi errori legati a **PyTorch** (specialmente per il supporto GPU).

In questo caso, installare manualmente la versione corretta di PyTorch (nel mio caso la 12.1, ho una RTX 4050):

```bash
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

Dopo aver installato correttamente PyTorch, rilanciare:

```bash
pip install -r requirements.txt
```

---

Esecuzione del servizio:
1. eseguire il comando "cd DS" da terminale
2. eseguire il comando "uvicorn api:app --reload"