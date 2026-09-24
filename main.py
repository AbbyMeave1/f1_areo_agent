#!/usr/bin/env python3
"""
F1 Agent - CLI Entry Point

An AI agent for analyzing Formula 1 aerodynamics, tyres, car performance,
and general F1 topics using physics calculations, knowledge base, and data.
"""

import sys
import time
import random
import shutil
from pathlib import Path
# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from f1_aero_agent.agent import F1AeroAgent, get_enhanced_supported_questions_text

# High-contrast colors for black background
RED = '\033[91m'        # Bright red for headers/accents
GREEN = '\033[92m'      # Bright green for success
YELLOW = '\033[93m'     # Bright yellow for highlights
CYAN = '\033[96m'       # Bright cyan for secondary text
WHITE = '\033[97m'      # Bright white for main text
MAGENTA = '\033[95m'    # Bright magenta for variety
BLUE = '\033[94m'       # Bright blue for variety
BOLD = '\033[1m'        # Bold text
RESET = '\033[0m'       # Reset to default

# Session lap counter
lap_counter = 0

# Terminal width cache
_terminal_width = None

def get_terminal_width() -> int:
    """Get terminal width with caching and minimum width."""
    global _terminal_width
    if _terminal_width is None:
        try:
            _terminal_width = shutil.get_terminal_size().columns
        except:
            _terminal_width = 80  # Default fallback
    # Ensure minimum width of 60
    return max(_terminal_width, 60)

def center_text(text: str, width: int | None = None) -> str:
    """
    Center a single line of text within the terminal width.
    
    Args:
        text: Text to center (single line)
        width: Terminal width (auto-detected if None)
    
    Returns:
        Centered text string
    """
    if width is None:
        width = get_terminal_width()
    
    # Remove ANSI codes for length calculation
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    
    # Calculate padding
    text_len = len(clean_text)
    if text_len >= width:
        return text
    
    padding = (width - text_len) // 2
    return ' ' * padding + text

def center_multiline_text(text: str, width: int | None = None) -> str:
    """
    Center multiple lines of text.
    
    Args:
        text: Multi-line text to center
        width: Terminal width (auto-detected if None)
    
    Returns:
        Centered multi-line text
    """
    if width is None:
        width = get_terminal_width()
    
    lines = text.split('\n')
    centered_lines = [center_text(line, width) for line in lines]
    return '\n'.join(centered_lines)

def draw_chat_box(prompt_text: str, lap_num: int | None = None) -> str:
    """
    Draw a chat box for user input at the bottom of the terminal.
    
    Args:
        prompt_text: Text to show in the prompt header
        lap_num: Current lap number (optional)
    
    Returns:
        Formatted chat box string
    """
    width = get_terminal_width()
    box_width = min(width - 4, 70)  # Leave some margin
    
    # Box drawing characters
    top_left = "╔"
    top_right = "╗"
    bottom_left = "╚"
    bottom_right = "╝"
    horizontal = "═"
    vertical = "║"
    left_t = "╠"
    right_t = "╣"
    
    # Create box lines
    top_line = top_left + horizontal * box_width + top_right
    middle_line = left_t + horizontal * box_width + right_t
    bottom_line = bottom_left + horizontal * box_width + bottom_right
    
    # Header text
    header = f"  💬 {prompt_text}"
    header_padding = box_width - len(header) + 2
    header_line = vertical + header + ' ' * header_padding + vertical
    
    # Prompt line with lap counter
    if lap_num:
        prompt = f"  🏁 Lap {lap_num} 🏎️:   "
    else:
        prompt = "  🏎️:   "
    prompt_padding = box_width - len(prompt) + 2
    prompt_line = vertical + prompt + ' ' * prompt_padding + vertical
    
    box_lines = [top_line, header_line, middle_line, prompt_line, bottom_line]
    return '\n'.join(box_lines)

# Fun racing facts
RACING_FACTS = [
    "💡 F1 cars can accelerate from 0-100 km/h in just 2.6 seconds!",
    "💡 An F1 car generates enough downforce to drive upside down at 120 mph!",
    "💡 F1 drivers lose an average of 3kg of weight during a race!",
    "💡 F1 brake discs can reach temperatures of 1,000°C!",
    "💡 An F1 engine can rev up to 15,000 RPM!",
    "💡 F1 pit stops can be completed in under 2 seconds!",
    "💡 F1 cars use over 100,000 sensors to collect data!",
    "💡 The steering wheel of an F1 car costs around $50,000!",
    "💡 F1 tyres lose performance after just a few laps!",
    "💡 DRS (Drag Reduction System) can add 10-12 km/h of top speed!",
]

# ASCII Art Components
RACING_CAR = """
    ___
   /   \\___
  |  🏎️  💨|
   \\___/‾‾‾
"""

CHECKERED_FLAG = """
▓▒▓▒▓▒▓▒
▒▓▒▓▒▓▒▓
▓▒▓▒▓▒▓▒
▒▓▒▓▒▓▒▓
"""

TROPHY = """
    ___________
   '._==_==_=_.'
   .-\\:      /-.
  | (|:.     |) |
   '-|:.     |-'
     \\::.    /
      '::. .'
        ) (
      _.' '._
     '-------'
"""

LARGE_BANNER = f"""
{RED}{BOLD}
   █████╗ ██████╗ ██████╗ ██╗   ██╗ ██████╗ ██████╗ ████████╗
  ██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝ ██╔══██╗╚══██╔══╝
  ███████║██████╔╝██████╔╝ ╚████╔╝ ██║  ███╗██████╔╝   ██║
  ██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  ██║   ██║██╔═══╝    ██║
  ██║  ██║██████╔╝██████╔╝   ██║   ╚██████╔╝██║        ██║
  ╚═╝  ╚═╝╚═════╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝        ╚═╝
{RESET}
{RED}        🏎️  Your AI Racing Engineer  💨{RESET}
{RED}        ═══════════════════════════════════════════{RESET}
"""

def racing_car_animation(distance: int = 50, message: str = "Processing") -> None:
    """
    Display a racing car moving across the screen (centered).
    
    Args:
        distance: Number of positions to move
        message: Message to display
    """
    car = "🏎️💨"
    width = get_terminal_width()
    print(f"\n{WHITE}{message}...{RESET}")
    
    # Center the animation
    start_pos = (width - distance) // 2
    for i in range(distance):
        line = ' ' * (start_pos + i) + car
        sys.stdout.write(f"\r{line}")
        sys.stdout.flush()
        time.sleep(0.03)
    
    final_line = ' ' * (start_pos + distance) + f"{RED}✓{RESET}"
    sys.stdout.write(f"\r{final_line}\n")
    sys.stdout.flush()


def spinning_tire_animation(duration: float = 1.5) -> None:
    """
    Display a spinning tire animation.
    
    Args:
        duration: How long to animate in seconds
    """
    frames = ["◐", "◓", "◑", "◒"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{WHITE}🏁 {frames[i % len(frames)]} Analyzing...{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f"\r{RED}✓ Analysis complete!{RESET}     \n")
    sys.stdout.flush()


def race_track_loading_bar(steps: int = 20, message: str = "Loading") -> None:
    """
    Display a loading bar styled as a race track.
    
    Args:
        steps: Number of steps in the loading bar
        message: Message to display
    """
    print(f"\n{WHITE}{message}...{RESET}")
    track = "═"
    car = "🏎️"
    
    for i in range(steps + 1):
        filled = track * i
        empty = " " * (steps - i)
        percentage = (i / steps) * 100
        
        sys.stdout.write(f"\r{RED}[{filled}{car}{empty}]{RESET} {WHITE}{percentage:.0f}%{RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    
    print(f"\n{RED}✓ Complete!{RESET}\n")


def print_checkered_flag() -> None:
    """Display a checkered flag pattern."""
    print(f"{WHITE}{CHECKERED_FLAG}{RESET}")


def print_racing_fact() -> None:
    """Display a random racing fact."""
    fact = random.choice(RACING_FACTS)
    print(f"\n{CYAN}{fact}{RESET}\n")


def print_victory_celebration() -> None:
    """Display a victory celebration."""
    print(f"\n{RED}{BOLD}")
    print("🏆 ═══════════════════════════════════════ 🏆")
    print(f"{WHITE}TASK COMPLETED SUCCESSFULLY!{RED}")
    print("🏆 ═══════════════════════════════════════ 🏆")
    print(f"{RESET}")
    print(f"{WHITE}{TROPHY}{RESET}")


def get_lap_display() -> str:
    """Get the current lap counter display."""
    global lap_counter
    lap_counter += 1
    return f"{RED}🏁 Lap {lap_counter}{RESET}"



def stream_text(text: str, delay: float = 0.02, centered: bool = False) -> None:
    """
    Display text character by character with streaming effect.
    Supports centered text by processing line by line.
    
    Args:
        text: Text to display
        delay: Delay between characters in seconds (default: 0.02)
        centered: Whether to center the text (default: True)
    """
    if centered:
        # Process line by line for centering
        lines = text.split('\n')
        for line in lines:
            centered_line = center_text(line)
            for char in centered_line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            sys.stdout.write('\n')
            sys.stdout.flush()
    else:
        # Original behavior
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')
        sys.stdout.flush()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='F1 Analysis Agent - Aerodynamics, Tyres, Cars & General F1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Aerodynamics (original functionality)
  python main.py "What is the front wing downforce at different speeds?"
  python main.py "Calculate drag force at 300 km/h"
  python main.py "Compare DRS open vs closed"
  python main.py "Explain ground effect"
  
  # Tyres (NEW!)
  python main.py "What's the difference between soft and hard tyres?"
  python main.py "How long do medium tyres last?"
  python main.py "What tyre strategy should I use?"
  
  # Car Performance (NEW!)
  python main.py "What is top speed in F1?"
  python main.py "How do F1 cars brake?"
  python main.py "What is telemetry data?"
  
  # General F1 (NEW!)
  python main.py "What is Monaco circuit like?"
  python main.py "What is DRS?"
  python main.py "What happens in a pit stop?"
  
  # Interactive mode
  python main.py --interactive
  
{get_enhanced_supported_questions_text()}
        """
    )
    
    parser.add_argument(
        'question',
        nargs='?',
        help='Question about F1 aerodynamics'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--mcp',
        action='store_true',
        help='Attempt to use MCP physics server (experimental)'
    )
    
    parser.add_argument(
        '--no-fastf1',
        action='store_true',
        help='Disable Fast-F1 data integration'
    )
    
    args = parser.parse_args()
    
    # Initialize agent with Fast-F1 enabled by default and optional MCP
    agent = F1AeroAgent(
        enable_fastf1=not args.no_fastf1,
        enable_mcp=args.mcp
    )
    
    if args.interactive:
        run_interactive_mode(agent)
    elif args.question:
        run_single_question(agent, args.question)
    else:
        parser.print_help()
        sys.exit(1)


def run_single_question(agent: F1AeroAgent, question: str):
    """
    Process a single question and display results with streaming output.
    
    Args:
        agent: F1AeroAgent instance
        question: User's question
    """
    width = get_terminal_width()
    print(center_text(f"\n{RED}{'═' * min(80, width - 4)}{RESET}"))
    print(center_text(f"{RED}{BOLD}🏎️  F1 AGENT - SINGLE QUERY MODE  💨{RESET}"))
    print(center_text(f"{RED}{'═' * min(80, width - 4)}{RESET}"))
    print(f"\n{WHITE}{BOLD}Question:{RESET} {WHITE}{question}{RESET}\n")
    
    # Fun racing car animation
    racing_car_animation(40, "Analyzing your question")
    
    # Process question
    result = agent.process_question(question)
    
    # Check if visualization was created
    has_visualization = (
        result.get('visualization_message') or
        result.get('graph_path') or
        result.get('visualization')
    )
    
    if has_visualization:
        # Simplified output for visualizations
        viz_path = (
            result.get('graph_path') or
            result.get('visualization') or
            'visualization file'
        )
        print_checkered_flag()
        print(f"{RED}{BOLD}🏁 Visualization created successfully!{RESET}")
        print(f"{WHITE}📊 Saved to:{RESET} {WHITE}{viz_path}{RESET}")
        print()
        print_victory_celebration()
    else:
        # Full response for non-visualization answers
        response = agent.format_response(result)
        width = get_terminal_width()
        print(f"\n{RED}{'─' * min(80, width - 4)}{RESET}")
        print(center_text(f"{RED}{BOLD}🏁 RESPONSE:{RESET}"))
        print()
        stream_text(response, delay=0.02)
        print(f"\n{RED}{'─' * min(80, width - 4)}{RESET}\n")
        
    # Show a random racing fact
    print_racing_fact()


def run_interactive_mode(agent: F1AeroAgent):
    """
    Run agent in interactive mode with streaming text output and chat box.
    
    Args:
        agent: F1AeroAgent instance
    """
    global lap_counter
    lap_counter = 0
    
    print(center_multiline_text(LARGE_BANNER))
    print(center_multiline_text(RACING_CAR))
    print(center_text(f"{RED}Welcome to {RED}{BOLD}AbbyGPT{RESET}{RED}, your AI Racing Engineer!{RESET}"))
    print(center_text(f"{RED}Powered by advanced aerodynamics, telemetry, and racing knowledge.{RESET}"))
    print()
    print(center_text(f"{RED}🏁 Ready to analyze F1 data and answer your questions!{RESET}"))
    print()
    print(center_text(f"{RED}Commands: {RED}'clear'{RESET} {RED}(pit stop) | {RED}'help'{RESET} {RED}| {RED}'quit'{RESET} {RED}(finish race){RESET}"))
    print()
    
    # Show initial racing fact
    print_racing_fact()
    
    while True:
        try:
            # Display chat box and get user input
            lap_counter += 1
            print(f"\n{draw_chat_box('Type your question (or \"help\", \"clear\", \"quit\"):', lap_counter)}")
            
            # Position cursor for input (move up to the prompt line)
            # Calculate the position: 5 lines up (bottom of box) - 1 (prompt line)
            sys.stdout.write('\033[2A')  # Move up 2 lines to the prompt line
            
            # Move cursor to after the prompt text
            width = get_terminal_width()
            box_width = min(width - 4, 70)
            cursor_pos = (width - box_width) // 2 + len(f"  🏁 Lap {lap_counter} > ") + 1
            sys.stdout.write(f'\033[{cursor_pos}G')  # Move to column position
            sys.stdout.flush()
            
            question = input().strip()
            
            # Move cursor down past the box
            sys.stdout.write('\033[3B')  # Move down 3 lines
            sys.stdout.flush()
            
            # Decrement lap counter since we incremented it before input
            lap_counter -= 1
            
            if not question:
                continue
            
            # Increment lap counter for actual processing
            lap_counter += 1
            
            # Handle special commands
            if question.lower() in ['quit', 'exit', 'q']:
                width = get_terminal_width()
                print(f"\n{RED}{BOLD}{'═' * min(60, width - 4)}{RESET}")
                print(f"{RED}{BOLD}🏁 Race finished! Thanks for using AbbyGPT!{RESET}")
                print(f"{WHITE}Total laps completed: {lap_counter}{RESET}")
                print(f"{RED}{BOLD}{'═' * min(60, width - 4)}{RESET}\n")
                print_checkered_flag()
                print(f"{WHITE}See you at the next Grand Prix! 🏎️💨{RESET}")
                print()
                break
            
            if question.lower() in ['clear', 'reset']:
                agent.clear_conversation_history()
                print(f"\n{RED}{BOLD}🔧 PIT STOP! 🔧{RESET}")
                print(f"{WHITE}✓ Conversation history cleared{RESET}")
                print(f"{WHITE}✓ Fresh tyres fitted{RESET}")
                print(f"{WHITE}✓ Ready to race again!{RESET}")
                print()
                # Show a racing fact after pit stop
                print_racing_fact()
                continue
            
            if question.lower() in ['help', 'h', '?']:
                width = get_terminal_width()
                print(f"\n{RED}{BOLD}{'═' * min(60, width - 4)}{RESET}")
                print(f"{RED}{BOLD}📋 SUPPORTED QUESTIONS & COMMANDS:{RESET}")
                print(f"{RED}{BOLD}{'═' * min(60, width - 4)}{RESET}")
                print(get_enhanced_supported_questions_text())
                print(f"\n{WHITE}{BOLD}Special Commands:{RESET}")
                print(f"{WHITE}'clear'{RESET} - Pit stop (clear conversation history)")
                print(f"{WHITE}'help'{RESET}  - Show this help message")
                print(f"{WHITE}'quit'{RESET}  - Finish the race (exit)")
                print(f"{RED}{BOLD}{'═' * min(60, width - 4)}{RESET}\n")
                continue
            
            # Process question with spinning animation
            spinning_tire_animation(1.5)
            result = agent.process_question(question)
            
            # Check if visualization was created
            has_visualization = (
                result.get('visualization_message') or
                result.get('graph_path') or
                result.get('visualization')
            )
            
            if has_visualization:
                # Simplified output for visualizations
                viz_path = (
                    result.get('graph_path') or
                    result.get('visualization') or
                    'visualization file'
                )
                width = get_terminal_width()
                print(f"\n{RED}{'─' * min(60, width - 4)}{RESET}")
                print(f"{RED}{BOLD}🏁 Visualization created successfully!{RESET}")
                print(f"{WHITE}📊 Saved to:{RESET} {WHITE}{viz_path}{RESET}")
                print(f"{RED}{'─' * min(60, width - 4)}{RESET}\n")
            else:
                # Full response for non-visualization answers
                response = agent.format_response(result)
                width = get_terminal_width()
                print(f"\n{RED}{'─' * min(60, width - 4)}{RESET}")
                print(center_text(f"{RED}{BOLD}🏁 RESPONSE:{RESET}"))
                print()
                stream_text(response, delay=0.02)
                print(f"\n{RED}{'─' * min(60, width - 4)}{RESET}")
            
            # Occasionally show a racing fact (every 3 laps)
            if lap_counter % 3 == 0:
                print_racing_fact()
            
        except KeyboardInterrupt:
            print(f"\n\n{WHITE}⚠️  Race interrupted! Exiting...{RESET}")
            print(f"{WHITE}Laps completed: {lap_counter}{RESET}")
            print()
            break
        except Exception as e:
            print(f"\n{RED}{BOLD}🔴 ERROR ON TRACK!{RESET}")
            print(f"{RED}Error:{RESET} {WHITE}{e}{RESET}")
            print(f"{WHITE}Please try again or type 'help' for supported questions.{RESET}")
            print()


if __name__ == '__main__':
    main()

# Made with Bob

