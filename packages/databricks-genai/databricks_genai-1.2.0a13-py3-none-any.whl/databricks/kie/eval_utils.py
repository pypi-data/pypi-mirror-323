"""Eval Utils for Tiles"""
from enum import Enum
from typing import Union

from databricks.agents.evals import judges
from mlflow.evaluation import Assessment

from databricks.kie.text_utils import fuzzy_string_match, normalize_text  # pylint: disable=ungrouped-imports

PrimitiveTypes = Union[int, float, str, bool, Enum]


# TODO: Needs to match TaskSpec definition of a metric
def exact_match(query: str, ground_truth: PrimitiveTypes, prediction: PrimitiveTypes) -> Assessment:
    del query  # unused
    result = ground_truth == prediction

    if result:
        rationale = 'Values matched exactly'
    else:
        rationale = 'Values did not match exactly'

    return Assessment(name='exact_match', value=result, rationale=rationale)


def normalized_match(query: str, ground_truth: PrimitiveTypes, prediction: PrimitiveTypes) -> Assessment:
    if not isinstance(ground_truth, str) or not isinstance(prediction, str):
        result = exact_match(query, ground_truth, prediction)
    else:
        gt_normalized = normalize_text(ground_truth)
        pred_normalized = normalize_text(prediction)
        result = exact_match(query, gt_normalized, pred_normalized)

    if result.value:
        rationale = 'Normalized values matched'
    else:
        rationale = 'Normalized values did not match'

    return Assessment(name='normalized_match', value=result.value, rationale=rationale)


def fuzzy_match(query: str, ground_truth: PrimitiveTypes, prediction: PrimitiveTypes) -> Assessment:
    if not isinstance(ground_truth, str) or not isinstance(prediction, str):
        result = exact_match(query, ground_truth, prediction).value
    else:
        result = fuzzy_string_match(ground_truth, prediction)

    if result:
        rationale = 'Values approximately matched'
    else:
        rationale = 'Values did not approximately match'
    return Assessment(name='fuzzy_match', value=result, rationale=rationale)


# TODO: Possibly need retries and robustness here
def correctness(query: str, ground_truth: PrimitiveTypes, prediction: PrimitiveTypes) -> Assessment:
    if not isinstance(ground_truth, str) or not isinstance(prediction, str):
        return exact_match(query, ground_truth, prediction)

    # TODO: I think this supports guidelines now and should be updated to use that
    correctness_result = judges.correctness(request=query, response=prediction, expected_response=ground_truth)

    # Correctness judge does not return lists
    assert isinstance(correctness_result, Assessment)

    if correctness_result.error_code is not None:
        return fuzzy_match(query, ground_truth, prediction)

    bool_value = correctness_result.value == 'yes'

    remade_result = Assessment(
        name='correctness_judge',
        value=bool_value,
        rationale=correctness_result.rationale,
    )
    return remade_result
