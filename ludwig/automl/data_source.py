from abc import ABC, abstractmethod

from typing import List

from ludwig.automl.utils import avg_num_tokens


class DataSource(ABC):
    @abstractmethod
    @property
    def columns(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def get_dtype(self, column) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_distinct_values(self, column) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_nonnull_values(self, column) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_avg_num_tokens(self, column) -> int:
        raise NotImplementedError()

    @abstractmethod
    def is_string_type(self, dtype) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()


class DataframeSource(DataSource):
    def __init__(self, df):
        self.df = df

    @property
    def columns(self) -> List[str]:
        return self.df.columns

    def get_dtype(self, column) -> str:
        return self.df[column].dtype.name

    def get_distinct_values(self, column) -> int:
        return len(self.df[column].unique())

    def get_nonnull_values(self, column) -> int:
        return len(self.df[column].notnull())

    def get_avg_num_tokens(self, column) -> int:
        return avg_num_tokens(self.df[column])

    def is_string_type(self, dtype) -> bool:
        return dtype in ['str', 'string', 'object']

    def __len__(self) -> int:
        return len(self.df)
