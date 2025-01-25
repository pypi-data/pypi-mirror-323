from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterator, Tuple



class DataSet(ABC):

    @abstractmethod
    def match(data: Any) -> bool: ...

    @abstractmethod
    def get_aacgm_data(self) -> Iterator[Tuple[datetime, float, float, float]]: ...

    @abstractmethod
    def convert(self): ...

    @abstractmethod
    def close(self): ...