import subprocess
import tempfile
from loguru import logger
import pandas as pd


def bcompare_frames(a: pd.DataFrame, b: pd.DataFrame):
    """
    Diff two dataframes (a and b) using Beyond Compare (wait for user to close the window)
    """
    aname = "a"
    bname = "b"

    if (a.index.name is not None) and (a.index.name != ""):
        aname = a.index.name

    if (b.index.name is not None) and (b.index.name != ""):
        bname = b.index.name

    if (a.columns.name is not None) and (a.columns.name != ""):
        aname = a.columns.name

    if (b.columns.name is not None) and (b.columns.name != ""):
        bname = b.columns.name

    with tempfile.NamedTemporaryFile(suffix=".csv", prefix=aname, delete=True) as temp1:
        with tempfile.NamedTemporaryFile(
            suffix=".csv", prefix=bname, delete=True
        ) as temp2:
            a.to_csv(temp1.name)
            b.to_csv(temp2.name)
            logger.debug(f"Temp files: {aname}: {temp1.name},\n{bname}: {temp2.name}")
            subprocess.run(["bcomp", temp1.name, temp2.name])
            # subprocess.run waits for the process to complete
            # bcomp in turn waits for the user to close the comparison window


def bcompare(
    a: pd.Series | pd.DataFrame | pd.Index, b: pd.Series | pd.DataFrame | pd.Index
):
    """
    Diff two series or dataframes using Beyond Compare (wait for user to close the window)
    """
    # promote index to series and series to dataframe
    if isinstance(a, pd.Index):
        a = a.to_series()
    if isinstance(b, pd.Index):
        b = b.to_series()
    # convert series to dataframes with frame.index.name | frame.columns.name = series.name
    if isinstance(a, pd.Series):
        a = pd.DataFrame(a)
    if isinstance(b, pd.Series):
        b = pd.DataFrame(b)
    bcompare_frames(a, b)
