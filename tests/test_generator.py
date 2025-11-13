import pytest
import pandas as pd
from src.generator import generate_prices

def test_generate_prices_length():
    df = generate_prices(n=100)
    assert len(df) == 100

def test_generate_prices_positive():
    df = generate_prices(n=100)
    assert all(df['price'] > 0)

def test_generate_prices_columns():
    df = generate_prices(n=100)
    assert list(df.columns) == ['timestamp', 'symbol', 'price']

def test_generate_prices_reproducible():
    df1 = generate_prices(n=100, seed=42)
    df2 = generate_prices(n=100, seed=42)
    pd.testing.assert_frame_equal(df1, df2)
