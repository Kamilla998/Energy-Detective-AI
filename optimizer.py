"""Simple transparent scheduling optimizer for the educational demo."""

def optimize_schedule(scenario):
    prices = scenario["prices"]
    solar = scenario["solar"]
    base_loads = scenario["base_loads"]
    grid_limit = scenario["grid_limit"]
    carbon_weight = scenario["carbon_weight"]
    tasks = scenario["appliances"]

    load_by_hour = list(base_loads)
    schedule = []
    violations = []

    # Prioritize long/high-power flexible tasks first.
    ordered = sorted(tasks, key=lambda task: task["power_kw"] * task["duration"], reverse=True)

    for task in ordered:
        duration = task["duration"]
        earliest = task["earliest"]
        latest_start = max(earliest, task["latest"] - duration + 1)
        possible_starts = range(earliest, latest_start + 1)

        def score(start):
            hours = list(range(start, start + duration))
            total = 0.0
            for hour in hours:
                estimated_grid = max(0.0, load_by_hour[hour] + task["power_kw"] - solar[hour])
                overload_penalty = max(0.0, estimated_grid - grid_limit) * 2.0
                carbon_penalty = carbon_weight * (1.0 if solar[hour] <= 0.1 else 0.2)
                total += prices[hour] * task["power_kw"] + overload_penalty + carbon_penalty
            return total

        best_start = min(possible_starts, key=score)
        hours = list(range(best_start, best_start + duration))
        for hour in hours:
            load_by_hour[hour] += task["power_kw"]
        schedule.append({
            "Appliance": task["name"],
            "Power (kW)": round(task["power_kw"], 2),
            "Duration (hours)": duration,
            "Start hour": best_start,
            "End hour": best_start + duration,
            "Flexible": "Yes" if task["flexible"] else "No",
            "Estimated energy (kWh)": round(task["power_kw"] * duration, 2),
        })

    for hour, load in enumerate(load_by_hour):
        grid_load = max(0.0, load - solar[hour])
        if grid_load > grid_limit:
            violations.append(f"Hour {hour:02d}: estimated grid load {grid_load:.2f} kW exceeds the {grid_limit:.2f} kW limit.")

    schedule.sort(key=lambda item: item["Start hour"])
    return schedule, load_by_hour, violations
