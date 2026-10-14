
"""
Energy Detective AI
File 2: agent.py

The agent coordinates investigation, scheduling, validation,
evaluation, and explanation for the simulated smart home.
"""

from optimizer import optimize_schedule
from energy_tools import (
    build_load_profile,
    calculate_schedule_metrics,
    check_constraints,
)


class EnergyDetectiveAgent:
    """Investigate a home energy scenario and propose a better plan."""

    def __init__(self, scenario):
        self.scenario = scenario
        self.decisions = []

    def log_decision(self, title, details):
        """Record a measurable action in the agent's audit log."""
        self.decisions.append({
            "title": title,
            "details": details,
        })

    def investigate(self):
        """Run the complete agent workflow."""

        scenario = self.scenario
        appliances = scenario["appliances"]
        prices = scenario["prices"]
        solar = scenario["solar"]
        carbon_intensity = scenario["carbon_intensity"]

        base_load_kw = scenario["base_load_kw"]
        grid_limit = scenario["grid_limit"]
        carbon_weight = scenario["carbon_weight"]
        demand_charge = scenario["demand_charge"]

        # --------------------------------------------------
        # STEP 1: OBSERVE THE HOME
        # --------------------------------------------------

        self.log_decision(
            "Observe: inspect the home",
            (
                f"The agent received {len(appliances)} appliance jobs. "
                f"The fixed background load is {base_load_kw:.2f} kW, "
                f"and the configured grid limit is {grid_limit:.2f} kW."
            ),
        )

        # --------------------------------------------------
        # STEP 2: INVESTIGATE ELECTRICITY PRICES
        # --------------------------------------------------

        expensive_hours = sorted(
            range(24),
            key=lambda hour: prices[hour],
            reverse=True,
        )[:5]

        expensive_text = ", ".join(
            f"{hour:02d}:00 (${prices[hour]:.3f}/kWh)"
            for hour in expensive_hours
        )

        ranked_appliances = sorted(
            appliances,
            key=lambda appliance: (
                appliance["power"] * appliance["duration"]
            ),
            reverse=True,
        )

        biggest_consumers = ", ".join(
            (
                f"{appliance['name']} "
                f"({appliance['power'] * appliance['duration']:.1f} kWh)"
            )
            for appliance in ranked_appliances[:3]
        )

        self.log_decision(
            "Investigate: identify expensive periods",
            (
                f"The five most expensive hours are: {expensive_text}. "
                f"The three largest controllable energy consumers are: "
                f"{biggest_consumers}."
            ),
        )

        # --------------------------------------------------
        # STEP 3: BUILD THE ORIGINAL SCHEDULE
        # --------------------------------------------------

        original_starts = {
            appliance["id"]: appliance["default_start"]
            for appliance in appliances
        }

        original_load = build_load_profile(
            appliances=appliances,
            starts=original_starts,
            base_load_kw=base_load_kw,
        )

        original_metrics = calculate_schedule_metrics(
            appliances=appliances,
            starts=original_starts,
            prices=prices,
            solar=solar,
            base_load_kw=base_load_kw,
            carbon_intensity=carbon_intensity,
            demand_charge=demand_charge,
            carbon_weight=carbon_weight,
        )

        original_errors = check_constraints(
            appliances=appliances,
            starts=original_starts,
            load_profile=original_load,
            grid_limit=grid_limit,
        )

        self.log_decision(
            "Establish baseline",
            (
                f"The original simulated bill is "
                f"${original_metrics['total_cost']:.2f}. "
                f"Peak demand is {original_metrics['peak_kw']:.2f} kW. "
                f"The original schedule has {len(original_errors)} "
                f"constraint violation(s)."
            ),
        )

        # --------------------------------------------------
        # STEP 4: PLAN A BETTER SCHEDULE
        # --------------------------------------------------

        optimized_starts, optimization_log = optimize_schedule(
            appliances=appliances,
            initial_starts=original_starts,
            prices=prices,
            solar=solar,
            base_load_kw=base_load_kw,
            carbon_intensity=carbon_intensity,
            demand_charge=demand_charge,
            carbon_weight=carbon_weight,
            grid_limit=grid_limit,
        )

        optimized_load = build_load_profile(
            appliances=appliances,
            starts=optimized_starts,
            base_load_kw=base_load_kw,
        )

        optimized_metrics = calculate_schedule_metrics(
            appliances=appliances,
            starts=optimized_starts,
            prices=prices,
            solar=solar,
            base_load_kw=base_load_kw,
            carbon_intensity=carbon_intensity,
            demand_charge=demand_charge,
            carbon_weight=carbon_weight,
        )

        optimized_errors = check_constraints(
            appliances=appliances,
            starts=optimized_starts,
            load_profile=optimized_load,
            grid_limit=grid_limit,
        )

        self.log_decision(
            "Plan: optimize appliance start times",
            (
                f"The scheduling optimizer accepted "
                f"{len(optimization_log)} improving move(s). "
                f"The optimized schedule contains "
                f"{len(optimized_errors)} constraint violation(s)."
            ),
        )

        # --------------------------------------------------
        # STEP 5: COMPARE THE RESULTS
        # --------------------------------------------------

        savings = (
            original_metrics["total_cost"]
            - optimized_metrics["total_cost"]
        )

        if original_metrics["total_cost"] > 0:
            savings_percent = (
                savings / original_metrics["total_cost"]
            ) * 100
        else:
            savings_percent = 0.0

        energy_change = (
            original_metrics["energy_kwh"]
            - optimized_metrics["energy_kwh"]
        )

        emissions_change = (
            original_metrics["emissions_kg"]
            - optimized_metrics["emissions_kg"]
        )

        self.log_decision(
            "Evaluate: measure the improvement",
            (
                f"Estimated bill change: ${savings:.2f} "
                f"({savings_percent:.1f}%). "
                f"Change in household energy use: "
                f"{energy_change:.2f} kWh. "
                f"Change in grid emissions: "
                f"{emissions_change:.2f} kg CO2."
            ),
        )

        # --------------------------------------------------
        # STEP 6: EXPLAIN THE NEW SCHEDULE
        # --------------------------------------------------

        schedule = []

        for appliance in appliances:
            appliance_id = appliance["id"]

            old_start = original_starts[appliance_id]
            new_start = optimized_starts[appliance_id]

            finish_hour = (
                new_start + appliance["duration"]
            )

            schedule.append({
                "Appliance": appliance["name"],
                "Power (kW)": appliance["power"],
                "Duration (hours)": appliance["duration"],
                "Original start": f"{old_start:02d}:00",
                "Recommended start": f"{new_start:02d}:00",
                "Finish": (
                    f"{finish_hour:02d}:00"
                    if finish_hour < 24
                    else "24:00"
                ),
                "Shift (hours)": new_start - old_start,
                "Priority": appliance["priority"],
            })

        changed_appliances = [
            item for item in schedule
            if item["Shift (hours)"] != 0
        ]

        if changed_appliances:
            change_summary = "; ".join(
                (
                    f"{item['Appliance']}: "
                    f"{item['Original start']} → "
                    f"{item['Recommended start']}"
                )
                for item in changed_appliances
            )
        else:
            change_summary = (
                "No start-time changes were accepted. "
                "The existing schedule may already be locally optimal "
                "under the current constraints."
            )

        if optimized_errors:
            recommendation = (
                "The optimizer could not find a fully feasible plan. "
                "Review the grid limit and appliance operating windows "
                "before using the proposed schedule."
            )
        elif savings > 0.005:
            recommendation = (
                f"The proposed schedule reduces the modeled daily "
                f"electricity bill by ${savings:.2f}. "
                f"Estimated reduction: {savings_percent:.1f}%. "
                f"Changes: {change_summary}"
            )
        elif savings < -0.005:
            recommendation = (
                f"The proposed plan has a modeled bill increase of "
                f"${abs(savings):.2f}. The optimizer may be balancing "
                "other objective terms or responding to constraints. "
                "Review the scenario settings."
            )
        else:
            recommendation = (
                "No material bill reduction was found. "
                f"Schedule changes: {change_summary}"
            )

        self.log_decision(
            "Explain: generate the recommendation",
            recommendation,
        )

        # --------------------------------------------------
        # FINAL AGENT OUTPUT
        # --------------------------------------------------

        return {
            "original_starts": original_starts,
            "optimized_starts": optimized_starts,
            "original_metrics": original_metrics,
            "optimized_metrics": optimized_metrics,
            "original_errors": original_errors,
            "constraint_violations": optimized_errors,
            "decisions": self.decisions,
            "schedule": schedule,
            "optimization_log": optimization_log,
            "summary": recommendation,
        }
