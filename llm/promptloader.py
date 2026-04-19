from pathlib import Path

from common import logger

class PromptLoader:
    def __init__(self, base_path="prompts"):
        self.base_path = Path(base_path)
        logger.info(f'Base path for prompt loader: {self.base_path.absolute()}')


    def load(self, agent_name: str, version: str = "latest"):
        agent_folder = self.base_path / agent_name
        files = sorted(agent_folder.glob("*.txt"))
        
        if not files:
            raise FileNotFoundError(f'No prompts found in {agent_folder.absolute()} directory')

        target = files[-1] if version == "latest" else agent_folder / f"{version}.txt"

        if not target.exists():
            raise FileNotFoundError(f'Version {version} not found for agent {agent_name}.')

        with open(target, "r") as f:
            return f.read().strip()
