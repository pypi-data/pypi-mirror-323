# %%
from pathlib import Path
from IPython.display import display, display_markdown as displaymd
import yfinance as yf
import pandas as pd
from tabulate import tabulate
from grynn_pylib.finance import timeseries as ts

tickers = ["QQQ", "QQQE", "SPY", "XLK", "VGT", "IWM", "ROM", "QLD", "SSO", "TQQQ"]
period = "10y"
# since yf 0.2.51 auto_adjust defaults to True and download/history do not return "Adj Close"
# https://github.com/copilot/c/5f0930d5-0652-426e-a1fd-6da47b081c6c
# https://github.com/ranaroussi/yfinance/issues/2219#issuecomment-2585580123
df = yf.download(tickers, period=period)
df = df["Close"]
start_date = df.index[0]
end_date = df.index[-1]
print(f"Data from {start_date} to {end_date} downloaded.")
display(df.head())

# %%
years = [3, 5, 7]
displaymd("## Rolling Median CAGR", raw=True)
displaymd(f"### From {df.index[0].date()} to {df.index[-1].date()}", raw=True)
d2 = pd.DataFrame({f"{k}yrs": ts.rolling_cagr(df, years=k, snap_to_closest=True).median() for k in years})
print(tabulate(d2.round(4) * 100, headers="keys", tablefmt="pipe", floatfmt=".2f"))

displaymd("## Min CAGR", raw=True)
displaymd(f"### From {df.index[0].date()} to {df.index[-1].date()}", raw=True)
min_cagrs = pd.DataFrame({f"{k}yrs": ts.rolling_cagr(df, years=k, snap_to_closest=True).min() for k in years})
print(tabulate(min_cagrs.round(4) * 100, headers="keys", tablefmt="pipe", floatfmt=".2f"))

with pd.ExcelWriter("rolling_median_cagr.xlsx", engine="xlsxwriter") as writer:
    # First write the DataFrames to create the worksheet
    d2.to_excel(writer, sheet_name="Rolling CAGR", startrow=2, startcol=0)
    min_cagrs.to_excel(writer, sheet_name="Rolling CAGR", startrow=2, startcol=d2.shape[1] + 3)

    # After writing, get the workbook and worksheet
    workbook = writer.book
    worksheet = writer.sheets["Rolling CAGR"]

    # Add formats
    line_format = workbook.add_format({"left": 1})
    header_format = workbook.add_format({"bold": True, "font_size": 12})

    # Apply formats and headers
    worksheet.write(0, 0, "Rolling Median CAGR", header_format)
    worksheet.write(0, d2.shape[1] + 3, "Minimum CAGR", header_format)
    worksheet.set_column(d2.shape[1] + 2, d2.shape[1] + 2, None, line_format)

p = Path("rolling_median_cagr.xlsx")
print(f"Saved to '{p.absolute()}'")
