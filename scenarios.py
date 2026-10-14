"""
Energy Detective AI
File 5: scenarios.py

Creates reproducible smart-home scenarios for the energy agent.
All scenarios are simulated; no real household data is required.
"""

from copy import deepcopy


HOURS = list(range(24))


def _base_prices():
    """Illustrative time-of-use tariff in currency units per kWh."""

    prices = []

    for hour in HOURS:
        if 0 <= hour < 6:
            price = 0.10
        elif 6 <= hour < 16:
            price = 0.19
        elif 16 <= hour < 21:
            price = 0.32
        else:
            price = 0.16

        prices.append(price)

    return prices


def _base_carbon_intensity():
    """Illustrative grid carbon intensity in kg CO2 per kWh."""

    values = []

    for hour in HOURS:
        if 10 <= hour < 16:
            values.append(0.24)
        elif 17 <= hour < 22:
            values.append(0.62)
        elif 0 <= hour < 6:
            values.append(0.38)
        else:
            values.append(0.48)

    return values


def _base_solar(capacity):
    """Approximate a bell-shaped daytime solar production curve."""

    shape = [
        0.00, 0.00, 0.00, 0.00, 0.00, 0.02,
        0.08, 0.20, 0.38, 0.58, 0.76, 0.92,
        1.00, 0.96, 0.82, 0.62, 0.38, 0.16,
        0.04, 0.00, 0.00, 0.00, 0.00, 0.00,
    ]

    return [
        round(capacity * factor, 3)
        for factor in shape
    ]


def _appliances():
    """
    Define flexible household jobs.

    earliest_start/latest_start are permitted start hours.
    duration is the number of consecutive hourly slots.
    """

    return [
        {
            "id": "ev",
            "name": "Electric Vehicle",
            "power": 3.3,
            "duration": 3,
            "earliest_start": 0,
            "latest_start": 5,
            "default_start": 17,
            "priority": "High",
        },
        {
            "id": "water_heater",
            "name": "Water Heater",
            "power": 2.0,
            "duration": 2,
            "earliest_start": 0,
            "latest_start": 5,
            "default_start": 18,
            "priority": "High",
        },
        {
            "id": "dishwasher",
            "name": "Dishwasher",
            "power": 1.2,
            "duration": 2,
            "earliest_start": 10,
            "latest_start": 21,
            "default_start": 18,
            "priority": "Medium",
        },
        {
            "id": "washing_machine",
            "name": "Washing Machine",
            "power": 0.8,
            "duration": 2,
            "earliest_start": 8,
            "latest_start": 20,
            "default_start": 17,
            "priority": "Medium",
        },
        {
            "id": "dryer",
            "name": "Clothes Dryer",
            "power": 2.5,
            "duration": 2,
            "earliest_start": 8,
            "latest_start": 21,
            "default_start": 19,
            "priority": "Medium",
        },
        {
            "id": "pool",
            "name": "Pool Pump",
            "power": 1.1,
            "duration": 3,
            "earliest_start": 8,
            "latest_start": 16,
            "default_start": 12,
            "priority": "Low",
        },
    ]


def get_scenario(
    scenario_name,
    peak_multiplier=3.0,
    solar_capacity=3.0,
    grid_limit=7.0,
    carbon_weight=0.0,
):
    """
    Return the configuration used by app.py and the agent.

    The scenario applies a consistent set of assumptions for
    tariffs, solar output, household load, and appliance jobs.
    """

    prices = _base_prices()
    solar = [0.0] * 24
    carbon = _base_carbon_intensity()

    base_load_kw = 0.7
    demand_charge = 0.0

    appliances = _appliances()

    # The baseline plan intentionally contains evening jobs.
    # The optimizer searches for better permitted start times.

    if scenario_name == "Normal Day":
        solar = _base_solar(solar_capacity)

    elif scenario_name == "Peak Price Crisis":
        solar = _base_solar(solar_capacity)

        for hour in range(16, 21):
            prices[hour] *= peak_multiplier

    elif scenario_name == "Heatwave":
        solar = _base_solar(solar_capacity)

        # Higher fixed demand represents cooling and refrigeration.
        base_load_kw = 2.0

        # Afternoon/evening cooling raises grid pressure.
        for hour in range(13, 22):
            prices[hour] *= 1.35

    elif scenario_name == "Solar Power Day":
        solar = _base_solar(max(solar_capacity, 4.0))

        # Midday electricity is modeled as less expensive.
        for hour in range(10, 16):
            prices[hour] *= 0.65

    elif scenario_name == "Grid Overload":
        solar = _base_solar(solar_capacity)

        # A tighter grid limit challenges the schedule optimizer.
        grid_limit = min(float(grid_limit), 5.0)
        base_load_kw = 1.0

    elif scenario_name == "Carbon Challenge":
        solar = _base_solar(solar_capacity)

        # Increase the importance of the emissions objective.
        carbon_weight = max(float(carbon_weight), 0.8)

    else:
        raise ValueError(
            f"Unknown scenario: {scenario_name}"
        )

    # Keep the original schedule inside the day so its initial
    # cost can be evaluated even when it violates capacity limits.
    # The optimizer may subsequently move jobs to permitted hours.

    return {
        "name": scenario_name,
        "appliances": deepcopy(appliances),
        "prices": prices,
        "solar": solar,
        "carbon_intensity": carbon,
        "base_load_kw": base_load_kw,
        "grid_limit": float(grid_limit),
        "carbon_weight": float(carbon_weight),
        "demand_charge": demand_charge,
    }
