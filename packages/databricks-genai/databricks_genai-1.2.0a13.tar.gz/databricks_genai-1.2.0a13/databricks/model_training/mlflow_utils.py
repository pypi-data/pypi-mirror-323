"""mlflow utility functions for handling runs and metadata"""
import json
from typing import Dict, NamedTuple, Optional

from databricks.sdk import WorkspaceClient  # pylint: disable=ungrouped-imports
from mlflow import MlflowClient
from mlflow.data.delta_dataset_source import DeltaDatasetSource
from mlflow.data.meta_dataset import MetaDataset
from mlflow.entities import DatasetInput, InputTag, SourceType
from mlflow.utils.mlflow_tags import (MLFLOW_DATABRICKS_NOTEBOOK_ID, MLFLOW_DATABRICKS_NOTEBOOK_PATH,
                                      MLFLOW_DATASET_CONTEXT, MLFLOW_SOURCE_NAME, MLFLOW_SOURCE_TYPE)

from databricks.model_training.api.utils import get_current_notebook_details


def get_mlflow_client() -> MlflowClient:
    return MlflowClient(tracking_uri="databricks", registry_uri="databricks-uc")


class DeltaTableDetails(NamedTuple):
    catalog: Optional[str]
    name: Optional[str]
    full_name: Optional[str]
    version: Optional[int]


def get_delta_table_details(path: str) -> DeltaTableDetails:
    w = WorkspaceClient()
    details = w.tables.get(path, include_delta_metadata=True)
    version = None
    if details.delta_runtime_properties_kvpairs:
        if details.delta_runtime_properties_kvpairs.delta_runtime_properties:
            attributes = details.delta_runtime_properties_kvpairs.delta_runtime_properties.get("commitAttributes")
            if attributes:
                version = json.loads(attributes)["version"]

    return DeltaTableDetails(catalog=details.catalog_name,
                             name=details.name,
                             full_name=details.full_name,
                             version=version)


def log_delta_table_source(run_id: str, path: str, name: str = "Dataset", split: Optional[str] = None):
    client = get_mlflow_client()

    # Get the source delta table
    table_details = get_delta_table_details(path)
    source = DeltaDatasetSource(delta_table_name=path, delta_table_version=table_details.version)
    #TODO: Could add schema using the columns field from get_delta_table_details
    meta = MetaDataset(source, name=name)

    # Contstruct the entities
    tags = [InputTag(key=MLFLOW_DATASET_CONTEXT, value=split)] if split else []
    inputs = [DatasetInput(dataset=meta._to_mlflow_entity(), tags=tags)]  # pylint: disable=protected-access

    return client.log_inputs(run_id=run_id, datasets=inputs)


def update_run_tags(run_id: str, tags: Dict[str, str]):
    client = get_mlflow_client()
    for k, v in tags.items():
        client.set_tag(run_id, k, v)


def change_run_name(run_id: str, new_name: str) -> None:
    client = get_mlflow_client()
    return client.update_run(run_id=run_id, name=new_name)


def add_notebook_source(run_id: str):
    details = get_current_notebook_details()
    if not details:
        return
    tags = {
        MLFLOW_SOURCE_NAME: details.notebook_path,
        MLFLOW_SOURCE_TYPE: SourceType.to_string(SourceType.NOTEBOOK),
        MLFLOW_DATABRICKS_NOTEBOOK_PATH: details.notebook_path,
        MLFLOW_DATABRICKS_NOTEBOOK_ID: details.notebook_id,
    }
    update_run_tags(run_id, tags)
