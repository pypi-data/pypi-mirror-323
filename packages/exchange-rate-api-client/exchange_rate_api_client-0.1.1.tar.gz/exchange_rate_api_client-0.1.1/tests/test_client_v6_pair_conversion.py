import unittest

from unittest.mock import patch, Mock, MagicMock

from exchange_rate_api_client._client import ExchangeRateApiV6Client

from exchange_rate_api_client.commons import PairConversion

from exchange_rate_api_client.exceptions import (
    UnsupportedCode,
    InvalidKey,
    InactiveAccount,
    QuotaReached,
    MalformedRequest,
)


class TestExchangeRateV6Client(unittest.TestCase):
    def setUp(self):
        self.client = ExchangeRateApiV6Client("mock-api-key")

    def test_initialization(self): ...

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_with_valid_codes(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "time_last_update_unix": 1737331202,
            "time_last_update_utc": "Mon, 20 Jan 2025 00:00:02 +0000",
            "time_next_update_unix": 1737417602,
            "time_next_update_utc": "Tue, 21 Jan 2025 00:00:02 +0000",
            "base_code": "EUR",
            "target_code": "USD",
            "conversion_rate": 1.0278,
            "extra_attribute": "extra",  # Extra attribute that will be ignored
        }

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        expected = PairConversion(
            base_code="EUR",
            target_code="USD",
            conversion_rate=1.0278,
            time_last_update_unix=1737331202,
            time_last_update_utc="Mon, 20 Jan 2025 00:00:02 +0000",
            time_next_update_unix=1737417602,
            time_next_update_utc="Tue, 21 Jan 2025 00:00:02 +0000",
        )

        result = self.client.pair_conversion("EUR", "USD")

        self.assertEqual(result.model_dump(), expected.model_dump())

        mock_get.assert_called_with(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/EUR/USD", timeout=10
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_with_amount(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "time_last_update_unix": 1737331202,
            "time_last_update_utc": "Mon, 20 Jan 2025 00:00:02 +0000",
            "time_next_update_unix": 1737417602,
            "time_next_update_utc": "Tue, 21 Jan 2025 00:00:02 +0000",
            "base_code": "EUR",
            "target_code": "USD",
            "conversion_rate": 1.0278,
            "conversion_result": 4.1112,
            "extra_attribute": "extra",  # Extra attribute that will be ignored
        }

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        expected = PairConversion(
            base_code="EUR",
            target_code="USD",
            conversion_rate=1.0278,
            conversion_result=4.1112,
            time_last_update_unix=1737331202,
            time_last_update_utc="Mon, 20 Jan 2025 00:00:02 +0000",
            time_next_update_unix=1737417602,
            time_next_update_utc="Tue, 21 Jan 2025 00:00:02 +0000",
        )

        result = self.client.pair_conversion("EUR", "USD", 4)

        self.assertEqual(result.model_dump(), expected.model_dump())

        mock_get.assert_called_with(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/EUR/USD/4", timeout=10
        )

    def test_pair_conversion_on_invalid_arguments_raises_exception(self):
        with self.assertRaises(ValueError) as context:
            self.client.pair_conversion(10, "USD", 10)

        self.assertIn("base code", str(context.exception).lower())

        with self.assertRaises(ValueError) as context:
            self.client.pair_conversion(None, "USD", 10)

        self.assertIn("base code", str(context.exception).lower())

        with self.assertRaises(ValueError) as context:
            self.client.pair_conversion("USD", 10, 10)

        self.assertIn("target code", str(context.exception).lower())

        with self.assertRaises(ValueError) as context:
            self.client.pair_conversion("USD", None, 10)

        self.assertIn("target code", str(context.exception).lower())

        with self.assertRaises(ValueError) as context:
            self.client.pair_conversion("USD", "EUR", "GBP")

        self.assertIn("amount", str(context.exception).lower())

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_unsupported_code_raises_exception(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        # The mock will only be called once and will be stored in the cache.
        mock_get.return_value = mock_supported_codes_response

        with self.assertRaises(UnsupportedCode) as context:
            self.client.pair_conversion("COP", "EUR")

        self.assertIn("COP", str(context.exception))

        with self.assertRaises(UnsupportedCode) as context:
            self.client.pair_conversion("EUR", "URU")

        self.assertIn("URU", str(context.exception))

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_exceptions_by_checking_supported_codes(
        self, mock_get: Mock
    ):
        mock_invalid_key_response = MagicMock()
        mock_invalid_key_response.status_code = 403
        mock_invalid_key_response.json.return_value = {"error-type": "invalid-key"}

        mock_inactive_account_response = MagicMock()
        mock_inactive_account_response.status_code = 403
        mock_inactive_account_response.json.return_value = {
            "error-type": "inactive-account"
        }

        mock_quota_reached_response = MagicMock()
        mock_quota_reached_response.status_code = 403
        mock_quota_reached_response.json.return_value = {"error-type": "quota-reached"}

        mock_unknown_error_type_response = MagicMock()
        mock_unknown_error_type_response.status_code = 400
        mock_unknown_error_type_response.json.return_value = {"error-type": "unknown"}

        mock_no_error_type_response = MagicMock()
        mock_no_error_type_response.status_code = 0
        mock_no_error_type_response.json.return_value = {}

        mock_get.side_effect = [
            mock_invalid_key_response,
            mock_inactive_account_response,
            mock_quota_reached_response,
            mock_unknown_error_type_response,
            mock_no_error_type_response,
        ]

        with self.assertRaises(InvalidKey):
            self.client.pair_conversion("EUR", "USD")

        with self.assertRaises(InactiveAccount):
            self.client.pair_conversion("EUR", "USD")

        with self.assertRaises(QuotaReached):
            self.client.pair_conversion("EUR", "USD")

        with self.assertRaises(Exception) as context:
            self.client.pair_conversion("EUR", "USD")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

        with self.assertRaises(Exception) as context:
            self.client.pair_conversion("EUR", "USD")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_negative_amount_raises_exception(self, mock_get: Mock):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_get.return_value = mock_supported_codes_response

        with self.assertRaises(ValueError):
            self.client.pair_conversion("USD", "EUR", -1)

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_unsupported_code_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        """Tests when UnsupportedCodeException is raised in the conversion request"""
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unsupported-code"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(UnsupportedCode):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_invalid_key_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "invalid-key"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InvalidKey):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_inactive_account_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "inactive-account"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(InactiveAccount):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_quota_reached_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error-type": "quota-reached"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(QuotaReached):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_malformed_request_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "malformed-request"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(MalformedRequest):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_unknown_error_type_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error-type": "unknown"}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception):
            self.client.pair_conversion("USD", "EUR")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )

    @patch("exchange_rate_api_client._client.requests.get")
    def test_pair_conversion_on_no_error_type_in_data_response_raises_exception(
        self, mock_get: Mock
    ):
        mock_supported_codes_response = MagicMock()
        mock_supported_codes_response.status_code = 200
        mock_supported_codes_response.json.return_value = {
            "supported_codes": [["USD", "United States Dollar"], ["EUR", "Euro"]]
        }

        mock_response = MagicMock()
        mock_response.status_code = 0
        mock_response.json.return_value = {}

        mock_get.side_effect = [mock_supported_codes_response, mock_response]

        with self.assertRaises(Exception) as context:
            self.client.pair_conversion("USD", "EUR")

        self.assertEqual(str(context.exception), "Unknown error ocurred")

        mock_get.assert_any_call(
            "https://v6.exchangerate-api.com/v6/mock-api-key/pair/USD/EUR",
            timeout=10,
        )
