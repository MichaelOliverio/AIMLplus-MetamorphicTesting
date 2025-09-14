class Config:
    # Percorsi modelli
    FRAME_MODEL_PATH = "models/frame_model.pkl"
    EMBED_MODEL_PATH = "models/embed_model/"
    LEMMATIZER_MODEL = "spacy_model"

    # Parametri per NLU
    EMBEDDING_THRESHOLD = 0.8

    # Logging
    LOG_FILE = "logs/daaiml.log"
    LOG_LEVEL = "INFO"
