import pytest
from grynn_pylib.finance import options


def test_bs_d1_d2():
    # Sample inputs
    S = 100  # Stock price
    K = 100  # Strike price
    T = 1  # Time to maturity
    r = 0.05  # Risk-free rate
    sigma = 0.2  # Volatility

    # Expected outputs (calculated using a known implementation)
    expected_d1 = 0.35
    expected_d2 = 0.15

    # Call the function
    d1, d2 = options.bs_d1_d2(S, K, T, r, sigma)

    # Assert the results
    assert d1 == pytest.approx(expected_d1, abs=1e-2)
    assert d2 == pytest.approx(expected_d2, abs=1e-2)


def test_bs_delta():
    # Sample inputs
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2

    # Expected outputs
    expected_call_delta = 0.6368
    expected_put_delta = -0.3632

    # Call the function
    call_delta = options.bs_delta(S, K, T, r, sigma, option_type="call")
    put_delta = options.bs_delta(S, K, T, r, sigma, option_type="put")

    # Assert the results
    assert call_delta == pytest.approx(expected_call_delta, abs=1e-4)
    assert put_delta == pytest.approx(expected_put_delta, abs=1e-4)


def test_bs_gamma():
    # Sample inputs
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2

    # Expected output
    expected_gamma = 0.0188

    # Call the function
    gamma = options.bs_gamma(S, K, T, r, sigma)

    # Assert the result
    assert gamma == pytest.approx(expected_gamma, abs=1e-4)


def test_bs_theta():
    # Sample inputs
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2

    # Expected outputs
    expected_call_theta = -0.0176
    expected_put_theta = -0.0045

    # Call the function
    call_theta = options.bs_theta(S, K, T, r, sigma, option_type="call")
    put_theta = options.bs_theta(S, K, T, r, sigma, option_type="put")

    # Assert the results
    assert call_theta == pytest.approx(expected_call_theta, abs=1e-4)
    assert put_theta == pytest.approx(expected_put_theta, abs=1e-4)


def test_bs_omega():
    # Sample inputs
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2
    option_price = 10.4506

    # Expected outputs
    expected_call_omega = 6.094
    expected_put_omega = -3.475

    # Call the function
    call_omega = options.bs_omega(S, K, T, r, sigma, option_price, option_type="call")
    put_omega = options.bs_omega(S, K, T, r, sigma, option_price, option_type="put")

    # Assert the results
    assert call_omega == pytest.approx(expected_call_omega, abs=1e-3)
    assert put_omega == pytest.approx(expected_put_omega, abs=1e-3)


def test_bs_omega_short_put():
    # Sample inputs
    S = 100
    K = 100
    T = 1
    r = 0.05
    sigma = 0.2
    option_price = 10.4506

    # Expected output
    expected_omega_short_put = 3.475

    # Call the function
    omega_short_put = options.bs_omega_short_put(S, K, T, r, sigma, option_price)

    # Assert the result
    assert omega_short_put == pytest.approx(expected_omega_short_put, abs=1e-3)


def test_short_payoff_put_percent():
    # Sample inputs
    S = 90
    K = 100
    premium = 5

    # Expected output
    expected_payoff = -0.0526

    # Call the function
    payoff = options.payoff_short_put_percent(S, K, premium)

    # Assert the result
    assert payoff == pytest.approx(expected_payoff, abs=1e-4)

    S = 110
    expected_payoff = 0.0526
    payoff = options.payoff_short_put_percent(S, K, premium)
    assert payoff == pytest.approx(expected_payoff, abs=1e-4)
