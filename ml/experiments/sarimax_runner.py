from ml.training.walkforward_training import WalkForwardTraining
from ml.models.sarimax_model import SARIMAXModel


def factory():
    return SARIMAXModel()


if __name__ == "__main__":

    trainer = WalkForwardTraining(
        model_factory=factory,
        model_name="sarimax"
    )

    trainer.run()