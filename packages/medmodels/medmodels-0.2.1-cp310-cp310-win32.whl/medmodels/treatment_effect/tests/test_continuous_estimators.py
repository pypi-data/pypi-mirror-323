"""Tests for the TreatmentEffect class in the treatment_effect module."""

from __future__ import annotations

import unittest
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import pandas as pd
import pytest

from medmodels import MedRecord
from medmodels.treatment_effect.continuous_estimators import (
    average_treatment_effect,
    cohens_d,
    hedges_g,
)

if TYPE_CHECKING:
    from medmodels.medrecord.types import NodeIndex


def create_patients(patient_list: List[NodeIndex]) -> pd.DataFrame:
    """Creates a patients dataframe.

    Returns:
        pd.DataFrame: A patients dataframe.
    """
    patients = pd.DataFrame(
        {
            "index": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
            "age": [20, 30, 40, 30, 40, 50, 60, 70, 80],
            "gender": [
                "male",
                "female",
                "male",
                "female",
                "male",
                "female",
                "male",
                "female",
                "male",
            ],
        }
    )

    return patients.loc[patients["index"].isin(patient_list)]


def create_diagnoses() -> pd.DataFrame:
    """Creates a diagnoses dataframe.

    Returns:
        pd.DataFrame: A diagnoses dataframe.
    """
    return pd.DataFrame(
        {
            "index": ["D1"],
            "name": ["Stroke"],
        }
    )


def create_prescriptions() -> pd.DataFrame:
    """Creates a prescriptions dataframe.

    Returns:
        pd.DataFrame: A prescriptions dataframe.
    """
    return pd.DataFrame(
        {
            "index": ["M1", "M2"],
            "name": ["Rivaroxaban", "Warfarin"],
        }
    )


def create_edges1(patient_list: List[NodeIndex]) -> pd.DataFrame:
    """Creates an edges dataframe.

    Returns:
        pd.DataFrame: An edges dataframe.
    """
    edges = pd.DataFrame(
        {
            "source": [
                "M2",
                "M1",
                "M2",
                "M1",
                "M2",
                "M1",
                "M2",
            ],
            "target": [
                "P1",
                "P2",
                "P2",
                "P3",
                "P5",
                "P6",
                "P9",
            ],
            "time": [
                datetime(1999, 10, 15),
                datetime(2000, 1, 1),
                datetime(1999, 12, 15),
                datetime(2000, 1, 1),
                datetime(2000, 1, 1),
                datetime(2000, 1, 1),
                datetime(2000, 1, 1),
            ],
        }
    )
    return edges.loc[edges["target"].isin(patient_list)]


def create_edges2(patient_list: List[NodeIndex]) -> pd.DataFrame:
    """Creates an edges dataframe with attribute "intensity".

    Returns:
        pd.DataFrame: An edges dataframe.
    """
    edges = pd.DataFrame(
        {
            "source": [
                "D1",
                "D1",
                "D1",
                "D1",
                "D1",
                "D1",
            ],
            "target": [
                "P1",
                "P2",
                "P3",
                "P3",
                "P4",
                "P7",
            ],
            "time": [
                datetime.strptime("2000-01-01", "%Y-%m-%d"),
                datetime.strptime("2000-07-01", "%Y-%m-%d"),
                datetime.strptime("1999-12-15", "%Y-%m-%d"),
                datetime.strptime("2000-01-05", "%Y-%m-%d"),
                datetime.strptime("2000-01-01", "%Y-%m-%d"),
                datetime.strptime("2000-01-01", "%Y-%m-%d"),
            ],
            "intensity": [
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
            ],
            "type": [
                "A",
                "B",
                "A",
                "B",
                "A",
                "A",
            ],
        }
    )
    return edges.loc[edges["target"].isin(patient_list)]


def create_medrecord(
    patient_list: Optional[List[NodeIndex]] = None,
) -> MedRecord:
    """Creates a MedRecord object.

    Returns:
        MedRecord: A MedRecord object.
    """
    if patient_list is None:
        patient_list = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]
    patients = create_patients(patient_list=patient_list)
    diagnoses = create_diagnoses()
    prescriptions = create_prescriptions()
    edges1 = create_edges1(patient_list=patient_list)
    edges2 = create_edges2(patient_list=patient_list)
    medrecord = MedRecord.from_pandas(
        nodes=[(patients, "index"), (diagnoses, "index"), (prescriptions, "index")],
        edges=[(edges1, "source", "target")],
    )
    medrecord.add_group(group="patients", nodes=patients["index"].to_list())
    medrecord.add_group(
        "Stroke",
        ["D1"],
    )
    medrecord.add_group(
        "Rivaroxaban",
        ["M1"],
    )
    medrecord.add_group(
        "Warfarin",
        ["M2"],
    )
    medrecord.add_edges((edges2, "source", "target"))
    return medrecord


class TestContinuousEstimators(unittest.TestCase):
    """Class to test the continuous estimators."""

    def setUp(self) -> None:
        self.medrecord = create_medrecord()
        self.outcome_group = "Stroke"
        self.time_attribute = "time"

    def test_average_treatment_effect(self) -> None:
        ate_result = average_treatment_effect(
            self.medrecord,
            treatment_outcome_true_set=set({"P2", "P3"}),
            control_outcome_true_set=set({"P1", "P4", "P7"}),
            outcome_group=self.outcome_group,
            outcome_variable="intensity",
            reference="last",
            time_attribute=self.time_attribute,
        )
        assert ate_result == pytest.approx(-0.1)

        ate_result = average_treatment_effect(
            self.medrecord,
            treatment_outcome_true_set=set({"P2", "P3"}),
            control_outcome_true_set=set({"P1", "P4", "P7"}),
            outcome_group=self.outcome_group,
            outcome_variable="intensity",
            reference="first",
            time_attribute=self.time_attribute,
        )
        assert ate_result == pytest.approx(-0.15)

    def test_invalid_treatment_effect(self) -> None:
        with pytest.raises(ValueError, match="Outcome variable must be numeric"):
            average_treatment_effect(
                self.medrecord,
                treatment_outcome_true_set=set({"P2", "P3"}),
                control_outcome_true_set=set({"P1", "P4", "P7"}),
                outcome_group=self.outcome_group,
                outcome_variable="type",
                reference="last",
                time_attribute=self.time_attribute,
            )

    def test_cohens_d(self) -> None:
        cohens_d_result = cohens_d(
            self.medrecord,
            treatment_outcome_true_set=set({"P2", "P3"}),
            control_outcome_true_set=set({"P1", "P4", "P7"}),
            outcome_group=self.outcome_group,
            outcome_variable="intensity",
            reference="last",
            time_attribute=self.time_attribute,
        )
        assert cohens_d_result == pytest.approx(-0.59, 2)

        cohens_d_result = cohens_d(
            self.medrecord,
            treatment_outcome_true_set=set({"P2", "P3"}),
            control_outcome_true_set=set({"P1", "P4", "P7"}),
            outcome_group=self.outcome_group,
            outcome_variable="intensity",
            reference="first",
            time_attribute=self.time_attribute,
        )
        assert cohens_d_result == pytest.approx(-0.96, 2)

    def test_invalid_cohens_d(self) -> None:
        with pytest.raises(ValueError, match="Outcome variable must be numeric"):
            cohens_d(
                self.medrecord,
                treatment_outcome_true_set=set({"P2", "P3"}),
                control_outcome_true_set=set({"P1", "P4", "P7"}),
                outcome_group=self.outcome_group,
                outcome_variable="type",
                reference="last",
                time_attribute=self.time_attribute,
            )

    def test_hedges_g(self) -> None:
        hedges_g_result = hedges_g(
            self.medrecord,
            treatment_outcome_true_set=set({"P2", "P3"}),
            control_outcome_true_set=set({"P1", "P4", "P7"}),
            outcome_group=self.outcome_group,
            outcome_variable="intensity",
            reference="last",
            time_attribute=self.time_attribute,
        )

        assert hedges_g_result == pytest.approx(-0.59, 2)


if __name__ == "__main__":
    run_test = unittest.TestLoader().loadTestsFromTestCase(TestContinuousEstimators)
    unittest.TextTestRunner(verbosity=2).run(run_test)
