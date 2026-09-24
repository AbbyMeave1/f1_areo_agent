# F1 Agent

An AI agent for analyzing Formula 1 aerodynamics, tyres, car performance, and general F1 topics using physics calculations, knowledge base, and **real-world race data** (Fast-F1 enabled by default).

## Overview

This agent provides comprehensive F1 analysis across multiple domains:
- **Aerodynamics**: Mathematically rigorous calculations using standard aerodynamic equations
- **Tyres**: Compound characteristics, degradation, and strategy recommendations
- **Car Performance**: Speed, braking, telemetry (with Fast-F1 integration)
- **General F1**: Tracks, racing concepts, and F1 knowledge
- **Physics backend abstraction** designed for IBM chuk-mcp-physics MCP server integration
- **Local visualizations** saved as PNG files using matplotlib
- **CLI interface** with single-question and interactive modes
- **Intelligent routing** with fallback for unsupported questions

## Features

### Supported Question Categories

#### 1. Aerodynamics (Original Functionality)

**Front Wing Downforce vs Speed**
- Calculates downforce generation across speed range
- Shows quadratic relationship with velocity
- Visualizes downforce curves

**Drag Force at Speed**
- Computes total drag force at specified speed
- Supports DRS (Drag Reduction System) open/closed comparison
- Always saves an explanatory drag-vs-speed graph with the queried point highlighted

**DRS Drag Reduction Comparison**
- Compares drag with DRS open vs closed
- Calculates percentage reduction
- Visualizes drag savings

**Ground Effect Analysis**
- Explains venturi/diffuser pressure dynamics
- Uses simplified Bernoulli equation
- Estimates downforce from pressure differential
- Always saves explanatory pressure-drop/downforce graphs tied to the underlying equations

#### 2. Tyres (NEW!)

**Tyre Compound Information**
- Characteristics of Soft, Medium, Hard, Intermediate, and Wet tyres
- Grip levels, durability, and typical lifespan
- Optimal temperature ranges and degradation rates

**Tyre Comparisons**
- Compare any two tyre compounds
- Understand trade-offs between grip and durability
- Strategic implications for race planning

**Tyre Strategy**
- Strategy recommendations based on track characteristics
- Undercut vs overcut concepts
- Pit stop timing considerations

#### 3. Car Performance (NEW!)

**Performance Metrics**
- Top speeds and acceleration data
- Braking performance and distances
- Lateral G-forces in corners

**Telemetry Information**
- Understanding telemetry data
- Throttle, brake, and steering inputs
- Performance analysis concepts

**Fast-F1 Integration** (Enabled by Default)
- Real-world race data from recent F1 seasons
- Historical lap times, sector times, and speeds
- Driver-specific performance data and telemetry
- Tyre compound usage and stint information
- Weather conditions and session data

#### 4. General F1 Knowledge (NEW!)

**Track Information**
- Characteristics of major circuits (Monaco, Silverstone, Spa, Monza, Singapore)
- Track types, surface conditions, and tyre stress levels
- Typical strategies for each circuit

**Racing Concepts**
- DRS (Drag Reduction System)
- Pit stops and strategy
- Undercut and overcut tactics
- Tyre blankets and regulations

### Intelligent Question Routing

The agent uses enhanced classification to route questions appropriately:
- **Confidence-based routing**: Questions are analyzed and routed to the best handler
- **Fallback handling**: Unsupported questions receive helpful "unable to answer" responses
- **Multi-category support**: Questions can span multiple domains

### What the Agent Cannot Answer

The agent will return "unable to answer" for:
- **Predictions**: "Who will win the championship?"
- **Opinions**: "Which driver is better?"
- **Future events**: "What will happen next year?"
- **Off-topic questions**: Questions not related to F1

### Physics Backend

The agent uses a clean abstraction layer (`physics/mcp_client.py`) designed for MCP integration:

- **Current Status**: Implements fallback analytic calculations using standard aerodynamic equations
- **MCP Integration Path**: Interface ready for IBM chuk-mcp-physics server
- **Equations Used**:
  - Dynamic pressure: `q = 0.5 * ρ * v²`
  - Lift/Downforce: `F_l = q * A * C_l`
  - Drag force: `F_d = q * A * C_d`
  - Pressure change: `ΔP = 0.5 * ρ * (v₁² - v₂²)`

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd f1_aero_agent
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-Line Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--interactive` or `-i` | Run in interactive mode for multiple questions | Single question mode |
| `--no-fastf1` | Disable Fast-F1 data integration | Fast-F1 **enabled** |
| `--mcp` | Enable MCP physics server (requires external setup) | Disabled |

### Single Question Mode

Ask a single question and get immediate results:

```bash
python main.py "What is the front wing downforce at different speeds?"
python main.py "Calculate drag force at 300 km/h"
python main.py "Compare DRS open vs closed"
python main.py "Explain ground effect"

# With real F1 data (enabled by default)
python main.py "What was Verstappen's fastest lap at Monaco 2024?"
python main.py "Show me tyre strategy from the last race"

# Disable Fast-F1 if needed
python main.py --no-fastf1 "What's the difference between soft and hard tyres?"
```

### Interactive Mode

Run in interactive mode for multiple questions:

```bash
python main.py --interactive
```

In interactive mode:
- Type your question and press Enter
- Type `help` to see supported questions
- Type `quit` or `exit` to exit

### Example Questions

#### Aerodynamics (Physics Calculations)
- "What is the front wing downforce at different speeds?"
- "Calculate drag force at 300 km/h"
- "Compare DRS open vs closed"
- "Explain ground effect"
- "How does the diffuser work?"

#### Tyres (Knowledge Base + Real Data)
- "What's the difference between soft and hard tyres?"
- "How long do medium tyres last?"
- "What tyre strategy should I use?"
- "Compare soft and medium compounds"
- "Tell me about intermediate tyres"
- "What compounds did Verstappen use in the last race?" (with Fast-F1)
- "Show tyre degradation data from Silverstone 2024" (with Fast-F1)

#### Car Performance (Knowledge Base + Real Data)
- "What is top speed in F1?"
- "How do F1 cars brake?"
- "What is telemetry data?"
- "How fast can an F1 car accelerate?"
- "What are lateral G-forces?"
- "What was the actual top speed at Monza 2024?" (with Fast-F1)
- "Show me Verstappen's telemetry from Monaco" (with Fast-F1)

#### General F1 (Knowledge Base)
- "What is Monaco circuit like?"
- "What is DRS?"
- "What happens in a pit stop?"
- "Tell me about Silverstone"
- "What is an undercut?"

#### Examples of Unsupported Questions (Will Return "Unable to Answer")
- "Who will win the championship?" (Prediction)
- "What's your favorite driver?" (Opinion)
- "Predict next race winner" (Future prediction)
- "Tell me about basketball" (Off-topic)

## Output

### Analysis Results

Each analysis provides:
- **Summary**: High-level results and key findings
- **Key Results**: Numerical values with units
- **Equations Used**: Mathematical formulas applied
- **Assumptions**: Simplifications and constants used
- **Generated Graph**: Path to at least one saved explanatory PNG file

### Visualizations

All visualizations are saved to the `f1_aero_visualizations/` directory with timestamps:
- `front_wing_downforce_YYYYMMDD_HHMMSS.png`
- `drag_force_YYYYMMDD_HHMMSS.png`
- `drs_comparison_YYYYMMDD_HHMMSS.png`
- `ground_effect_YYYYMMDD_HHMMSS.png`

Every supported analysis saves at least one mathematically explanatory graph:
- **Front wing downforce**: downforce vs speed curve
- **Drag at speed**: drag vs speed curve plus dynamic-pressure curve, with the queried speed highlighted
- **DRS comparison**: drag-force comparison and drag-reduction percentage across speed
- **Ground effect / diffuser**: pressure-drop vs speed and estimated-downforce vs speed based on Bernoulli-style reasoning

## Project Structure

```
f1_aero_agent/
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── test_integration.py          # Comprehensive integration tests
├── examples.py                  # Usage examples
├── agent/
│   ├── __init__.py
│   ├── core.py                  # Main agent logic with routing
│   ├── prompt.py                # Enhanced question classification
│   └── router.py                # Question routing logic
├── data/
│   ├── __init__.py
│   ├── knowledge_base.py        # F1 domain knowledge (tyres, tracks, concepts)
│   ├── fastf1_client.py         # Fast-F1 data integration
│   └── cache_manager.py         # Data caching
├── physics/
│   ├── __init__.py
│   ├── mcp_client.py            # MCP abstraction layer
│   └── calculations.py          # F1-specific calculations
└── visualization/
    ├── __init__.py
    └── generator.py             # Matplotlib visualizations
```

## MCP Integration Status

### Current Implementation

The project includes a complete MCP client abstraction (`physics/mcp_client.py`) with:
- Clean interface for physics calculations
- Fallback analytic implementation
- Ready for MCP server integration

### Future MCP Integration

To integrate with the IBM chuk-mcp-physics MCP server:

1. **Install MCP Python client** (when available):
   ```bash
   pip install mcp
   ```

2. **Update `mcp_client.py`**:
   - Implement MCP connection in `__init__`
   - Route calculation methods to MCP server
   - Handle MCP protocol communication

3. **Run with MCP**:
   ```bash
   python main.py --mcp "Your question here"
   ```

The interface is designed to make this transition seamless without changing the agent logic.

## Fast-F1 Integration

### Fast-F1 Enabled by Default

The agent includes Fast-F1 integration **enabled by default** for real-world race data:

```bash
# Fast-F1 is enabled automatically
python main.py "What was Verstappen's fastest lap at Monaco 2024?"

# Disable if needed
python main.py --no-fastf1 "What's the difference between soft and hard tyres?"
```

### Fast-F1 Features

With Fast-F1 enabled (default), the agent can access:
- **Historical race data** from recent F1 seasons
- **Lap times and sector times** for all drivers
- **Telemetry data** (speed, throttle, brake, steering)
- **Driver-specific performance metrics**
- **Tyre compound usage** and stint information
- **Weather conditions** during sessions

### Programmatic Usage

```python
from f1_aero_agent.agent import F1AeroAgent

# Fast-F1 enabled by default
agent = F1AeroAgent()

# Explicitly disable Fast-F1
agent = F1AeroAgent(enable_fastf1=False)

# Enable MCP (requires external setup)
agent = F1AeroAgent(enable_mcp=True)
```

### First Run Notes

- **Internet required**: First time accessing data for a specific race
- **Automatic caching**: Data is cached locally for faster subsequent access
- **Cache location**: `~/.f1_aero_agent/cache/fastf1/`
- **Download time**: Initial data fetch may take 10-30 seconds per session

## Technical Details

### Aerodynamic Parameters

The agent uses typical F1 values:
- **Frontal Area**: 1.5 m²
- **Front Wing Area**: 1.0 m²
- **Front Wing C_l**: -3.5 (negative = downforce)
- **Drag Coefficient (DRS closed)**: 0.9
- **Drag Coefficient (DRS open)**: 0.7
- **Air Density**: 1.225 kg/m³ (sea level, 15°C)

### Assumptions

All analyses clearly state assumptions:
- Constant coefficients (reality: vary with conditions)
- Incompressible flow (valid for F1 speeds)
- Steady-state conditions
- Simplified geometry
- Standard atmospheric conditions

### Limitations

- Simplified 1D/2D analysis (real F1 aero is complex 3D)
- Constant coefficients (reality: vary with ride height, yaw, etc.)
- No tire wake, suspension effects, or driver inputs
- Inviscid flow assumptions for ground effect

## Development

### Adding New Analyses

1. Add question type to `agent/prompt.py` (classification)
2. Update routing logic in `agent/router.py` if needed
3. Implement calculation in `physics/calculations.py` or add to `data/knowledge_base.py`
4. Create visualization in `visualization/generator.py` (if applicable)
5. Add handler method in `agent/core.py`

### Testing

Run comprehensive integration tests:
```bash
python test_integration.py
```

Test specific question types:
```bash
python main.py "Calculate drag force at 200 km/h"
python main.py "What's the difference between soft and hard tyres?"
python main.py "What is Monaco like?"
python main.py --interactive
```

Run example demonstrations:
```bash
python examples.py
```

## License

This project is provided as-is for educational and analysis purposes.

## References

- Standard aerodynamic equations (Anderson, "Fundamentals of Aerodynamics")
- F1 technical regulations (FIA)
- IBM chuk-mcp-physics: https://github.com/IBM/chuk-mcp-physics

## Support

For questions about F1 aerodynamics analysis, use the interactive mode or refer to the supported question types.

For technical issues, check:
1. Python version (3.8+)
2. Dependencies installed (`pip install -r requirements.txt`)
3. Virtual environment activated
4. Visualization output directory permissions