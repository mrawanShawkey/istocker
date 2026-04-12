from ml.training.walkforward_training import WalkForwardTraining
from ml.models.xgboost_model import XGBoostModel


def factory():
    return XGBoostModel()


if __name__ == "__main__":

    trainer = WalkForwardTraining(
        model_factory=factory,
        model_name="xgboost"
    )

    trainer.run()