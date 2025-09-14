from abc import ABC, abstractmethod

class BaseFrameExtractorHandler(ABC):
    """Classe base per gestire i modelli di generazione."""
    
    @abstractmethod
    def generate_output(self, text: str) -> str:
        """Metodo astratto per generare output dato un testo di input."""
        pass
