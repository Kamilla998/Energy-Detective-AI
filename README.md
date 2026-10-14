# ⚡ Energy Detective AI
## The Smart Home Energy Optimization Agent

Energy Detective AI is an interactive educational project that
investigates electricity consumption in a simulated smart home.

The agent analyzes electricity prices, appliance schedules,
solar generation, grid limits, and carbon intensity. It then
searches for a better appliance schedule and explains its decisions.

## Main Features

- Interactive Streamlit dashboard
- Six simulated energy scenarios
- Time-of-use electricity pricing
- Peak-price crisis simulation
- Smart appliance scheduling
- Solar generation simulation
- Grid capacity constraint checking
- Estimated electricity bill comparison
- Carbon emissions estimation
- Agent decision log
- Downloadable JSON and CSV reports

## Technology Stack

- Python
- Streamlit
- Pandas
- Search-based optimization

## Project Structure

    Energy-Detective-AI/
    ├── app.py
    ├── agent.py
    ├── optimizer.py
    ├── energy_tools.py
    ├── scenarios.py
    ├── requirements.txt
    └── README.md

## How the Agent Works

### 1. Observe

The agent receives the simulated household configuration,
appliance requirements, electricity prices, and grid limits.

### 2. Investigate

It identifies expensive electricity periods and ranks
appliances by their estimated energy consumption.

### 3. Plan

The optimizer searches for alternative appliance start times.

### 4. Validate

Candidate schedules are checked against permitted operating
windows and the configured grid capacity.

### 5. Evaluate

The agent compares estimated costs, grid consumption,
peak demand, and carbon emissions.

### 6. Explain

The application presents the proposed schedule, accepted
changes, and an investigation report.

## Available Scenarios

1. Normal Day
2. Peak Price Crisis
3. Heatwave
4. Solar Power Day
5. Grid Overload
6. Carbon Challenge

## Requirements

- Python 3.10 or newer
- pip

## Installation

Clone this repository:

    git clone https://github.com/YOUR_USERNAME/energy-detective-ai.git

Enter the project directory:

    cd energy-detective-ai

Create a virtual environment:

    python -m venv .venv

Activate it on Windows PowerShell:

    .venv\Scripts\Activate.ps1

On macOS or Linux:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Start the application:

    streamlit run app.py

Open the local address shown in the terminal.

## Practical Demo

1. Choose Peak Price Crisis.
2. Increase the peak price multiplier.
3. Run the investigation.
4. Inspect the original and optimized bills.
5. Review the recommended appliance schedule.
6. Open the decision log.
7. Download the JSON or CSV report.
8. Compare the results with another scenario.

## Important Limitations

This project is an educational simulation.

Its electricity tariffs, household loads, solar generation,
and carbon intensity values are illustrative rather than live data.

The optimizer uses a heuristic search algorithm. It may not find
the globally optimal schedule, and some scenarios may have no
feasible schedule under the selected constraints.

The application does not connect to or control real appliances.
Its estimated savings are not guaranteed real-world savings.

## Future Improvements

- Real electricity price forecasting
- Weather-based solar prediction
- Battery storage scheduling
- Electric vehicle charging optimization
- Smart-meter data import
- Natural-language household instructions
- Optional integration with a language model

## License

MIT
