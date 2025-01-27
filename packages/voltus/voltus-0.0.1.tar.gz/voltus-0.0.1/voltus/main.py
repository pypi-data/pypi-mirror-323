from enum import StrEnum
from io import BytesIO
from typing import Any, Dict, List, Optional
import pandas as pd
import requests


class ExampleDatasets(StrEnum):
    PowerUsage = ("Power Usage",)
    KMeansClustering = ("KMeans Clustering",)
    DatetimeFeatures = ("Datetime Features",)
    StatisticalInformation = ("Statistical Information",)
    LagsOrLeads = ("Lags or Leads",)
    WindDirectionAndModule = ("Wind Direction and Module",)
    RollingWindowFeatures = ("Rolling Window Features",)
    ExpandingWindowFeatures = ("Expanding Window Features",)
    SubtractingDates = ("Subtracting Dates",)
    ClearSkyModel = ("Clear Sky Model",)
    PCADecomposition = ("PCA Decomposition",)
    WindEnergy = ("Wind Energy",)
    SquaredValue = ("Squared Value",)
    CrossEffectsFeatures = ("Cross Effects Features",)
    Recipe = "Recipe"


class VoltusClient:
    """
    A client for interacting with the Voltus feature store API.

    Attributes:
        api_url (str): The base URL of the Voltus API.
        token (str): The authentication token.
    """

    def __init__(self, api_base_url: str, token: str, verify_requests: bool = True):
        """
        Initializes the VoltusClient.

        Args:
            api_url: The base URL of the Voltus API.
        """
        # checking inputs
        if api_base_url is None:
            raise Exception(f"'api_base_url' is required. Got '{api_base_url}'")
        elif not isinstance(api_base_url, str):
            raise Exception(
                f"'api_base_url' must be a string. Got {type(api_base_url)}"
            )

        if token is None:
            raise Exception(f"'token' is required. Got '{token}'")
        elif not isinstance(token, str):
            raise Exception(f"'token' must be a string. Got {type(token)}")

        # parsing api_base_url
        self.url = (
            api_base_url.replace("\\", "/")
            .replace("https://", "")
            .replace("http://", "")
            .strip("/")
            .strip()
        )
        self.url = api_base_url
        self.token = token
        self.verify_requests = verify_requests
        self.healthcheck()

    def healthcheck(self) -> bool:
        try:
            response = requests.get(
                verify=self.verify_requests,
                url=f"https://{self.url}/v1/current_authenticated_user",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "accept": "application/json",
                },
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to '{self.url}'. Error: {str(e)}")

        assert response.status_code == 200, f"Status code mismatch: {response.text}"
        response_json = response.json()
        assert (
            response_json["user"]["token"] == self.token
        ), f"Token mismatch: {response.json()}"

        return True

    def get_task_status(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gets the status of an asynchronous task.

        Args:
            task_id (Optional[str], optional): The ID of the task. If None, retrieves the status of all tasks. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing the status of a task.
        """
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/task_status",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"task_id": task_id},
        )
        return response.json()

    def get_current_authenticated_user(self):
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/current_authenticated_user",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
        )
        return response.json()

    def add_dataset(
        self,
        dataset: pd.DataFrame,
        dataset_name: str = "new dataset",
        description: str = "",
        overwrite: bool = True,
    ):
        buffer = BytesIO()
        dataset.to_parquet(buffer, index=False)
        buffer.seek(0)
        response = requests.post(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/datasets/file",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            params={
                "dataset_name": dataset_name,
                "description": description,
                "overwrite": overwrite,
            },
            files={
                "file": (
                    f"{dataset_name}.parquet",
                    buffer,
                ),
            },
        )
        print(response.text)

    def list_datasets(self) -> List[str]:
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/datasets/list",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"detailed": "false"},
        )

        assert response.status_code == 200, f"Status code mismatch: {response.text}"
        return response.json()

    def retrieve_dataset(self, dataset_name: str) -> pd.DataFrame:
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/datasets/{dataset_name}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "file_format": "json",
            },
        )
        print(response.text)
        assert response.status_code == 200, f"Status code mismatch: {response.text}"
        return response.json()

    def delete_datasets(self, dataset_names: List[str]) -> None:
        response = requests.delete(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/datasets/delete",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "dataset_names": dataset_names,
            },
        )
        assert response.status_code == 200, f"Status code mismatch: {response.text}"

    def list_example_datasets(self) -> List[str]:
        return [d.value for d in ExampleDatasets]

    def retrieve_example_dataset(self, dataset_name: str) -> pd.DataFrame:
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/datasets/example/{dataset_name}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "file_format": "json",
            },
        )
        assert response.status_code == 200, f"Status code mismatch: {response.text}"
        return response.json()

    def apply_feature_function_to_dataset(
        self,
        feature_function_name: str,
        original_datasets: List[str],
        generated_dataset_name: Optional[str] = None,
        generated_dataset_description: Optional[str] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        process_synchronously: bool = True,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        """
        Applies a feature function to existing data.

        Args:
            feature_function_name (str): The name of the feature function to apply.
            original_datasets (List[str]): A list of dataset names to apply the function to
            generated_dataset_name (Optional[str], optional): A name for the generated dataset. Defaults to None.
            generated_dataset_description (Optional[str], optional): A description for the generated dataset. Defaults to None.
            kwargs (Optional[Dict[str, Any]], optional): Keyword arguments for the feature function. Defaults to None.
            overwrite (bool, optional): Whether to overwrite an existing dataset. Defaults to True.

        Returns:
        Dict[str, Any]: A dict with the response message and, if any, task_ids.
        """
        instruction = {
            "feature_function_name": feature_function_name,
            "original_datasets": original_datasets,
            "generated_dataset_name": generated_dataset_name,
            "generated_dataset_description": generated_dataset_description,
            "feature_function_kwargs": kwargs or {},
        }
        response = requests.post(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/functions/apply_to_dataset",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={
                "process_synchronously": process_synchronously,
                "overwrite": overwrite,
            },
            json=[instruction],
        )
        return response.json()

    def list_feature_functions(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """
        Lists available feature functions.

        Args:
            detailed (bool, optional): Whether to include detailed information about each feature function. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a feature function.
        """
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/functions/list",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
            params={"detailed": detailed},
        )
        return response.json()

    def list_feature_functions_tags(self) -> List[str]:
        """
        Lists all available tags for feature functions.

        Returns:
            List[str]: A list of tags.
        """
        response = requests.get(
            verify=self.verify_requests,
            url=f"https://{self.url}/v1/functions/tags",
            headers={
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json",
            },
        )
        return response.json()["tags"]

    # def list_trained_models(self) -> List[str]:
    #     """
    #     Lists the available trained ML models.

    #     Returns:
    #         List[str]: A list of model names.
    #     """
    #     response = self._make_request("GET", "/machinelearning/models")
    #     return response.json()


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv(verbose=True)

    BASE_URL = os.getenv("BASE_URL", None)
    USER_TOKEN = os.getenv("USER_TOKEN", None)

    client = VoltusClient(BASE_URL, USER_TOKEN, verify_requests=True)

    # user_json = client.get_current_authenticated_user()
    # print(user_json)

    # df = pd.read_csv(
    #     "C:/Users/carlos.t.santos/Desktop/Files/Reps/feature-store/clients/python-client/python_client/energy_data.csv"
    # )
    # client.add_dataset(df)

    dataset_names = client.list_datasets()
    for dataset_name in dataset_names:
        print(dataset_name)

    # client.retrieve_dataset(dataset_names[0])
