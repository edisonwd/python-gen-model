from abc import ABC, abstractmethod


class AbstractPrintModel(ABC):
    """
    Abstract class for all print models.
    """

    @abstractmethod
    def model_type(self):
        pass

    @abstractmethod
    def print_header(self, **kwargs):
        pass

    @abstractmethod
    def print_model(self, **kwargs):
        pass

    @classmethod
    def get_all_print_models(cls):
        """
        Returns a list of all print models.
        """
        subclasses = set(cls.__subclasses__())
        sub_dict = {}
        for subclass in subclasses:
            sub_instance = subclass()
            sub_dict[sub_instance.model_type()] = sub_instance
        return sub_dict
