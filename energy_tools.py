"""
Energy Detective AI
File 4: energy_tools.py

Core calculation tools:
- Hourly household load profile
- Solar generation accounting
- Electricity bill estimation
- Carbon emissions estimation
- Appliance scheduling validation
"""

from collections import defaultdict


HOURS_PER_DAY = 24


def _active_hours(start_hour, duration):
    """Return the hours occupied by a job in a 24-hour day."""

    return [
        (start_hour + offset) % HOURS_PER_DAY
        for offset in range(duration)
    ]


def build_load_profile(
    appliances,
    starts,
    base_load_kw,
):
    """
    Build the total household load for each hour.

    The profile includes the fixed background load and all
    scheduled appliance loads. Solar generation is handled
    separately when calculating grid imports.
    """

    load = [float(base_load_kw) for _ in range(HOURS_PER_DAY)]

    for appliance in appliances:
        appliance_id = appliance["id"]
        start_hour = int(starts[appliance_id])
        duration = int(appliance["duration"])
        power = float(appliance["power"])

        for hour in _active_hours(start_hour, duration):
            load[hour] += power

    return load


def calculate_schedule_metrics(
    appliances,
    starts,
    prices,
    solar,
    base_load_kw,
    carbon_intensity,
    demand_charge,
    carbon_weight,
):
    """
    Calculate energy, estimated bill, peak demand, emissions,
    and a combined optimization objective.

    Prices are currency units per kWh.
    Solar and household loads are expressed in kW.
    Each time slot represents one hour.
    """

    load = build_load_profile(
        appliances=appliances,
        starts=starts,
        base_load_kw=base_load_kw,
    )

    grid_import = []
    grid_export = []
    total_cost = 0.0
    total_energy = 0.0
    total_emissions = 0.0

    for hour in range(HOURS_PER_DAY):
        household_load = load[hour]
        solar_generation = float(solar[hour])

        imported = max(
            0.0,
            household_load - solar_generation,
        )

        exported = max(
            0.0,
            solar_generation - household_load,
        )

        price = float(prices[hour])
        intensity = float(carbon_intensity[hour])

        grid_import.append(imported)
        grid_export.append(exported)

        total_energy += imported

        # Only imported grid electricity incurs this modeled charge.
        total_cost += imported * price

        # Carbon intensity is measured in kg CO2 per kWh.
        total_emissions += imported * intensity

    peak_kw = max(grid_import, default=0.0)

    # Demand charges represent a simplified daily peak charge.
    total_cost += peak_kw * float(demand_charge)

    # Carbon weight is a transparent educational objective term.
    # It is not an electricity tariff.
    objective = (
        total_cost
        + float(carbon_weight) * total_emissions
    )

    return {
        "energy_kwh": round(total_energy, 4),
        "total_cost": round(total_cost, 4),
        "peak_kw": round(peak_kw, 4),
        "emissions_kg": round(total_emissions, 4),
        "objective": round(objective, 6),
        "hourly_load": [
            round(value, 4) for value in load
        ],
        "hourly_grid_import": [
            round(value, 4) for value in grid_import
        ],
        "hourly_solar": [
            round(float(value), 4) for value in solar
        ],
    }


def check_constraints(
    appliances,
    starts,
    load_profile,
    grid_limit,
):
    """
    Validate appliance start windows, duration, and hourly
    grid import capacity.

    Return a list of human-readable violations.
    """

    violations = []

    if len(load_profile) != HOURS_PER_DAY:
        violations.append(
            "The load profile must contain exactly 24 hourly values."
        )
        return violations

    for appliance in appliances:
        appliance_id = appliance["id"]

        if appliance_id not in starts:
            violations.append(
                f"{appliance['name']}: no start time was provided."
            )
            continue

        start = starts[appliance_id]
        earliest = appliance["earliest_start"]
        latest = appliance["latest_start"]
        duration = appliance["duration"]

        if not isinstance(start, int) or isinstance(start, bool):
            violations.append(
                f"{appliance['name']}: start time must be an integer hour."
            )
            continue

        if start < earliest or start > latest:
            violations.append(
                f"{appliance['name']}: start time {start}:00 is outside "
                f"the permitted window {earliest}:00–{latest}:00."
            )

        if duration < 1 or duration > HOURS_PER_DAY:
            violations.append(
                f"{appliance['name']}: invalid job duration."
            )

        if start + duration > HOURS_PER_DAY:
            violations.append(
                f"{appliance['name']}: the job extends beyond midnight."
            )

    for hour, load in enumerate(load_profile):
        if load > grid_limit + 1e-9:
            violations.append(
                f"Grid capacity exceeded at {hour:02d}:00: "
                f"{load:.2f} kW exceeds {grid_limit:.2f} kW."
            )

    return violations


def calculate_energy_report(
    scenario,
    result,
):
    """
    Produce the baseline-versus-optimized report consumed by app.py.
    """

    appliances = scenario["appliances"]
    prices = scenario["prices"]
    solar = scenario["solar"]
    base_load_kw = scenario["base_load_kw"]
    carbon_intensity = scenario["carbon_intensity"]
    demand_charge = scenario["demand_charge"]
    carbon_weight = scenario["carbon_weight"]

    original = calculate_schedule_metrics(
        appliances=appliances,
        starts=result["original_starts"],
        prices=prices,
        solar=solar,
        base_load_kw=base_load_kw,
        carbon_intensity=carbon_intensity,
        demand_charge=demand_charge,
        carbon_weight=carbon_weight,
    )

    optimized = calculate_schedule_metrics(
        appliances=appliances,
        starts=result["optimized_starts"],
        prices=prices,
        solar=solar,
        base_load_kw=base_load_kw,
        carbon_intensity=carbon_intensity,
        demand_charge=demand_charge,
        carbon_weight=carbon_weight,
    )

    hourly_comparison = []

    for hour in range(HOURS_PER_DAY):
        hourly_comparison.append({
            "hour": f"{hour:02d}:00",
            "price": round(float(prices[hour]), 4),
            "solar": round(float(solar[hour]), 4),
            "original_load": round(
                original["hourly_grid_import"][hour], 4
            ),
            "optimized_load": round(
                optimized["hourly_grid_import"][hour], 4
            ),
        })

    return {
        "original": original,
        "optimized": optimized,
        "hourly_comparison": hourly_comparison,
    }
