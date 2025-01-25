import unittest

import numpy as np
import polars as pl
import pytest
from sklearn.datasets import load_iris

from medmodels.treatment_effect.matching.algorithms import propensity_score as ps


class TestPropensityScore(unittest.TestCase):
    def test_calculate_propensity(self) -> None:
        x, y = load_iris(return_X_y=True)

        # Set random state by each propensity estimator:
        hyperparameters = {"random_state": 1}
        hyperparameters_logit = {"random_state": 1, "max_iter": 200}
        x = np.array(x)
        y = np.array(y)

        # Logistic Regression model:
        result_1, result_2 = ps.calculate_propensity(
            x,
            y,
            np.array([x[0, :]]),
            np.array([x[1, :]]),
            hyperparameters=hyperparameters_logit,
        )
        assert result_1[0] == pytest.approx(1.4e-08, 9)
        assert result_2[0] == pytest.approx(3e-08, 9)

        # Decision Tree Classifier model:
        result_1, result_2 = ps.calculate_propensity(
            x,
            y,
            np.array([x[0, :]]),
            np.array([x[1, :]]),
            model="dec_tree",
            hyperparameters=hyperparameters,
        )
        assert result_1[0] == pytest.approx(0, 2)
        assert result_2[0] == pytest.approx(0, 2)

        # Random Forest Classifier model:
        result_1, result_2 = ps.calculate_propensity(
            x,
            y,
            np.array([x[0, :]]),
            np.array([x[1, :]]),
            model="forest",
            hyperparameters=hyperparameters,
        )
        assert result_1[0] == pytest.approx(0, 2)
        assert result_2[0] == pytest.approx(0, 2)

    def test_run_propensity_score(self) -> None:
        # Set random state by each propensity estimator:
        hyperparameters = {"random_state": 1}
        hyperparameters_logit = {"random_state": 1, "max_iter": 200}

        ###########################################
        # 1D example
        control_set = pl.DataFrame({"a": [1, 5, 1, 3]})
        treated_set = pl.DataFrame({"a": [1, 4]})

        # logit model
        expected_logit = pl.DataFrame({"a": [1.0, 3.0]})
        result_logit = ps.run_propensity_score(
            treated_set, control_set, hyperparameters=hyperparameters_logit
        )
        assert result_logit.equals(expected_logit)

        # dec_tree metric
        expected_logit = pl.DataFrame({"a": [1.0, 1.0]})
        result_logit = ps.run_propensity_score(
            treated_set, control_set, model="dec_tree", hyperparameters=hyperparameters
        )
        assert result_logit.equals(expected_logit)

        # forest model
        expected_logit = pl.DataFrame({"a": [1.0, 1.0]})
        result_logit = ps.run_propensity_score(
            treated_set, control_set, model="forest", hyperparameters=hyperparameters
        )
        assert result_logit.equals(expected_logit)

        ###########################################
        # 3D example with covariates
        cols = ["a", "b", "c"]
        array = np.array([[1, 3, 5], [5, 2, 1], [1, 4, 10]])
        control_set = pl.DataFrame(array, schema=cols)
        treated_set = pl.DataFrame({"a": [1], "b": [4], "c": [2]})
        covs = ["a", "c"]

        # logit model
        expected_logit = pl.DataFrame({"a": [1.0], "b": [3.0], "c": [5.0]})
        result_logit = ps.run_propensity_score(
            treated_set,
            control_set,
            covariates=covs,
            hyperparameters=hyperparameters_logit,
        )
        assert result_logit.equals(expected_logit)

        # dec_tree model
        expected_logit = pl.DataFrame({"a": [1.0], "b": [3.0], "c": [5.0]})
        result_logit = ps.run_propensity_score(
            treated_set,
            control_set,
            model="dec_tree",
            covariates=covs,
            hyperparameters=hyperparameters,
        )
        assert result_logit.equals(expected_logit)

        # forest model
        expected_logit = pl.DataFrame({"a": [1.0], "b": [3.0], "c": [5.0]})
        result_logit = ps.run_propensity_score(
            treated_set,
            control_set,
            model="forest",
            covariates=covs,
            hyperparameters=hyperparameters,
        )
        assert result_logit.equals(expected_logit)

        # using 2 nearest neighbors
        expected_logit = pl.DataFrame(
            {
                "a": [1.0, 5.0],
                "b": [3.0, 2.0],
                "c": [5.0, 1.0],
            }
        )
        result_logit = ps.run_propensity_score(
            treated_set,
            control_set,
            number_of_neighbors=2,
        )
        assert result_logit.equals(expected_logit)


if __name__ == "__main__":
    run_test = unittest.TestLoader().loadTestsFromTestCase(TestPropensityScore)
    unittest.TextTestRunner(verbosity=2).run(run_test)
