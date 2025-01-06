from typing import Any

from amp_ds_platform_library.models.metadata.metadata_service import APIRequest, APIRequestMethod, Job, JobCreateRequest
import requests


class MetadataServiceOperator:

    base_url: str = "https://amp-ds-platform-services.g.apple.com/metadata/api/"

    def __init__(self, token: str):
        """Constructor for MetadataServiceOperator.

        :param token: Access token for Platform Services API
        """
        self.token = token

    def create_job(self, job_create_request: JobCreateRequest) -> Job:
        """Create job metadata.

        :param job_create_request: JobCreateRequest
        :return: JobCreateResponse
        """
        headers: dict[str, Any] = {
            "Authorization": f"Api-Key {self.token}"
        }
        api_request = APIRequest(
            url=self.base_url + "v2/jobs/",
            method=APIRequestMethod.post,
            headers=headers,
            json_data=job_create_request.model_dump()
        )
        api_response: dict[str, Any] = self.api_request(api_request=api_request)
        response: Job = Job(**api_response.get("data", {}))

        return response

    def get_jobs(self) -> list[Job]:
        """Get jobs metadata.

        :return: list[Job]
        """
        headers: dict[str, Any] = {
            "Authorization": f"Api-Key {self.token}"
        }
        api_request = APIRequest(
            url=self.base_url + "v2/jobs/",
            method=APIRequestMethod.get,
            headers=headers
        )
        api_response: dict[str, Any] = self.api_request(api_request=api_request)
        response: list[Job] = [Job(**job) for job in api_response.get("data", [])]

        return response

    @staticmethod
    def api_request(api_request: APIRequest) -> dict[str, Any]:
        """Execute platform services API requests.

        :param api_request: APIRequest
        :return: dict[str,str]
        """
        result: dict[str, Any] = {}
        try:
            if api_request.method == "GET":
                response = requests.get(url=api_request.url, headers=api_request.headers, params=api_request.params)
            elif api_request.method == "POST":
                response = requests.post(url=api_request.url, headers=api_request.headers, json=api_request.json_data)
            elif api_request.method == "PATCH":
                response = requests.patch(url=api_request.url, headers=api_request.headers, json=api_request.json_data)
            elif api_request.method == "DELETE":
                response = requests.delete(url=api_request.url, headers=api_request.headers)
            else:
                raise RuntimeError("API request method not permitted.")
            response.raise_for_status()
            result = {"data": response.json()}
        except requests.exceptions.RequestException as e:
            raise RuntimeError("Metadata Service request error occured: " + str(e))

        return result