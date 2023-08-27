import logging
from dataclasses import dataclass, field

import tidi

logging.basicConfig(level=logging.INFO)


class NumRepeats(int):
    ...


tidi.register(NumRepeats(10))


@dataclass
class AlgorithmConfig:
    atol: float
    num_repeats: NumRepeats = field(default_factory=tidi.field_factory(NumRepeats))


class Algorithm:
    @tidi.inject
    def __init__(self, name: str, alg_config: tidi.Injected[AlgorithmConfig] = tidi.UNSET):
        self.name = name
        self.atol = alg_config.atol
        self.num_repeats = alg_config.num_repeats

    def __call__(self, feature: float) -> float:
        return feature * self.atol * self.num_repeats


def configure_algorithm():
    atol = float(input("enter aboslute tolerance: "))
    algorithm_config = AlgorithmConfig(atol=atol)
    tidi.register(algorithm_config)
    logging.info("algorithm configured ✅")


def build_model():
    name = input("enter model name: ")
    model = Algorithm(name)
    tidi.register(model)
    logging.info("model built ✅")


@tidi.inject
def run_model(model: tidi.Injected[Algorithm] = tidi.UNSET):
    feature = float(input("enter input value: "))
    logging.info('algorithm "%s" has output = %.4f 😎', model.name, model(feature))


def main():
    configure_algorithm()
    build_model()
    run_model()


if __name__ == "__main__":
    main()
