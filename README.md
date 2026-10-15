# Indonesia Exchange Rates Timeseries

Target Currencies List: Defines major global currencies (such as USD, EUR, SGD, JPY, etc.) to be tracked against the Indonesian Rupiah (IDR).

Dynamic Date Window: Uses the datetime module to establish a 30-day historical window to gather a rich time-series dataset.

Public Financial API: Queries the reliable Frankfurter exchange rate API to pull historical currency valuation records.

Data Formatting & Sorting: Normalizes the JSON response into structured tabular rows, sorts them chronologically using Pandas, and saves the output into indonesia_exchange_rates_timeseries.csv ready for Kaggle.
