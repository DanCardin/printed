from sqlalchemy_model_factory import declarative

from printed.schema import Print


@declarative
class ModelFactory:
    def print(
        self,
        name: str = "foo",
    ):
        return Print(
            name=name,
        )
