import unittest
import pandas as pd
import numpy as np
import warnings
from grynn_pylib.finance import timeseries


class TestTimeSeries(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame with a datetime index
        dates = pd.date_range(start="2020-01-01", periods=1000, freq="B")
        data = np.random.rand(1000) * 100
        self.df = pd.DataFrame(data, index=dates, columns=["price"])

    def test_rolling_cagr_normal_case(self):
        # Test the rolling CAGR with a normal case
        result = timeseries.rolling_cagr(self.df["price"])
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(self.df))

        result = timeseries.rolling_cagr(self.df["price"], years=3)
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(self.df))

    def test_rolling_cagr_known_values(self):
        # Test the rolling CAGR with known values
        # data starts with 1, and increases by 0.1% every day
        data = np.power(1.001, np.arange(1000))
        d1 = self.df.copy()
        d1["price"] = data

        for years in [1, 2, 3]:
            result = timeseries.rolling_cagr(
                d1["price"], years=years, snap_to_closest=True
            )
            self.assertIsInstance(result, pd.Series)
            self.assertEqual(len(result), len(d1))

            # all dates <= years should be NaN
            self.assertTrue(
                result.iloc[result.index < result.index[0] + pd.DateOffset(years=years)]
                .isna()
                .all()
            )
            # all dates > years should be non-NaN
            self.assertTrue(
                result.iloc[
                    result.index >= result.index[0] + pd.DateOffset(years=years)
                ]
                .notna()
                .all()
            )
            valid_values = result.iloc[
                result.index >= result.index[0] + pd.DateOffset(years=years)
            ]
            self.assertTrue(np.allclose(valid_values, 0.29, atol=1e-2))

    def test_non_datetime_index_error(self):
        # Test the rolling CAGR with a non-datetime index to trigger an error
        series = pd.Series(np.arange(1000))
        with self.assertRaises(AssertionError):
            timeseries.rolling_cagr(series)

    def test_rolling_cagr_long_window_error(self):
        # Test the rolling CAGR with a long window to trigger an error
        series = pd.Series(
            np.arange(1000),
            index=pd.date_range(start="2010-01-01", periods=1000, freq="B"),
        )
        result = timeseries.rolling_cagr(series, years=10)
        self.assertIsInstance(result, pd.Series)
        self.assertTrue(result.isna().all())

    def test_rolling_cagr_short_index_warning(self):
        # Test the rolling CAGR with a short index to trigger a warning
        short_df = self.df.iloc[:200]  # Less than 1 year of data
        with self.assertWarns(UserWarning):
            result = timeseries.rolling_cagr(short_df["price"])
            self.assertIsInstance(result, pd.Series)
            self.assertEqual(len(result), len(short_df))

    def test_rolling_cagr_edge_case(self):
        # Test the rolling CAGR with an edge case of exactly 1 year of data
        idx = self.df.index.get_loc(self.df.index[0] + pd.DateOffset(years=1))
        one_year_df = self.df.iloc[:idx]  # Exactly 1 year of data
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = timeseries.rolling_cagr(one_year_df["price"])
            self.assertIsInstance(result, pd.Series)
            self.assertEqual(len(result), len(one_year_df))

    def test_rolling_cagr_zero_values(self):
        # Test the rolling CAGR with zero values in the data
        zero_data = np.zeros(1000)
        zero_df = pd.DataFrame(zero_data, index=self.df.index, columns=["price"])
        result = timeseries.rolling_cagr(zero_df["price"])
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(zero_df))
        self.assertTrue(result.isna().all())

    def test_rolling_cagr_known_df(self):
        tickers = ["A", "B", "C"]
        bdays = 2000
        data = np.power(1.001, np.arange(bdays))
        data = np.tile(data, (len(tickers), 1)).T
        dates = pd.bdate_range(start="2020-01-01", periods=bdays)
        df = pd.DataFrame(data, index=dates, columns=tickers)

        # Calculate rolling CAGR for 3 years
        cagrs = timeseries.rolling_cagr(df, years=1, snap_to_closest=True)

        # assert that the result is a DataFrame
        # assert that the result has the same number of rows as the input
        self.assertIsInstance(cagrs, pd.DataFrame)
        self.assertEqual(len(cagrs), len(df))
        self.assertTrue(
            cagrs.iloc[cagrs.index < cagrs.index[0] + pd.DateOffset(years=1)]
            .isna()
            .all(axis=None)
        )
        valid_cagrs = cagrs.iloc[cagrs.index >= cagrs.index[0] + pd.DateOffset(years=1)]
        self.assertTrue(valid_cagrs.notna().all(axis=None))
        valid_cagrs = valid_cagrs.round(6)
        self.assertEqual(
            valid_cagrs.iloc[:, 0].nunique(),
            2,
            "Expected 2 unique values in the CAGR DataFrame, 261 & 262 bdays",
        )


if __name__ == "__main__":
    unittest.main()
