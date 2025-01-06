import os
from time import sleep
from typing import Any

import splunklib.client as client  # type: ignore
import splunklib.results as results  # type: ignore


class SplunkOperator:
    SPLUNK_PIE_INDEX_NAME = 'datainfra'
    SPLUNK_ITUNES_INDEX_NAME = 'amp_ds_spark_jobs'

    def get_pie_splunk_service(self) -> client.Service:
        """Instantiates the Splunk client service.

        :return: client.Service
        """
        service = client.connect(
            host='splunk.pie.apple.com',
            port=8089,
            token=os.getenv('AMP_DSA_SA_SPLUNK_JWT_TOKEN'),
            retries=5,
            retryDelay=5
        )
        assert isinstance(service, client.Service)
        return service

    def get_itunes_splunk_service(self) -> client.Service:
        """Instantiates the itunes Splunk client service.

        :return: client.Service
        """
        service = client.connect(
            host='splunk.itunes.apple.com',
            port=8089,
            token=os.getenv('AMP_DSA_SA_SPLUNK_JWT_TOKEN_ITUNES'),
            retries=5,
            retryDelay=5
        )
        assert isinstance(service, client.Service)
        return service

    def run_search(
            self, service: client.Service, search_query: str, search_params: dict[Any, Any]
    ) -> results.JSONResultsReader:
        """Runs Splunk Search using query and additional params.

        :param service: client.Service
        :param search_query: str
        :param search_params: dict[Any,Any]
        :return: results.JSONResultsReader
        """
        job = service.jobs.create(search_query, **search_params)

        while not job.is_ready():
            print("waiting for job to be ready")
            sleep(5)

        while not job.is_done():
            print("waiting for job to be done")
            sleep(5)

        return results.JSONResultsReader(job.results(output_mode='json', count=0))

    def run_search_in_pie_and_itunes(
            self, search_query: str, search_params: dict[Any, Any], file_name: str = ""
    ) -> list[dict[str, str]]:
        """Builds search params and runs the search in Splunk for both pie and itunes.

        :param search_query: str
        :param search_params: dict[Any,Any]
        :param file_name: str
        :return: list[dict[str, str]]
        """
        search_query_pie = search_query.replace('{{ index_name }}', self.SPLUNK_PIE_INDEX_NAME)
        search_query_itunes = search_query.replace('{{ index_name }}', self.SPLUNK_ITUNES_INDEX_NAME)

        pie_reader = self.run_search(self.get_pie_splunk_service(), search_query_pie, search_params)
        search_results_pie = list([row for row in pie_reader if isinstance(row, dict)])
        itunes_reader = self.run_search(self.get_itunes_splunk_service(), search_query_itunes, search_params)
        search_results_itunes = list([row for row in itunes_reader if isinstance(row, dict)])

        if len(file_name) > 0:
            print(f"received {len(search_results_pie)} rows from splunk.pie for search query in {file_name}")
            print(f"received {len(search_results_itunes)} rows from splunk.itunes for search query in {file_name}")

        return search_results_pie + search_results_itunes

    def run_search_in_itunes(self, search_query: str, search_params: dict[Any, Any],
                             file_name: str = "") -> list[dict[str, str]]:
        """Builds search params and runs the search in itunes Splunk.

        :param search_query: str
        :param search_params: dict[Any,Any]
        :param file_name: str
        :return: list[dict[str, str]]
        """
        search_query_itunes = search_query.replace('{{ index_name }}', self.SPLUNK_ITUNES_INDEX_NAME)

        itunes_reader = self.run_search(self.get_itunes_splunk_service(), search_query_itunes, search_params)
        search_results_itunes = list([row for row in itunes_reader if isinstance(row, dict)])

        if file_name is not None:
            print(f"received {len(search_results_itunes)} rows from splunk.itunes for search query in {file_name}")

        return search_results_itunes

    def run_search_in_pie(self, search_query: str, search_params: dict[Any, Any],
                          file_name: str = "") -> list[dict[str, str]]:
        """Builds search params and runs the search in pie Splunk.

        :param search_query: str
        :param search_params: dict[Any,Any]
        :param file_name: str
        :return: list[dict[str, str]]
        """
        search_query_pie = search_query.replace('{{ index_name }}', self.SPLUNK_PIE_INDEX_NAME)

        pie_reader = self.run_search(self.get_pie_splunk_service(), search_query_pie, search_params)
        search_results_pie = list([row for row in pie_reader if isinstance(row, dict)])

        if file_name is not None:
            print(f"received {len(search_results_pie)} rows from splunk.pie for search query in {file_name}")

        return search_results_pie
