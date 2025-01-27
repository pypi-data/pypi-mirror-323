import os
import pathlib

MICKELONIUS_PKG_DIR = pathlib.Path(__file__).parent.absolute() # /data1/repos/ml/ml
MICKELONIUS_DIR = pathlib.Path(__file__).parent.parent.absolute() # /data1/repos/ml
MICKELONIUS_TEST_DATA_DIR = os.environ.get("MICKELONIUS_TEST_DATA_DIR", MICKELONIUS_DIR / "test/data")
MICKELONIUS_DATA_DIR = os.environ.get("MICKELONIUS_DATA_DIR", MICKELONIUS_DIR / "data")

