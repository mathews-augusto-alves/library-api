import json
import statistics
import time
from abc import ABC, abstractmethod
from collections import Counter
from typing import List, Dict

class StatisticCalculator:
    """Responsável por calcular métricas estatísticas básicas."""

    def __init__(self, data: List[float]):
        if not data:
            raise ValueError("A lista de dados não pode estar vazia.")
        self.data = data

    # Cálculo de média
    def mean(self) -> float:
        return statistics.mean(self.data)

    # Cálculo de mediana
    def median(self) -> float:
        return statistics.median(self.data)

    # Cálculo de moda
    def mode(self) -> float:
        counter = Counter(self.data)
        return counter.most_common(1)[0][0]

    def all_metrics(self) -> Dict[str, float]:
        return {
            "media": self.mean(),
            "mediana": self.median(),
            "moda": self.mode()
        }

class Formatter(ABC):
    @abstractmethod
    def format(self, metrics: Dict[str, float]) -> str:
        pass

class ConsoleFormatter(Formatter):
    def format(self, metrics: Dict[str, float]) -> str:
        return (
            f"Média: {metrics['media']}\n"
            f"Mediana: {metrics['mediana']}\n"
            f"Moda: {metrics['moda']}"
        )

class JsonFormatter(Formatter):
    def format(self, metrics: Dict[str, float]) -> str:
        return json.dumps(metrics, ensure_ascii=False, indent=2)


# ---- Orquestrador ----
class DataProcessor:
    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    def process(self, data: List[float]) -> str:
        calculator = StatisticCalculator(data)
        metrics = calculator.all_metrics()
        return self.formatter.format(metrics)

if __name__ == "__main__":
    data = [5, 2, 2, 8, 5, 5, 9, 2]

    start = time.time()
    processor_console = DataProcessor(ConsoleFormatter())
    print(processor_console.process(data))

    processor_json = DataProcessor(JsonFormatter())
    print(processor_json.process(data))
    end = time.time()

    print("Tempo de execução:", round(end - start, 6), "s")
