"""
Core implementation of the Kradle Minecraft agent.
"""
from typing import Optional, List, Dict, Union
import time
from rich.console import Console
from rich.table import Table
from rich import box
from kradle.models import Observation
from kradle.memory.standard_memory import StandardMemory


class KradleMinecraftAgent:
    """Base class for Kradle Minecraft agents"""
    
    def __init__(self, slug: str, memory: Optional[StandardMemory] = StandardMemory(), action_delay: int = 100):
        # Basic configuration
        self.slug = slug
        self.action_delay = action_delay
        self.console = Console()
        
        # State management
        self.task: Optional[str] = None
        self.commands: Optional[Dict] = None
        self.js_functions: Optional[Dict] = None
        self.participant_id: Optional[str] = None
        self.memory = memory
        
        # Styling
        self._agent_colors = ["cyan", "magenta", "green", "yellow", "blue", "red", "white"]
        self.color = self._agent_colors[hash(slug) % len(self._agent_colors)]
    
    def _display_state(self, state: Observation) -> None:
        """Display current agent state in console with distinct agent styling."""
        header = f"[bold {self.color}]{'='*20} Agent: {self.slug} {'='*20}[/bold {self.color}]"
        timestamp = time.strftime('%H:%M:%S')
        
        table = Table(
            box=box.ROUNDED, 
            show_header=False, 
            padding=(0, 1),
            border_style=self.color
        )
        table.add_column("Category", style=self.color)
        table.add_column("Value", style="bright_" + self.color)
        
        self.console.print("\n")
        self.console.print(header)
        self.console.print(f"[{self.color}]Event Received at {timestamp} (Port: {self.port})[/{self.color}]")
        
        table.add_row("Position", f"x: {state.x:.2f}, y: {state.y:.2f}, z: {state.z:.2f}")
        table.add_row("Inventory", ", ".join(state.inventory) if state.inventory else "empty")
        table.add_row("Equipped", state.equipped if state.equipped else "nothing")
        table.add_row("Entities", ", ".join(state.entities) if state.entities else "none")
        table.add_row("Blocks", ", ".join(state.blocks) if state.blocks else "none")
        table.add_row("Craftable", ", ".join(state.craftable) if state.craftable else "none")
        
        self.console.print(table)
    
    def initialize_agent(self, agent_config) -> List[str]:
        """Called when agent is initialized. Override in subclass."""
        return []
    
    def on_event(self, data: Observation) -> Dict:
        """Process the current state and return an action. Must be implemented by subclasses."""
        raise NotImplementedError("Agents must implement event() method")