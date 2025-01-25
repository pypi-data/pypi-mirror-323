import json
import opensearchpy
# from opensearchpy import OpenSearch, helpers

from python_sdk_remote import our_object, utilities
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class OpenSearchIngester(opensearchpy.OpenSearch):
    def __init__(self):
        host = utilities.our_get_env(key="OPENSEARCH_HOST")
        hosts = [{"host": host, "port": 9200}]
        username = "admin"
        password = utilities.our_get_env(key="OPENSEARCH_INITIAL_ADMIN_PASSWORD")
        print(password)

        self.client = opensearchpy.OpenSearch(
            hosts=hosts,
            http_auth=(username, password),
            use_ssl=True,
            verify_certs=False,
        )

# TODO: add support for multiple types of objects
    def create_ingest_bulk(self, object: list[our_object.OurObject]):
        for obj in object:
            if not isinstance(obj, our_object.OurObject):
                raise ValueError("Input must be an instance of OurObject")

        data = []

        for obj in object:
            data.append(json.loads(obj.to_json()))

        index_name = object[0].__class__.__name__.lower()

        try:
            self.create_index_if_not_exists(index_name)
        except Exception as e:
            print(f"Error creating index: {e}")

        action = {
                "index": {
                    "_index": index_name
                    }
                }

        bulk_json = self.payload_constructor(data, action)

        response = self.client.bulk(
            body=bulk_json,
            index=index_name,
        )

        # TODO: add support for chunking
        # if len(bulk_json) < 500:
        #     response = opensearchpy.helpers.bulk(
        #         client=self.client,
        #         actions=bulk_json,
        #         index=index_name
        #     )
        # else:
        #     response = opensearchpy.helpers.bulk(
        #         client=self.client,
        #         actions=bulk_json,
        #         index=index_name,
        #         chunk_size=500
        #     )

        return response, len(bulk_json.split('\n')), len(data)

    def payload_constructor(self, data, action):
        payload_lines = []
        for datum in data:
            payload_lines.append(json.dumps(action))
            payload_lines.append(json.dumps(datum))

        return "\n".join(payload_lines)

    def create_index_if_not_exists(self, index_name):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name)
