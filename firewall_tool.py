from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess

class FirewallToolInput(BaseModel):
    """Input schema for FirewallBlockTool."""
    ip_address: str = Field(..., description="The IP address to block on the firewall.")

class FirewallBlockTool(BaseTool):
    name: str = "Firewall Block Tool"
    description: str = "Blocks malicious IP addresses using UFW on Ubuntu."
    args_schema: type[BaseModel] = FirewallToolInput  # This forces the agent to send only the IP

    def _run(self, ip_address: str):
        """Executes the UFW deny command for a specific IP."""
        try:
            # Subprocess: Using Python to execure terminal commands.
            # Using 'ufw deny' from terminal to tell Linux Firewall to drop traffic.
            command = [ "sudo", "ufw", "insert", "1",  "deny", "from", ip_address ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True              # If command fails STOP, throw an ERROR
            )

            return f"Successfuly added block rule for {ip_address}:{result.stdout}"
        
        except subprocess.CalledProcessError as e:
            return f"Failed to block IP. Error {e.stderr}"
        except Exception as e:
            return f"CRITICAL ERROR: Failed to execute firewall command. Details: {str(e)}"