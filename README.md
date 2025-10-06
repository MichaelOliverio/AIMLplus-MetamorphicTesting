# Installation guide and configuration

## 1. Configuration file `.env`
In the folder `DS`:
- Copy the file `.env.example`
- Rename it into `.env`
- Add the same key of Hugging Face both to:
  - `HUGGINGFACE_API_KEY`
  - `HUGGINGFACE_FINE_TUNING_LLM_KEY`

---

## 2. Installing libs
All the necessaries libs are listed in `requirements.txt`.

To install them:
```bash
pip install -r requirements.txt
````

### Tip: create a virtual enviroment

To avoid conflicts it is suggested to work in a virtual enviroment

*  **Windows**:

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

*  **Linux/Mac**:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

---

## 3. PyTorch common problems

At the first execution of:

```bash
pip install -r requirements.txt
```

there could be some issues with **PyTorch** (expecially to support GPU).

In this case, manually install the right version of PyTorch (in my case the 12.1, I'm using a RTX 4050):

```bash
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

After having installed PyTorch correctly, re-execute:

```bash
pip install -r requirements.txt
```

---

To execute the service:
1. From terminal: "cd DS"
2. Then execute command "uvicorn api:app --reload"

---

## 4. Testing tools

Inside the folder "SvgTesting" it is possible to find all the testing tools created to test the system and all the corpuses