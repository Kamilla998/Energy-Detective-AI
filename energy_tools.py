"""Calculations and reporting tools used by the Energy Detective agent."""

def calculate_energy_report(scenario, result):
    prices = scenario["prices"]
    solar = scenario["solar"]
    base_loads = scenario["base_loads"]
    optimized_load = result["optimized_load"]

    original_load = list(base_loads)
    for task in scenario["appliances"]:
        # Simulated baseline: run flexible tasks during the evening where possible.
        if task["flexible"]:
            start = min(max(17, task["earliest"]), task["latest"] - task["duration"] + 1)
        else:
            start = task["earliest"]
        for hour in range(start, min(start + task["duration"], 24)):
            original_load[hour] += task["power_kw"]

    def totals(loads):
        grid = [max(0.0, loads[h] - solar[h]) for h in range(24)]
        energy = sum(grid)
        cost = sum(grid[h] * prices[h] for h in range(24))
        peak = max(grid) if grid else 0.0
        return {
            "energy_kwh": round(energy, 2),
            "total_cost": round(cost, 2),
            "peak_kw": round(peak, 2),
            "hourly_grid": grid,
        }

    original = totals(original_load)
    optimized = totals(optimized_load)
    hourly_comparison = []
    for hour in range(24):
        hourly_comparison.append({
            "hour": f"{hour:02d}:00",
            "price": round(prices[hour], 3),
            "original_load": round(original["hourly_grid"][hour], 2),
            "optimized_load": round(optimized["hourly_grid"][hour], 2),
            "solar_generation": round(solar[hour], 2),
        })

    return {
        "original": original,
        "optimized": optimized,
        "hourly_comparison": hourly_comparison,
    }
