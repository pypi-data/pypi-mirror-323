"""Module implementaion of entrypoint API for Text2Text."""

import functools
import random
import re
from datetime import datetime
from typing import Dict, List, Optional

import mlflow
import pandas as pd
import requests as request_lib
from databricks.agents.evals import judges, metric  # pylint: disable=ungrouped-imports
from mlflow import create_experiment, get_experiment_by_name, get_trace, start_run
from mlflow.evaluation import Assessment
from mlflow.models import infer_signature
from tqdm import tqdm

from databricks.kie.t2t_custom_model import CustomModel, ModelWrapper
from databricks.kie.t2t_instruction_analyzer import InstructionInfo, generate_instruction_info
from databricks.kie.t2t_metrics import create_classic_metrics
from databricks.kie.t2t_schema import SideBySideResult, T2TSystemParams, T2TSystemResult, Text2TextTaskSpec
from databricks.kie.t2t_utils import (INSTRUCTION_AND_INPUT_PROMPT_TEMPLATE, LLM_JUDGE_EVAL_PROMPT_TEMPLATE,
                                      generate_evaluation_criteria, validate_secret_exists)
from databricks.kie.task_spec import get_default_experiment_name_with_suffix
from databricks.model_training.api.utils import get_host_and_token_from_env
from databricks.model_training.mlflow_utils import get_mlflow_client
from databricks.model_training.version import __version__


class Text2TextRunner:
    """
    A class to manage the Text2Text model lifecycle, including training, evaluation, and deployment.

    Main API:
    - compile(): Optimizes prompt / model given provided hyperparameters.
    - update_system_param(): Updates the state of the runner with new instruction, evaluation criteria, or example data.
    - evaluate_models(): Evaluates all models in the runner.
    - visualize_models(): Visualizes model predictions for a subset of test data.
    - deploy_model(): Deploys a model to a production endpoint.
    """
    NUM_FEW_SHOTS = [0, 5]
    MIN_EVAL_DATA = 5
    MAX_EVAL_DATA = 100
    MAX_EXAMPLES_FOR_VISUALIZATION = 5
    DEFAULT_MODEL_ID = "gpt-4o-2024-08-06-text2text"
    MODEL_SELECTION = ["gpt-4o-2024-08-06-text2text", "gpt-4o-mini-2024-07-18-text2text"]
    MODEL_SELECTION_WITH_STRUCTURED_OUTPUT_SUPPORT = ["gpt-4o-2024-08-06-text2text", "gpt-4o-mini-2024-07-18-text2text"]
    INSTRUCTION_TEMPLATE = """
        INSTRUCTION: {optimized_instruction}
        OUTPUT FORMAT: {output_format}

        Given the following instruction and output format, provide response that follows the instruction and output format given the user input.
        User input will be provided below as part of the user message.  
    """

    def __init__(self, task_spec: Text2TextTaskSpec):
        """
        Initializes the Text2TextRunner with the provided parameters.

        Args:
            task_spec: Text2TextTaskSpec object containing the instruction, example data, and evaluation criteria
        """
        self.model_map: Dict[str, ModelWrapper] = {}
        self.test_data: List[Dict[str, str]] = []
        self.train_data: List[Dict[str, str]] = []
        self.instruction_info = None
        self.default_model: Optional[ModelWrapper] = None
        self.prev_task_spec: Optional[Text2TextTaskSpec] = None
        self.prev_params: Optional[T2TSystemParams] = None
        self.custom_metrics = []

        self.current_task_spec = task_spec
        self.current_params = task_spec.to_system_param()
        experiment_name = task_spec.experiment_name
        if not experiment_name:
            now = datetime.now()
            formatted_string = now.strftime("%Y_%m_%d_%H_%M_%S")
            experiment_name = get_default_experiment_name_with_suffix(f"t2t_{formatted_string}")
            print(f"Experiment name not provided. Creating new experiment: {experiment_name}")

        self.experiment_id = self._get_exp_id(experiment_name)
        self.mlflow_client = get_mlflow_client()

    def compile(self) -> T2TSystemResult:
        self._prepare_data()

        # get common data shared between previous state and new state.
        common_data = []
        prev_res = []
        if self.prev_params:
            print("Generating response for previous state for side by side comparison...")
            # generate req/response for previous state. This will be used to compare with current state.
            common_data = self.prev_params.get_sxs_data(self.current_params)[0:self.MAX_EXAMPLES_FOR_VISUALIZATION]
            assert self.default_model is not None
            prev_res = self._visualize_model(self.default_model, data=common_data)

        print("Compiling new system...")
        # Construct evaluation criteria. Infer from examples if not provided.
        if not self.current_params.evaluation_criteria:
            print("Inferring evaluation criteria automatically...")
            inferred_eval_criteria = generate_evaluation_criteria(self.current_params.instruction, self.train_data)
            self.current_params.evaluation_criteria = inferred_eval_criteria
            self.current_task_spec.evaluation_criteria = inferred_eval_criteria

        self._create_custom_metrics()

        # update models & system state to create new Text2Text models
        num_icl_examples = min(len(self.train_data), 10)
        self.instruction_info: Optional[InstructionInfo] = generate_instruction_info(
            self.train_data[:num_icl_examples], self.current_params.instruction,
            self.current_params.evaluation_criteria)

        self._create_classic_metrics()
        self.model_map = {}
        self._create_models()

        # generate response for common data for current state -- to be used for SxS comparison.
        current_res = []
        if prev_res:
            assert common_data and self.default_model is not None
            print("Getting new system response for side by side comparison..")
            current_res = self._visualize_model(self.default_model, data=common_data)

        return self._get_model_result(prev_res, current_res)

    def _get_judge_prompt(self, eval_criteria: str) -> str:
        return LLM_JUDGE_EVAL_PROMPT_TEMPLATE.format(
            eval_criteria=eval_criteria
        ) + "\n The instruction & request is : '{request}' \n  Model Response is: '{response}'"

    def _get_model_result(self, prev_result, current_result) -> T2TSystemResult:
        sxs_results = None
        if self.prev_params:
            sxs_results = []
            assert prev_result and current_result
            for prev, current in zip(prev_result, current_result):
                sxs_results.append(
                    SideBySideResult(request=prev['input'],
                                     previous_response=prev['model_output'],
                                     current_response=current['model_output']))

        assert self.default_model is not None

        data = self.test_data[0:self.MAX_EXAMPLES_FOR_VISUALIZATION]
        print("Visualizing model results..")
        examples = self._visualize_model(self.default_model, data=data)

        print("Evaluating default model...")
        eval_result = self._evaluate_model(self.default_model, data=data)
        models = [model.run_name for model in self.model_map.values()]

        return T2TSystemResult(
            eval_result=eval_result,
            examples=examples,
            sxs_result=sxs_results,
            current_task_spec=self.current_task_spec,
            experiment_id=self.experiment_id,
            model_candidates=models,
            default_model=self.default_model.run_name,
            instruction_info=self.instruction_info,
        )

    def get_system_param(self):
        models = list(self.model_map.keys())

        return {
            "instruction": self.current_params.instruction,
            "eval_criteria": self.current_task_spec.evaluation_criteria,
            "example_data": self.test_data[:self.MAX_EXAMPLES_FOR_VISUALIZATION],
            "experiment_id": self.experiment_id,
            "model_candidates": models,
            "instruction_info": self.instruction_info,
        }

    def update_system_param(self, new_spec: Text2TextTaskSpec):
        """Updates the state of the runner with new Text2Text spec."""
        if new_spec.experiment_name is not self.current_task_spec.experiment_name:
            raise ValueError("Experiment name cannot be updated.")

        new_system_param = new_spec.to_system_param()
        self.prev_params = self.current_params
        self.prev_task_spec = self.current_task_spec
        self.current_task_spec = new_spec
        self.current_params = new_system_param
        return self.compile()

    def evaluate_models(self):
        """Evaluates all models in the runner using the provided evaluation criteria."""
        result = {}
        if not self.current_task_spec.evaluation_criteria:
            raise ValueError("Evaluation criteria is not provided. Make sure to call `compile()` API.")

        for model_wrapper in self.model_map.values():
            model_eval = self._evaluate_model(model_wrapper)
            result[model_wrapper.run_name] = model_eval
        return result

    def visualize_models(self):
        """Runs a subset of test data through each model and returns the results."""
        result = {}
        for model_wrapper in self.model_map.values():
            result[model_wrapper.run_name] = self._visualize_model(model_wrapper)
        return pd.DataFrame.from_dict(result)

    def deploy_model(self, run_name: str, schema_name: str, endpoint_name: str, secret_scope: str, secret_key: str):
        """Deploys a model to a production endpoint using the provided secret.

        Args:
            run_name: The run name of the model to deploy.
            schema_name: The unity catalog schema name to use for the model.
            endpoint_name: The name of the endpoint to deploy.
            secret_scope: The secret scope containing the secret.
            secret_key: The secret key to use for the deployment.
        """
        if not validate_secret_exists(secret_scope, secret_key):
            raise ValueError(f"Secret {secret_key} in scope {secret_scope} does not exist.")

        model_wrapper = None
        model_wrapper = self.model_map.get(run_name, None)
        if not model_wrapper:
            raise ValueError(
                f"invalid model descriptor.. input: `{run_name}` candidates: {list(self.model_map.keys())}")

        self._register_model(model_wrapper, schema_name)

        model_url = model_wrapper.get_model_path()
        production_model = mlflow.pyfunc.load_model(model_url)
        api_url, api_token = get_host_and_token_from_env()
        data = {
            "name": endpoint_name,
            "config": {
                "served_entities": [{
                    "entity_name": model_wrapper.registered_model_name,
                    "entity_version": '1',
                    "workload_size": "Small",
                    "scale_to_zero_enabled": True,
                    "environment_vars": {
                        "DATABRICKS_HOST": api_url,
                        "DATABRICKS_TOKEN": "{{" + f"secrets/{secret_scope}/{secret_key}" + "}}",
                    }
                }]
            }
        }

        headers = {"Context-Type": "text/json", "Authorization": f"Bearer {api_token}"}

        response = request_lib.post(url=f"{api_url}/api/2.0/serving-endpoints", json=data, headers=headers, timeout=60)
        print("Deployed endpoint.. Response status:", response.status_code)
        print("Deployed endpoint.. Response text:", response.text, "\n")
        return production_model

    def _get_exp_id(self, experiment_name: str):
        experiment = get_experiment_by_name(experiment_name)
        if not experiment:
            return create_experiment(name=experiment_name)
        return experiment.experiment_id

    def _create_custom_metrics(self):
        """Create custom metrics for the model.

        Generates custom metrics for the model based on the self.current_task_spec.eval_criteria.
        Assumes that self.evaluation_criteria is already set.(i.e. compile() has been called)
        """

        def _wrapper_fn(request: str, response: str, guideline: str, metric_name: str):
            assessment = judges.guideline_adherence(
                request=request,
                response=response,
                guidelines=[guideline],
            )
            return Assessment(name=metric_name,
                              value=assessment.value,
                              rationale=assessment.rationale,
                              source=assessment.source)

        eval_criteria = self.current_task_spec.evaluation_criteria
        assert eval_criteria
        self.custom_metrics = []
        for criterion in eval_criteria:
            metric_name = re.sub(r'[^a-zA-Z0-9]', '_', criterion)
            custom_metric_fn = functools.partial(_wrapper_fn, guideline=criterion, metric_name=metric_name)
            custom_metric = metric(eval_fn=custom_metric_fn, name=metric_name)
            self.custom_metrics.append(custom_metric)

    def _create_classic_metrics(self):
        """Creates classic metrics for given the instruction type. Assumes self.instruction_info is already set."""
        assert self.instruction_info.instruction_type
        classic_metrics = create_classic_metrics(self.instruction_info.instruction_type)
        self.custom_metrics.extend(classic_metrics)

    def _prepare_data(self):
        """Randomly sample half of example_data to test data and other half to train data."""
        # TODO: support unlabeled data / output generation.
        assert self.current_params.labelled_examples
        data = self.current_params.labelled_examples
        example_data = [{'request': datum[0], 'response': datum[1]} for datum in data]
        example_data_size = len(data)
        if example_data_size < self.MIN_EVAL_DATA:
            self.test_data = example_data
            return

        indices = list(range(example_data_size))
        random.shuffle(indices)
        split_index = example_data_size // 2

        train_indices = indices[:split_index]
        test_indices = indices[split_index:]

        self.train_data = [example_data[i] for i in train_indices]
        self.test_data = [example_data[i] for i in test_indices]

    def _create_optimized_instruction(self):
        if not self.instruction_info:
            raise ValueError("Instruction info is not provided. Make sure to call `compile()` API.")

        optimized_instruction = self.instruction_info.optimized_instruction
        output_format = self.instruction_info.output_format

        return self.INSTRUCTION_TEMPLATE.format(optimized_instruction=optimized_instruction,
                                                output_format=output_format)

    def _create_models(self):
        for model_id in self.MODEL_SELECTION:
            if model_id in self.MODEL_SELECTION_WITH_STRUCTURED_OUTPUT_SUPPORT:
                model = self._create_cot_model(model_id)
                self.model_map[model.run_name] = model
                if model_id == self.DEFAULT_MODEL_ID:
                    self.default_model = model

            model = self._create_baseline_model(model_id)
            self.model_map[model.run_name] = model

            for n in self.NUM_FEW_SHOTS:
                if n > len(self.train_data):
                    break

                model = self._create_text2text_model(model_id, self._create_optimized_instruction(), num_few_shot=n)
                self.model_map[model.run_name] = model

    def _create_cot_model(self, model_id: str):
        num_few_shot_examples = max(n for n in self.NUM_FEW_SHOTS if n <= len(self.train_data))
        model_descriptor = f"{model_id}_chain_of_thought"
        return self._create_text2text_model(model_id,
                                            self._create_optimized_instruction(),
                                            num_few_shot=num_few_shot_examples,
                                            use_cot=True,
                                            model_descriptor=model_descriptor)

    def _create_baseline_model(self, model_id: str):
        model_descriptor = f"{model_id}_baseline"
        return self._create_text2text_model(model_id,
                                            self.current_params.instruction,
                                            num_few_shot=0,
                                            use_cot=False,
                                            model_descriptor=model_descriptor)

    def _register_model(self, model_wrapper: ModelWrapper, schema_path: str):
        custom_model = model_wrapper.custom_model
        run_id = model_wrapper.run_id
        registered_model_name = f'{schema_path}.t2t_{self.experiment_id}_{run_id}'
        model_wrapper.registered_model_name = registered_model_name
        with start_run(experiment_id=self.experiment_id, run_id=run_id):
            mlflow.pyfunc.log_model(
                "model",
                python_model=custom_model,
                pip_requirements=["pandas", "mlflow", f"databricks-genai=={__version__}", "databricks-connect"],
                signature=custom_model.signature,
                registered_model_name=registered_model_name)

    def _create_text2text_model(
        self,
        model_id: str,
        instruction: str,
        num_few_shot: int = 0,
        use_cot: bool = False,
        model_descriptor: Optional[str] = None,
    ) -> ModelWrapper:
        description = (f't2t_model_registry_{model_descriptor}'
                       if model_descriptor else f't2t_model_registry_{model_id}_few_shot_{num_few_shot}')
        with start_run(
                experiment_id=self.experiment_id,
                description=description,
        ) as run:
            few_shot_examples = []
            if num_few_shot:
                few_shot_examples = random.sample(self.train_data, num_few_shot)

            signature = infer_signature(model_input=["input"], model_output=["output"])

            custom_model = CustomModel(
                instruction,
                signature,
                model_id,
                few_shot_examples,
                model_descriptor=model_descriptor,
                use_cot=use_cot,
            )
            run_id = run.info.run_id
            run_name = run.info.run_name
            return ModelWrapper(custom_model, run_id, run_name, registered_model_name=None)

    def _visualize_model(self, model_wrapper: ModelWrapper, data: Optional[List[Dict[str, str]]] = None):
        custom_model = model_wrapper.custom_model
        model_results = []
        eval_data = data or self.test_data[0:self.MAX_EXAMPLES_FOR_VISUALIZATION]
        for datum in tqdm(eval_data, desc=f"Visualizing model {model_wrapper.run_name}"):
            req = datum['request']
            output_dict = {}
            output_dict["input"] = req
            output_dict["model_output"] = custom_model.predict(None, req)
            if 'response' in datum:
                output_dict["label"] = datum['response']
            model_results.append(output_dict)
        return model_results

    def _evaluate_model(self,
                        model_wrapper: ModelWrapper,
                        data: Optional[List[Dict[str, str]]] = None) -> mlflow.models.EvaluationResult:
        eval_data = data or self.test_data[0:self.MAX_EVAL_DATA]
        if not self.current_params.evaluation_criteria:
            raise ValueError("Evaluation criteria is not provided. Please invoke `compile()` API.")

        custom_model = model_wrapper.custom_model
        requests = [
            INSTRUCTION_AND_INPUT_PROMPT_TEMPLATE.format(instruction=self.current_params.instruction,
                                                         inp=datum['request']) for datum in eval_data
        ]
        ground_truth = [datum['response'] for datum in eval_data]

        with start_run(experiment_id=self.experiment_id, run_id=model_wrapper.run_id):
            model_responses = []
            traces = []
            for req in tqdm(requests, desc=f"Evaluating model {model_wrapper.run_name}"):
                root_span = self.mlflow_client.start_trace(name=model_wrapper.run_name)
                request_id = root_span.request_id
                model_response = custom_model.predict(None, req)
                self.mlflow_client.end_trace(request_id)

                traces.append(get_trace(request_id).to_json())
                model_responses.append(model_response)

            eval_df = pd.DataFrame({
                "request": requests,
                "expected_response": ground_truth,
                "response": model_responses,
                "trace": traces
            })

            return mlflow.evaluate(
                data=eval_df,
                model_type="databricks-agent",  # Enable Mosaic AI Agent Evaluation
                extra_metrics=self.custom_metrics,
                # Disable built-in judges.
                evaluator_config={'databricks-agent': {
                    "metrics": [],
                }})
