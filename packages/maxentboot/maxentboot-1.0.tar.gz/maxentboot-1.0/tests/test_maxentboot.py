#!/usr/bin/env python
"""Tests for `maxentboot` package."""

import numpy as np
import pandas as pd
import pytest
from click.testing import CliRunner

from maxentboot import cli
from maxentboot.maxentboot import maxentboot, trimmed_mean


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'maxentboot' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_trimmed_mean_basic():
    x = pd.Series([1, 2, 3, 4, 5])
    assert np.isclose(trimmed_mean(x), 2.5)


def test_trimmed_mean_custom_trim():
    x = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert np.isclose(trimmed_mean(x, trim=0.2), 5.5)


def test_trimmed_mean_extreme_values():
    x = pd.Series([1, 100, 2, 3, 4, 1000, 5])
    assert np.isclose(trimmed_mean(x), 19.17, rtol=1e-2)


@pytest.fixture
def sample_series():
    return pd.Series([1, 2, 3, 4, 5], index=['a', 'b', 'c', 'd', 'e'])


def test_maxentboot_basic(sample_series):
    result = maxentboot(sample_series, num_replicates=100)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 100)
    assert list(result.index) == ['a', 'b', 'c', 'd', 'e']


def test_maxentboot_preserves_range(sample_series):
    result = maxentboot(sample_series, num_replicates=100)
    min_orig, max_orig = sample_series.min(), sample_series.max()
    assert np.all(result.min() >= min_orig - 1)  # Allow small buffer
    assert np.all(result.max() <= max_orig + 1)  # Allow small buffer


def test_maxentboot_type_error():
    with pytest.raises(TypeError, match="`x` should be a pandas.Series"):
        maxentboot([1, 2, 3])


def test_maxentboot_preserves_order(sample_series):
    result = maxentboot(sample_series, num_replicates=100)
    assert list(result.index) == list(sample_series.index)


def test_maxentboot_random_seed():
    np.random.seed(42)
    series = pd.Series([1, 2, 3, 4, 5])
    result1 = maxentboot(series, num_replicates=10)
    np.random.seed(42)
    result2 = maxentboot(series, num_replicates=10)
    pd.testing.assert_frame_equal(result1, result2)


def test_maxentboot_different_trim():
    series = pd.Series([1, 2, 3, 4, 5])
    result = maxentboot(series, num_replicates=100, trim=0.2)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 100)


def test_maxentboot_empty_series():
    with pytest.raises(IndexError):
        maxentboot(pd.Series([]))


def test_maxentboot_single_value():
    with pytest.raises(IndexError):
        maxentboot(pd.Series([1]))


def test_maxentboot_numerical_stability():
    series = pd.Series([1e-10, 1e-9, 1e-8, 1e-7])
    result = maxentboot(series, num_replicates=100)
    assert not np.any(np.isnan(result.values))
    assert not np.any(np.isinf(result.values))
