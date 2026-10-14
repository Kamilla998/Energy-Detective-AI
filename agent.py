"""Transparent rule-based AI-agent simulation."""

from optimizer import optimize_schedule

class EnergyDetectiveAgent:
    def __init__(self, scenario):
        self.scenario = scenario

    def investigate(self):
        scenario = self.scenario
        schedule, optimized_load, violations = optimize_schedule(scenario)
        prices = scenario["prices"]
        solar = scenario["solar"]
        base_loads = scenario["base_loads"]
        appliances = scenario["appliances"]

        peak_hours = [hour for hour, price in enumerate(prices) if price >= max(prices) * 0.8]
        solar_hours = [hour for hour, amount in enumerate(solar) if amount > 0.5]
        flexible_count = sum(1 for task in appliances if task["flexible"])

        decisions = [
            {
                "title": "Observe the energy environment",
                "details": f"The agent loaded the '{scenario['name']}' scenario, 24 hourly electricity prices, estimated household base loads, and solar generation."
            },
            {
                "title": "Detect expensive periods",
                "details": "Higher-price hours detected: " + (", ".join(f"{hour:02d}:00" for hour in peak_hours) if peak_hours else "none") + ". Flexible appliances should avoid these periods when practical."
            },
            {
                "title": "Check renewable energy availability",
                "details": "Hours with useful simulated solar generation: " + (", ".join(f"{hour:02d}:00" for hour in solar_hours) if solar_hours else "none") + ". The scheduler prefers these hours when the score is lower."
            },
            {
                "title": "Optimize appliance schedule",
                "details": f"The scheduler compared candidate start times for {len(appliances)} appliances, prioritizing energy cost, grid-limit penalties, and the carbon-reduction setting. {flexible_count} appliances are marked flexible."
            },
            {
                "title": "Validate grid constraints",
                "details": "The agent checked each hour against the configured grid limit after accounting for simulated solar generation. " + (f"{len(violations)} potential limit violation(s) were found." if violations else "No grid-limit violations were found.")
            },
        ]

        summary = (
            f"For the '{scenario['name']}' scenario, the agent created a schedule for {len(schedule)} appliances. "
            "Compare the estimated bill before and after optimization; results are educational estimates based on simulated data, not live meter readings."
        )
        return {
            "schedule": schedule,
            "optimized_load": optimized_load,
            "constraint_violations": violations,
            "decisions": decisions,
            "summary": summary,
        }
