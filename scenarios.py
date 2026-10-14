"""Scenario data and configuration for Energy Detective AI."""

SCENARIO_NAMES = [
    "Normal Day",
    "Peak Price Crisis",
    "Heatwave",
    "Solar Power Day",
    "Grid Overload",
    "Carbon Challenge",
]

APPLIANCES = [
    {"name": "Electric vehicle", "power_kw": 3.3, "duration": 3, "earliest": 0, "latest": 23, "flexible": True},
    {"name": "Water heater", "power_kw": 2.0, "duration": 2, "earliest": 5, "latest": 22, "flexible": True},
    {"name": "Air conditioner", "power_kw": 1.5, "duration": 8, "earliest": 10, "latest": 21, "flexible": False},
    {"name": "Dishwasher", "power_kw": 1.2, "duration": 2, "earliest": 0, "latest": 23, "flexible": True},
    {"name": "Washing machine", "power_kw": 0.8, "duration": 2, "earliest": 0, "latest": 23, "flexible": True},
    {"name": "Clothes dryer", "power_kw": 2.5, "duration": 2, "earliest": 0, "latest": 23, "flexible": True},
]

def get_scenario(scenario_name, peak_multiplier=3.0, solar_capacity=3.0, grid_limit=7.0, carbon_weight=0.3):
    """Create a scenario with 24 hourly prices, base loads, and appliance tasks."""
    base_prices = [0.12] * 24
    for hour in range(0, 6):
        base_prices[hour] = 0.08
    for hour in range(17, 22):
        base_prices[hour] = 0.12 * peak_multiplier

    base_loads = [0.45] * 24
    for hour in range(10, 21):
        base_loads[hour] += 1.5

    solar = [0.0] * 24
    for hour, value in [(8, 0.3), (9, 0.8), (10, 1.5), (11, 2.3), (12, 3.0),
                        (13, 3.4), (14, 3.0), (15, 2.2), (16, 1.2), (17, 0.4)]:
        solar[hour] = min(value, solar_capacity)

    appliances = [dict(item) for item in APPLIANCES]
    if scenario_name == "Heatwave":
        base_loads = [load + (1.0 if 11 <= hour <= 19 else 0.0) for hour, load in enumerate(base_loads)]
    elif scenario_name == "Solar Power Day":
        base_prices = [price * 0.9 for price in base_prices]
    elif scenario_name == "Grid Overload":
        base_loads = [load + (1.5 if 17 <= hour <= 21 else 0.0) for hour, load in enumerate(base_loads)]
    elif scenario_name == "Carbon Challenge":
        # Lower-carbon hours are approximated as midday hours with solar availability.
        pass
    elif scenario_name == "Normal Day":
        for hour in range(17, 22):
            base_prices[hour] = 0.18

    return {
        "name": scenario_name,
        "prices": base_prices,
        "base_loads": base_loads,
        "solar": solar,
        "solar_capacity": solar_capacity,
        "grid_limit": grid_limit,
        "carbon_weight": carbon_weight,
        "appliances": appliances,
    }
