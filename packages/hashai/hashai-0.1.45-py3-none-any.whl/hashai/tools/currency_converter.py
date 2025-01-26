# currency_converter.py
from .base_tool import BaseTool
from forex_python.converter import CurrencyRates, CurrencyCodes
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import Field

class CurrencyConverter(BaseTool):
    default_from_currency: str = Field(default="USD", description="Default base currency (e.g., 'USD').")
    default_to_currency: str = Field(default="EUR", description="Default target currency (e.g., 'EUR').")
    enable_historical_rates: bool = Field(default=True, description="Enable fetching historical exchange rates.")
    enable_multiple_currencies: bool = Field(default=True, description="Enable converting to multiple target currencies.")
    enable_currency_info: bool = Field(default=True, description="Enable fetching currency information (e.g., symbol, name).")

    def __init__(self, **kwargs):
        super().__init__(
            name="CurrencyConverter",
            description="Convert the currency.",
            **kwargs)
        self.c = CurrencyRates()
        self.codes = CurrencyCodes()

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the currency conversion based on the provided input.

        Args:
            input_data (Dict[str, Any]): Input data containing the currencies and optional parameters.

        Returns:
            Dict[str, Any]: Currency conversion results and additional information.
        """
        from_currency = input_data.get("from_currency", self.default_from_currency)
        to_currencies = input_data.get("to_currencies", [self.default_to_currency])
        if isinstance(to_currencies, str):
            to_currencies = [to_currencies]  # Convert single currency to list

        amount = input_data.get("amount", 1)
        date = input_data.get("date")  # For historical rates
        time_range = input_data.get("time_range")  # For historical rate trends

        results = {}

        # Fetch currency information (e.g., symbol, name)
        if self.enable_currency_info:
            results["from_currency_info"] = self._get_currency_info(from_currency)
            results["to_currencies_info"] = {
                currency: self._get_currency_info(currency) for currency in to_currencies
            }

        # Perform conversions
        results["conversions"] = {}
        for to_currency in to_currencies:
            conversion_data = {}

            # Real-time conversion
            conversion_data["real_time"] = self.c.convert(from_currency, to_currency, amount)

            # Historical conversion (if enabled)
            if self.enable_historical_rates:
                if date:
                    conversion_data["historical"] = self.c.convert(
                        from_currency, to_currency, amount, date
                    )
                if time_range:
                    conversion_data["trend"] = self._get_historical_trend(
                        from_currency, to_currency, time_range
                    )

            results["conversions"][to_currency] = conversion_data

        return results

    def _get_currency_info(self, currency_code: str) -> Dict[str, str]:
        """
        Fetch currency information (e.g., symbol, name).

        Args:
            currency_code (str): The currency code (e.g., "USD").

        Returns:
            Dict[str, str]: Currency information.
        """
        return {
            "code": currency_code,
            "symbol": self.codes.get_symbol(currency_code),
            "name": self.codes.get_currency_name(currency_code),
        }

    def _get_historical_trend(
        self, from_currency: str, to_currency: str, time_range: str
    ) -> Dict[str, float]:
        """
        Fetch historical exchange rate trends for a given time range.

        Args:
            from_currency (str): The base currency.
            to_currency (str): The target currency.
            time_range (str): The time range (e.g., "1w", "1m", "1y").

        Returns:
            Dict[str, float]: Historical exchange rates.
        """
        end_date = datetime.now()
        if time_range == "1w":
            start_date = end_date - timedelta(weeks=1)
        elif time_range == "1m":
            start_date = end_date - timedelta(days=30)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            raise ValueError(f"Unsupported time range: {time_range}")

        rates = {}
        current_date = start_date
        while current_date <= end_date:
            rate = self.c.get_rate(from_currency, to_currency, current_date)
            rates[current_date.strftime("%Y-%m-%d")] = rate
            current_date += timedelta(days=1)

        return rates