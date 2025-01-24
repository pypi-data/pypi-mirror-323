"""
Core implementation of the Kradle Minecraft agent.
"""
from typing import Optional, List, Dict, Union
import time
import logging
import os
import sys
import requests
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
        self.docs: Optional[Dict] = None
        self.skills: Optional[Dict] = None
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
    
    def on_event(self, data: Observation) -> str:
        """Process the current state and return an action. Must be implemented by subclasses."""
        raise NotImplementedError("Agents must implement event() method")
    
def create_session(api_key: str, challenge_slug: str, agents: Union[KradleMinecraftAgent, List[KradleMinecraftAgent]]) -> Optional[str]:
    """Create a new challenge session for one or more agents."""
    console = Console()
    logger = logging.getLogger(__name__)
    
    # Environment-specific URLs
    KRADLE_APP_URL = (
        "http://localhost:3000" 
        if os.getenv("KRADLE_DEV") 
        else "https://mckradleai.vercel.app"
    )
    KRADLE_APP_LIVE_SESSION_URL = "https://mckradleai-git-jt-session-map-kradle-f5bad6db.vercel.app/session-map"
    
    try:
        # Normalize agents to list
        agent_list = [agents] if not isinstance(agents, list) else agents
        
        # Validate agents
        for agent in agent_list:
            if not agent.url:
                raise ValueError(f"Agent {agent.slug} is not properly started")
            if not hasattr(agent, 'slug'):
                raise ValueError("Agent has no slug defined")
        
        # Prepare session data
        agent_data = [
            {
                'agentSlug': agent.slug,
                'agentUrl': agent.url
            }
            for agent in agent_list
        ]
        
        console.print("Launching session...")
        
        # Make API request
        response = requests.post(
            f'{KRADLE_APP_URL}/api/createSession',
            headers={
                'Content-Type': 'application/json',
                'kradle-api-key': api_key
            },
            json={
                'challengeSlug': challenge_slug,
                'agents': agent_data
            },
            timeout=30
        )
        
        if response.status_code in (200, 201):
            session_id = response.json()['sessionId']
            console.print("\nSession launched successfully!", style="bold green")
            session_url = f"{KRADLE_APP_LIVE_SESSION_URL}/{session_id}?_vercel_share=9GXlpNbfQWUP6jjM3VZ3RL9WRMT4qJVx"
            console.print(f"\nView it live: {session_url}")
            return session_id
            
        response.raise_for_status()
        
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        # Shutdown all agents
        for agent in agent_list:
            try:
                agent.shutdown()
            except:
                pass
        
        if isinstance(e, requests.RequestException):
            console.print(
                f"\n[yellow]Unable to reach Kradle Workbench at {KRADLE_APP_URL}\n"
                "Please try again in a few minutes.[/yellow]"
            )
        else:
            console.print(f"[red]Error: {str(e)}[/red]")
        
        sys.exit(1)
    
    return None