import time

from elasticsearch import Elasticsearch

TIMEOUT = 60

if __name__ == '__main__':
    es_client = Elasticsearch(hosts='http://elasticsearch:9200')

    start_time = time.time()

    while True:

        if es_client.ping():
            break

        if time.time() - start_time > TIMEOUT:
            raise TimeoutError(
                f'Elasticsearch did not become ready within {TIMEOUT} seconds'
            )

        time.sleep(1)
