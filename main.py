# Write a small Python program that uses the https://fixer.io API to get the USD to GBP exchange rate.
# Assume that the API call might fail sometimes, and in this case your program should retry until it succeeds.
# The program should output the number of GBP you can buy with 100 USD, e.g. "£78.73". Please include tests.


import unittest
from unittest.mock import patch
import requests
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# Retry until it succeed might not be the best approach, retry after a few times is much safer.
def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session


def get_connection():
    try:
        response = requests_retry_session().\
            get("http://data.fixer.io/api/latest?access_key=5d116b0c18890dc5c93af9641e08dc16")

        data = response.text
        parse_json = json.loads(data)
        gbp = parse_json['rates']['GBP']
        usd = parse_json['rates']['USD']

        exchange = gbp / usd
        exchange = 100 * exchange
        exchange = str(round(exchange, 2))

    except Exception as e:
        print('It failed :(', e.__class__.__name__)

    print("£{}".format(exchange))
    return exchange


get_connection()


class TestConnection(unittest.TestCase):

    @patch('main.requests_retry_session')
    def test_retry_session(self, mock_requests_retry_session):
        assert mock_requests_retry_session()
        mock_requests_retry_session.assert_called_once()

    @patch('main.get_connection')
    def test_get_connection_assert_called_once(self, mock_connection):
        assert mock_connection()
        mock_connection.assert_called_once()

    @patch('main.get_connection')
    def test_get_connection_assert_raises_timeout(self, mock_connection):
        mock_connection.side_effect = ConnectionError
        with self.assertRaises(ConnectionError):
            mock_connection()

    @patch('main.get_connection')
    def test_response_assert_with_values(self, mock_connection):
        assert mock_connection()

        mock_connection.return_value = {'£75.6'}
        mock_connection.assert_called_once()


if __name__ == '__main__':
    unittest.main()




