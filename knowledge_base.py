"""
F1 Knowledge Base

Pre-defined data about F1 tyres, tracks, and general racing knowledge
that doesn't require API calls.
"""

from typing import Dict, List, Optional, Any
from enum import Enum


class TyreCompound(Enum):
    """F1 tyre compound types."""
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"


class KnowledgeBase:
    """
    Repository of F1 domain knowledge including tyre characteristics,
    track information, and general racing facts.
    """
    
    # Tyre compound characteristics
    TYRE_DATA = {
        TyreCompound.SOFT: {
            "name": "Soft",
            "color": "Red",
            "grip_level": "High",
            "durability": "Low",
            "optimal_temp_range": "90-110°C",
            "typical_life_laps": "15-25",
            "characteristics": [
                "Highest grip level",
                "Fastest lap times",
                "Shortest lifespan",
                "Quick warm-up",
                "Best for qualifying and short stints"
            ],
            "degradation_rate": "High",
            "performance_window": "Narrow"
        },
        TyreCompound.MEDIUM: {
            "name": "Medium",
            "color": "Yellow",
            "grip_level": "Medium",
            "durability": "Medium",
            "optimal_temp_range": "85-105°C",
            "typical_life_laps": "25-35",
            "characteristics": [
                "Balanced performance",
                "Good compromise between speed and durability",
                "Versatile for various strategies",
                "Moderate warm-up time",
                "Most commonly used in races"
            ],
            "degradation_rate": "Medium",
            "performance_window": "Medium"
        },
        TyreCompound.HARD: {
            "name": "Hard",
            "color": "White",
            "grip_level": "Low",
            "durability": "High",
            "optimal_temp_range": "80-100°C",
            "typical_life_laps": "35-50",
            "characteristics": [
                "Longest lifespan",
                "Lower grip than softer compounds",
                "Slower warm-up",
                "Best for long stints",
                "Resistant to degradation"
            ],
            "degradation_rate": "Low",
            "performance_window": "Wide"
        },
        TyreCompound.INTERMEDIATE: {
            "name": "Intermediate",
            "color": "Green",
            "grip_level": "Variable",
            "durability": "Medium",
            "optimal_temp_range": "70-90°C",
            "typical_life_laps": "Variable",
            "characteristics": [
                "For damp or drying track conditions",
                "Grooved tread pattern",
                "Can disperse moderate water",
                "Performance depends on track wetness",
                "Bridge between dry and wet tyres"
            ],
            "degradation_rate": "Variable",
            "performance_window": "Narrow (condition-dependent)"
        },
        TyreCompound.WET: {
            "name": "Wet",
            "color": "Blue",
            "grip_level": "Variable",
            "durability": "Medium",
            "optimal_temp_range": "60-80°C",
            "typical_life_laps": "Variable",
            "characteristics": [
                "For heavy rain conditions",
                "Deep grooved tread pattern",
                "Can disperse up to 85 liters of water per second at 300 km/h",
                "Essential for safety in wet conditions",
                "Performance degrades on drying track"
            ],
            "degradation_rate": "Variable",
            "performance_window": "Narrow (condition-dependent)"
        }
    }
    
    # Track characteristics that affect tyre choice
    TRACK_CHARACTERISTICS = {
        "Monaco": {
            "type": "Street Circuit",
            "surface": "Low grip, bumpy",
            "tyre_stress": "Low",
            "typical_strategy": "One-stop or no-stop",
            "preferred_compounds": ["SOFT", "MEDIUM"],
            "characteristics": [
                "Lowest average speed",
                "Many slow corners",
                "Limited overtaking",
                "Low tyre degradation"
            ]
        },
        "Silverstone": {
            "type": "High-speed Circuit",
            "surface": "Smooth, high grip",
            "tyre_stress": "High",
            "typical_strategy": "Two-stop",
            "preferred_compounds": ["MEDIUM", "HARD"],
            "characteristics": [
                "High-speed corners",
                "High lateral loads",
                "Significant tyre degradation",
                "Weather can be unpredictable"
            ]
        },
        "Monza": {
            "type": "High-speed Circuit",
            "surface": "Smooth",
            "tyre_stress": "Low",
            "typical_strategy": "One-stop",
            "preferred_compounds": ["SOFT", "MEDIUM"],
            "characteristics": [
                "Highest average speed",
                "Long straights",
                "Few corners",
                "Low tyre degradation"
            ]
        },
        "Spa-Francorchamps": {
            "type": "High-speed Circuit",
            "surface": "Variable grip",
            "tyre_stress": "Medium-High",
            "typical_strategy": "One or two-stop",
            "preferred_compounds": ["MEDIUM", "HARD"],
            "characteristics": [
                "Long lap",
                "Mix of high and low-speed corners",
                "Weather often variable",
                "Challenging for tyre management"
            ]
        },
        "Singapore": {
            "type": "Street Circuit",
            "surface": "Low grip initially",
            "tyre_stress": "Medium",
            "typical_strategy": "Two-stop",
            "preferred_compounds": ["SOFT", "MEDIUM"],
            "characteristics": [
                "Night race",
                "Hot and humid",
                "Many corners",
                "Track grip improves during weekend"
            ]
        }
    }
    
    # General F1 racing knowledge
    RACING_KNOWLEDGE = {
        "drs": {
            "name": "Drag Reduction System",
            "description": "Adjustable rear wing element that reduces drag",
            "activation": "Within 1 second of car ahead in DRS zones",
            "effect": "10-15 km/h speed increase on straights",
            "restrictions": "Not available in first 2 laps or under wet conditions"
        },
        "pit_stop": {
            "typical_duration": "2-3 seconds",
            "time_loss": "20-25 seconds including pit lane",
            "components": "Tyre change, possible front wing adjustment",
            "crew_size": "Up to 20 people"
        },
        "undercut": {
            "description": "Pit earlier than rival to gain track position",
            "advantage": "Fresh tyres on clear track",
            "risk": "May need to manage tyres longer later"
        },
        "overcut": {
            "description": "Stay out longer than rival before pitting",
            "advantage": "Build gap on old tyres, emerge ahead on fresh tyres",
            "risk": "Tyre degradation may cost time"
        },
        "tyre_blankets": {
            "description": "Heated covers to pre-warm tyres",
            "temperature": "Up to 70°C for slicks",
            "purpose": "Bring tyres closer to optimal operating temperature",
            "regulation": "Will be banned from 2024 onwards (delayed)"
        }
    }
    
    # Physics concepts
    PHYSICS_CONCEPTS = {
        "g_force": {
            "name": "G-Force",
            "definition": "Measurement of acceleration felt as weight, where 1g equals Earth's gravity (9.81 m/s²)",
            "f1_context": {
                "braking": "5-6g during heavy braking zones",
                "cornering": "4-6g in high-speed corners",
                "acceleration": "1.5-2g during acceleration"
            },
            "driver_impact": [
                "Extreme physical demands on neck and core muscles",
                "Blood pressure changes affecting vision",
                "Requires exceptional fitness and conditioning",
                "Sustained exposure throughout 1.5-2 hour races"
            ],
            "examples": [
                "Turn 1 at Monza: ~5g braking",
                "130R at Suzuka: ~5g lateral",
                "Eau Rouge at Spa: ~4.5g combined"
            ]
        },
        "downforce": {
            "name": "Downforce",
            "definition": "Aerodynamic force pushing the car down onto the track, increasing grip",
            "purpose": "Allows higher cornering speeds by increasing tire grip without adding weight",
            "sources": [
                "Front wing: ~25-30% of total downforce",
                "Floor and diffuser: ~50-60% of total downforce",
                "Rear wing: ~20-25% of total downforce",
                "Bodywork and other elements: ~5-10%"
            ],
            "typical_values": "3-4 times the car's weight at high speed (2400-3200kg at 250 km/h)",
            "trade_offs": {
                "benefits": "Higher cornering speeds, better braking, improved traction",
                "costs": "Increased drag, reduced top speed, higher tire wear"
            },
            "adjustment": "Teams adjust downforce levels based on track characteristics (high for Monaco, low for Monza)"
        },
        "drag": {
            "name": "Aerodynamic Drag",
            "definition": "Air resistance force opposing the car's motion",
            "impact": [
                "Reduces top speed on straights",
                "Increases fuel consumption",
                "Requires more power to overcome",
                "Proportional to square of velocity (double speed = 4x drag)"
            ],
            "management": {
                "drs": "Drag Reduction System reduces drag by ~10-15% when activated",
                "setup": "Teams balance drag vs downforce based on track layout",
                "slipstreaming": "Following another car reduces drag by up to 30%"
            },
            "typical_values": "Drag coefficient (Cd) around 0.7-1.0 for modern F1 cars"
        },
        "cornering_forces": {
            "name": "Cornering Forces",
            "definition": "Lateral forces acting on the car and driver during turns",
            "components": [
                "Centripetal force: Required to change direction",
                "Tire grip: Provides the cornering force",
                "Aerodynamic downforce: Increases available grip",
                "Weight transfer: Affects tire loading"
            ],
            "typical_values": {
                "low_speed": "2-3g in slow corners (Monaco hairpin)",
                "medium_speed": "3-4g in medium corners",
                "high_speed": "4-6g in fast corners (Copse, 130R)"
            },
            "driver_experience": "Sustained lateral forces cause neck strain and require exceptional core strength"
        },
        "braking_forces": {
            "name": "Braking Forces",
            "definition": "Deceleration forces when slowing the car",
            "f1_performance": {
                "peak_deceleration": "5-6g in heavy braking zones",
                "brake_pressure": "Up to 150kg of pedal force required",
                "brake_temp": "800-1000°C disc temperature",
                "stopping_distance": "~65m from 200 km/h to 0"
            },
            "braking_distances": {
                "300_to_200": "~85-95 meters",
                "200_to_100": "~55-65 meters",
                "100_to_0": "~30-35 meters"
            },
            "energy_recovery": "MGU-K harvests up to 120kW during braking",
            "driver_technique": "Trail braking, brake balance adjustment, managing brake temperatures"
        },
        "lateral_acceleration": {
            "name": "Lateral Acceleration",
            "definition": "Sideways acceleration experienced during cornering",
            "f1_values": {
                "typical_range": "3-6g depending on corner speed",
                "peak_values": "Up to 6g in fastest corners",
                "sustained": "4-5g for several seconds in long corners"
            },
            "factors": [
                "Corner radius and speed",
                "Aerodynamic downforce level",
                "Tire grip and temperature",
                "Track surface characteristics"
            ],
            "measurement": "Measured by accelerometers in the car's data acquisition system"
        },
        "aerodynamic_balance": {
            "name": "Aerodynamic Balance",
            "definition": "Distribution of downforce between front and rear axles",
            "importance": [
                "Affects car handling characteristics",
                "Determines understeer/oversteer balance",
                "Critical for driver confidence",
                "Changes with speed and ride height"
            ],
            "typical_distribution": "Front 40-45%, Rear 55-60% of total downforce",
            "adjustment_methods": [
                "Front wing angle changes",
                "Rear wing angle adjustments",
                "Ride height modifications",
                "Suspension geometry changes"
            ],
            "track_specific": "High-speed tracks need more rear bias, tight circuits need more front"
        },
        "weight_transfer": {
            "name": "Weight Transfer",
            "definition": "Shift of load between tires during acceleration, braking, and cornering",
            "impact_on_handling": {
                "braking": "Weight shifts forward, increasing front grip, reducing rear grip",
                "acceleration": "Weight shifts rearward, increasing rear grip, reducing front grip",
                "cornering": "Weight shifts to outside tires, affecting balance"
            },
            "management": [
                "Suspension setup controls weight transfer rate",
                "Anti-roll bars affect lateral weight transfer",
                "Brake balance adjusts front/rear braking forces",
                "Driver technique can optimize weight transfer"
            ],
            "typical_values": "Up to 60-70% of weight can transfer to front wheels under heavy braking"
        },
        "mechanical_grip": {
            "name": "Mechanical Grip",
            "definition": "Grip generated by tire contact with track surface, independent of aerodynamics",
            "sources": [
                "Tire compound and construction",
                "Suspension geometry and setup",
                "Weight distribution",
                "Track surface characteristics"
            ],
            "vs_aerodynamic_grip": {
                "mechanical": "Constant regardless of speed, works at all speeds including low speed",
                "aerodynamic": "Increases with speed squared, minimal at low speeds"
            },
            "importance": "Critical in slow corners and during low-speed phases (pit entry, hairpins)",
            "optimization": "Suspension setup, tire pressures, camber angles, toe settings"
        }
    }
    
    # 2026 F1 Regulations
    REGULATIONS_2026 = {
        "power_unit": {
            "hybrid_system": {
                "ice_power": "~400-450 kW (536-603 hp)",
                "electric_power": "~350 kW (469 hp) - significantly increased from current 120 kW",
                "total_power": "~750-800 kW (1006-1073 hp)",
                "electric_deployment": "Much more electric power available throughout lap"
            },
            "sustainable_fuel": {
                "type": "100% sustainable fuel (e-fuels or advanced biofuels)",
                "carbon_neutral": "Net-zero carbon emissions from fuel",
                "energy_density": "Similar to current fuel specifications"
            },
            "mgu_changes": {
                "mgu_k": "Significantly more powerful, ~350 kW output",
                "mgu_h": "Removed from regulations",
                "battery": "Increased capacity to support higher electric deployment"
            },
            "fuel_flow": "Reduced to promote efficiency and electric power usage"
        },
        "aerodynamics": {
            "active_aero": {
                "description": "Active aerodynamic elements allowed for first time in decades",
                "front_wing": "Adjustable elements to optimize performance",
                "rear_wing": "Active rear wing with multiple modes",
                "purpose": "Reduce drag on straights, increase downforce in corners"
            },
            "downforce_reduction": "Overall downforce reduced by ~30% compared to 2025",
            "drag_reduction": "Overall drag reduced by ~55% compared to 2025",
            "ground_effect": "Continued use of ground effect aerodynamics with refined regulations",
            "design_philosophy": "Emphasis on efficiency and reduced dirty air impact"
        },
        "car_specifications": {
            "weight": {
                "minimum_weight": "~768 kg (increased from current 798 kg due to battery changes)",
                "distribution": "Adjusted for new power unit layout"
            },
            "dimensions": {
                "length": "Reduced by ~200mm compared to current cars",
                "width": "Maintained at 2000mm",
                "wheelbase": "Reduced to improve agility"
            },
            "tires": {
                "size": "18-inch wheels maintained",
                "compounds": "Continued development of sustainable materials"
            }
        },
        "key_changes_summary": [
            "Massive increase in electric power (120 kW → 350 kW)",
            "Introduction of active aerodynamics",
            "100% sustainable fuels mandatory",
            "Removal of MGU-H for cost reduction",
            "Significant reduction in drag and downforce",
            "Smaller, more agile cars",
            "Focus on sustainability and efficiency",
            "Improved racing through reduced dirty air"
        ],
        "goals": [
            "Carbon neutrality through sustainable fuels",
            "Better racing with active aero and reduced dirty air",
            "Cost reduction through simpler power units",
            "Road relevance with high electric power deployment",
            "Maintain performance levels despite efficiency focus"
        ]
    }
    
    # Current F1 Teams (2024-2025 season)
    F1_TEAMS = {
        "red_bull_racing": {
            "full_name": "Oracle Red Bull Racing",
            "base": "Milton Keynes, United Kingdom",
            "power_unit": "Red Bull Powertrains (Honda-derived)",
            "team_principal": "Christian Horner",
            "technical_director": "Pierre Waché",
            "championships": {
                "constructors": 6,
                "drivers": 7,
                "recent": "2021-2023 (Constructors), 2021-2023 (Drivers - Verstappen)"
            },
            "colors": ["Navy Blue", "Red", "Yellow"],
            "notable_drivers": ["Max Verstappen", "Sergio Pérez"],
            "founded": 2005,
            "previous_names": ["Jaguar Racing", "Stewart Grand Prix"]
        },
        "ferrari": {
            "full_name": "Scuderia Ferrari",
            "base": "Maranello, Italy",
            "power_unit": "Ferrari (works team)",
            "team_principal": "Frédéric Vasseur",
            "technical_director": "Enrico Cardile",
            "championships": {
                "constructors": 16,
                "drivers": 15,
                "recent": "2008 (Constructors), 2007 (Drivers - Räikkönen)"
            },
            "colors": ["Red", "Yellow"],
            "notable_drivers": ["Charles Leclerc", "Carlos Sainz"],
            "founded": 1950,
            "legacy": "Oldest and most successful team in F1 history"
        },
        "mercedes": {
            "full_name": "Mercedes-AMG Petronas Formula One Team",
            "base": "Brackley, United Kingdom",
            "power_unit": "Mercedes (works team)",
            "team_principal": "Toto Wolff",
            "technical_director": "James Allison",
            "championships": {
                "constructors": 8,
                "drivers": 9,
                "recent": "2014-2021 (Constructors), 2014-2020 (Drivers - Hamilton)"
            },
            "colors": ["Silver", "Turquoise", "Black"],
            "notable_drivers": ["Lewis Hamilton", "George Russell"],
            "founded": 2010,
            "previous_names": ["Brawn GP", "Honda Racing F1", "BAR"]
        },
        "mclaren": {
            "full_name": "McLaren Formula 1 Team",
            "base": "Woking, United Kingdom",
            "power_unit": "Mercedes",
            "team_principal": "Andrea Stella",
            "technical_director": "Peter Prodromou",
            "championships": {
                "constructors": 8,
                "drivers": 12,
                "recent": "1998 (Constructors), 2008 (Drivers - Hamilton)"
            },
            "colors": ["Papaya Orange", "Blue"],
            "notable_drivers": ["Lando Norris", "Oscar Piastri"],
            "founded": 1966,
            "legacy": "Second most successful British team after Williams"
        },
        "aston_martin": {
            "full_name": "Aston Martin Aramco Cognizant Formula One Team",
            "base": "Silverstone, United Kingdom",
            "power_unit": "Mercedes",
            "team_principal": "Mike Krack",
            "technical_director": "Dan Fallows",
            "championships": {
                "constructors": 0,
                "drivers": 0,
                "recent": "N/A (rebranded in 2021)"
            },
            "colors": ["British Racing Green", "Lime"],
            "notable_drivers": ["Fernando Alonso", "Lance Stroll"],
            "founded": 2021,
            "previous_names": ["Racing Point", "Force India", "Jordan"]
        },
        "alpine": {
            "full_name": "BWT Alpine F1 Team",
            "base": "Enstone, United Kingdom",
            "power_unit": "Renault (works team)",
            "team_principal": "Bruno Famin",
            "technical_director": "Matt Harman",
            "championships": {
                "constructors": 2,
                "drivers": 2,
                "recent": "2006 (Constructors), 2006 (Drivers - Alonso)"
            },
            "colors": ["Blue", "Pink", "Red"],
            "notable_drivers": ["Pierre Gasly", "Esteban Ocon"],
            "founded": 2021,
            "previous_names": ["Renault F1 Team", "Lotus F1", "Benetton"]
        },
        "williams": {
            "full_name": "Williams Racing",
            "base": "Grove, United Kingdom",
            "power_unit": "Mercedes",
            "team_principal": "James Vowles",
            "technical_director": "Pat Fry",
            "championships": {
                "constructors": 9,
                "drivers": 7,
                "recent": "1997 (Constructors), 1997 (Drivers - Villeneuve)"
            },
            "colors": ["Blue", "White", "Red"],
            "notable_drivers": ["Alex Albon", "Logan Sargeant"],
            "founded": 1977,
            "legacy": "Third most successful constructor in F1 history"
        },
        "rb": {
            "full_name": "Visa Cash App RB Formula One Team",
            "base": "Faenza, Italy",
            "power_unit": "Red Bull Powertrains",
            "team_principal": "Laurent Mekies",
            "technical_director": "Jody Egginton",
            "championships": {
                "constructors": 0,
                "drivers": 1,
                "recent": "2008 (Drivers - Vettel as Toro Rosso)"
            },
            "colors": ["Navy Blue", "Red"],
            "notable_drivers": ["Yuki Tsunoda", "Daniel Ricciardo"],
            "founded": 2006,
            "previous_names": ["AlphaTauri", "Toro Rosso", "Minardi"],
            "role": "Red Bull's junior team"
        },
        "sauber": {
            "full_name": "Stake F1 Team Kick Sauber",
            "base": "Hinwil, Switzerland",
            "power_unit": "Ferrari",
            "team_principal": "Alessandro Alunni Bravi",
            "technical_director": "Jan Monchaux",
            "championships": {
                "constructors": 0,
                "drivers": 0,
                "recent": "N/A"
            },
            "colors": ["Green", "White", "Red"],
            "notable_drivers": ["Valtteri Bottas", "Zhou Guanyu"],
            "founded": 1993,
            "previous_names": ["Alfa Romeo Racing", "BMW Sauber"],
            "future": "Becoming Audi works team in 2026"
        },
        "haas": {
            "full_name": "MoneyGram Haas F1 Team",
            "base": "Kannapolis, North Carolina, USA / Banbury, UK",
            "power_unit": "Ferrari",
            "team_principal": "Ayao Komatsu",
            "technical_director": "Andrea De Zordo",
            "championships": {
                "constructors": 0,
                "drivers": 0,
                "recent": "N/A"
            },
            "colors": ["White", "Red", "Black"],
            "notable_drivers": ["Nico Hülkenberg", "Kevin Magnussen"],
            "founded": 2016,
            "distinction": "First American F1 team since 1986"
        }
    }
    
    # Car Components and Specifications
    CAR_COMPONENTS = {
        "power_unit": {
            "ice": {
                "type": "1.6L V6 turbocharged",
                "power": "~750-800 hp (560-600 kW)",
                "rpm_limit": "15,000 RPM",
                "fuel_flow": "100 kg/hour maximum",
                "efficiency": "~50% thermal efficiency (road cars ~30%)"
            },
            "ers": {
                "mgu_k": {
                    "name": "Motor Generator Unit - Kinetic",
                    "power": "120 kW (161 hp)",
                    "harvest": "Recovers energy under braking",
                    "deployment": "Provides power boost during acceleration"
                },
                "mgu_h": {
                    "name": "Motor Generator Unit - Heat",
                    "function": "Recovers energy from exhaust gases",
                    "connection": "Connected to turbocharger",
                    "benefit": "Eliminates turbo lag, harvests waste heat"
                },
                "battery": {
                    "capacity": "4 MJ per lap",
                    "weight": "~20-25 kg",
                    "voltage": "~800V"
                }
            },
            "total_power": "~1000 hp (750 kW) combined ICE + ERS",
            "fuel": "E10 fuel (10% ethanol, 90% fossil fuel)",
            "oil": "Highly specialized lubricants for extreme conditions"
        },
        "dimensions": {
            "length": "~5500mm (varies by team)",
            "width": "2000mm maximum",
            "height": "~950mm (varies by design)",
            "wheelbase": "3400-3700mm (varies by team)",
            "minimum_weight": "798 kg including driver",
            "weight_distribution": "~45% front, 55% rear (varies by setup)"
        },
        "gearbox": {
            "gears": "8-speed sequential",
            "type": "Semi-automatic with paddle shifters",
            "shift_time": "~0.05 seconds (50 milliseconds)",
            "reverse_gear": "Mandatory, rarely used",
            "construction": "Carbon fiber casing, titanium gears",
            "durability": "Must last multiple race weekends"
        },
        "brakes": {
            "discs": {
                "material": "Carbon-carbon composite",
                "diameter": "330mm front, 370mm rear maximum",
                "thickness": "28-32mm",
                "temperature": "800-1000°C during braking"
            },
            "calipers": {
                "pistons": "6-piston front, 4-piston rear",
                "material": "Aluminum alloy",
                "pressure": "Up to 150 kg pedal force"
            },
            "performance": {
                "deceleration": "5-6g peak",
                "cooling": "Brake ducts with adjustable openings",
                "wear": "Discs can last entire race weekend"
            },
            "brake_by_wire": "Rear brakes integrated with ERS harvesting"
        },
        "suspension": {
            "type": "Double wishbone (front and rear)",
            "adjustability": [
                "Ride height",
                "Camber angle",
                "Toe angle",
                "Anti-roll bar stiffness",
                "Spring rates",
                "Damper settings"
            ],
            "materials": "Carbon fiber, titanium, aluminum alloys",
            "travel": "Limited to ~100mm to maintain aerodynamic efficiency",
            "active_systems": "Banned (except DRS)",
            "heave_springs": "Third spring element to control pitch"
        },
        "steering": {
            "type": "Power-assisted rack and pinion",
            "wheel": {
                "functions": "Gear changes, brake balance, DRS, radio, drink, settings",
                "buttons": "20+ buttons and rotary switches",
                "displays": "LCD screen showing telemetry",
                "cost": "~$50,000-80,000 per wheel"
            },
            "ratio": "Variable depending on team preference",
            "lock_to_lock": "~360-450 degrees"
        },
        "fuel_system": {
            "tank_capacity": "110 kg maximum",
            "fuel_load": "Varies by strategy (typically 100-110 kg at start)",
            "fuel_effect": "~0.03s per lap per kg of fuel",
            "refueling": "Banned since 2010"
        },
        "electronics": {
            "ecu": "Standard McLaren Applied ECU (control unit)",
            "sensors": "100+ sensors monitoring all systems",
            "data_logging": "Real-time telemetry to pit wall",
            "driver_aids": "Traction control and ABS banned",
            "energy_management": "Complex software for ERS deployment"
        },
        "safety": {
            "halo": {
                "introduction": 2018,
                "material": "Titanium",
                "strength": "Can withstand 12 tonnes load",
                "weight": "7 kg"
            },
            "survival_cell": "Carbon fiber monocoque, FIA crash tested",
            "seat": "Custom molded for each driver",
            "harness": "6-point safety harness",
            "hans": "Head and Neck Support device mandatory"
        }
    }
    
    def __init__(self):
        """Initialize the knowledge base."""
        pass
    
    def get_tyre_info(self, compound: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tyre compound.
        
        Args:
            compound: Tyre compound name (e.g., 'SOFT', 'MEDIUM', 'HARD')
        
        Returns:
            Dictionary with tyre characteristics, or None if not found
        """
        try:
            compound_enum = TyreCompound[compound.upper()]
            return self.TYRE_DATA.get(compound_enum)
        except KeyError:
            return None
    
    def get_all_tyre_compounds(self) -> List[str]:
        """
        Get list of all available tyre compounds.
        
        Returns:
            List of compound names
        """
        return [compound.value for compound in TyreCompound]
    
    def compare_tyres(self, compound1: str, compound2: str) -> Dict[str, Any]:
        """
        Compare two tyre compounds.
        
        Args:
            compound1: First compound name
            compound2: Second compound name
        
        Returns:
            Dictionary with comparison data
        """
        tyre1 = self.get_tyre_info(compound1)
        tyre2 = self.get_tyre_info(compound2)
        
        if not tyre1 or not tyre2:
            return {"error": "One or both compounds not found"}
        
        return {
            "compound1": {
                "name": compound1,
                "data": tyre1
            },
            "compound2": {
                "name": compound2,
                "data": tyre2
            },
            "comparison": {
                "grip": f"{compound1} has {tyre1['grip_level']} grip vs {compound2} with {tyre2['grip_level']} grip",
                "durability": f"{compound1} has {tyre1['durability']} durability vs {compound2} with {tyre2['durability']} durability",
                "degradation": f"{compound1} degrades at {tyre1['degradation_rate']} rate vs {compound2} at {tyre2['degradation_rate']} rate"
            }
        }
    
    def get_track_info(self, track_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific track.
        
        Args:
            track_name: Name of the track (e.g., 'Monaco', 'Silverstone')
        
        Returns:
            Dictionary with track characteristics, or None if not found
        """
        return self.TRACK_CHARACTERISTICS.get(track_name)
    
    def get_all_tracks(self) -> List[str]:
        """
        Get list of all tracks in the knowledge base.
        
        Returns:
            List of track names
        """
        return list(self.TRACK_CHARACTERISTICS.keys())
    
    def get_racing_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a racing concept or term.
        
        Args:
            concept: Racing concept name (e.g., 'drs', 'undercut')
        
        Returns:
            Dictionary with concept information, or None if not found
        """
        return self.RACING_KNOWLEDGE.get(concept.lower())
    
    def get_all_racing_concepts(self) -> List[str]:
        """
        Get list of all racing concepts in the knowledge base.
        
        Returns:
            List of concept names
        """
        return list(self.RACING_KNOWLEDGE.keys())
    
    def recommend_tyre_strategy(
        self, 
        track_name: str, 
        race_distance: int = 50
    ) -> Dict[str, Any]:
        """
        Recommend a tyre strategy for a given track.
        
        Args:
            track_name: Name of the track
            race_distance: Number of laps in the race
        
        Returns:
            Dictionary with strategy recommendation
        """
        track_info = self.get_track_info(track_name)
        
        if not track_info:
            return {"error": f"Track {track_name} not found in knowledge base"}
        
        strategy = {
            "track": track_name,
            "race_distance": race_distance,
            "typical_strategy": track_info["typical_strategy"],
            "preferred_compounds": track_info["preferred_compounds"],
            "considerations": track_info["characteristics"]
        }
        
        # Add specific recommendations based on track characteristics
        if track_info["tyre_stress"] == "Low":
            strategy["recommendation"] = (
                "Low tyre degradation allows for aggressive one-stop strategy. "
                "Consider starting on softs for track position."
            )
        elif track_info["tyre_stress"] == "High":
            strategy["recommendation"] = (
                "High tyre degradation requires careful management. "
                "Two-stop strategy likely optimal. Consider medium-hard-medium."
            )
        else:
            strategy["recommendation"] = (
                "Moderate tyre degradation. Strategy flexibility available. "
                "Monitor race conditions and adjust accordingly."
            )
        
        return strategy
    
    def get_physics_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a physics concept.
        
        Args:
            concept: Physics concept name (e.g., 'g_force', 'downforce', 'drag')
        
        Returns:
            Dictionary with concept information, or None if not found
        """
        return self.PHYSICS_CONCEPTS.get(concept.lower().replace('-', '_').replace(' ', '_'))
    
    def get_all_physics_concepts(self) -> List[str]:
        """
        Get list of all physics concepts in the knowledge base.
        
        Returns:
            List of concept names
        """
        return list(self.PHYSICS_CONCEPTS.keys())
    
    def get_2026_regulations(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about 2026 F1 regulations.
        
        Args:
            category: Specific category (e.g., 'power_unit', 'aerodynamics', 'car_specifications')
                     If None, returns all regulations
        
        Returns:
            Dictionary with regulation information, or None if category not found
        """
        if category:
            result = self.REGULATIONS_2026.get(category.lower())
            return result if result else None
        return self.REGULATIONS_2026
    
    def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an F1 team.
        
        Args:
            team_name: Team name (e.g., 'ferrari', 'red_bull_racing', 'mercedes')
        
        Returns:
            Dictionary with team information, or None if not found
        """
        # Normalize team name
        normalized = team_name.lower().replace(' ', '_').replace('-', '_')
        
        # Try direct match first
        if normalized in self.F1_TEAMS:
            return self.F1_TEAMS[normalized]
        
        # Try partial matches
        for key, team_data in self.F1_TEAMS.items():
            if normalized in key or normalized in team_data['full_name'].lower():
                return team_data
        
        return None
    
    def get_all_teams(self) -> List[str]:
        """
        Get list of all F1 teams in the knowledge base.
        
        Returns:
            List of team names
        """
        return [team['full_name'] for team in self.F1_TEAMS.values()]
    
    def get_car_component_info(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a car component.
        
        Args:
            component: Component name (e.g., 'power_unit', 'brakes', 'suspension')
        
        Returns:
            Dictionary with component information, or None if not found
        """
        return self.CAR_COMPONENTS.get(component.lower().replace(' ', '_').replace('-', '_'))
    
    def get_all_car_components(self) -> List[str]:
        """
        Get list of all car components in the knowledge base.
        
        Returns:
            List of component names
        """
        return list(self.CAR_COMPONENTS.keys())
    
    def get_concept_info(self, concept: str) -> Optional[Dict[str, Any]]:
        """
        Get information about any concept (racing, physics, or general).
        Searches across all knowledge base sections.
        
        Args:
            concept: Concept name to search for
        
        Returns:
            Dictionary with concept information, or None if not found
        """
        # Try racing concepts first
        result = self.get_racing_concept(concept)
        if result:
            return {"type": "racing_concept", "data": result}
        
        # Try physics concepts
        result = self.get_physics_concept(concept)
        if result:
            return {"type": "physics_concept", "data": result}
        
        # Try car components
        result = self.get_car_component_info(concept)
        if result:
            return {"type": "car_component", "data": result}
        
        # Try team info
        result = self.get_team_info(concept)
        if result:
            return {"type": "team", "data": result}
        
        return None

# Made with Bob
