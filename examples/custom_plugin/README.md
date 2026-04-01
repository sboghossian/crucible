# Example: Custom Plugin

This example demonstrates the Crucible Plugin API for registering custom agents.

## Structure

```
examples/custom_plugin/
├── plugin.yaml          # Plugin manifest
├── sentiment_agent.py   # Agent using @agent_plugin decorator
├── plugin_hooks.py      # Lifecycle hooks (before_run, after_run)
└── README.md
```

## Running

```bash
# Discover via directory
crucible --plugins-dir examples/custom_plugin research "AI trends 2025"

# Explicit module load
crucible --plugin sentiment_agent.SentimentAnalyzerAgent research "AI trends 2025"

# Dev mode with hot-reload
crucible --plugins-dir examples/custom_plugin --watch-plugins research "AI trends 2025"

# List loaded plugins
crucible plugins list --plugins-dir examples/custom_plugin
```

## Decorator API

```python
from crucible.plugins import agent_plugin
from crucible.core.agent import BaseAgent, AgentResult

@agent_plugin(
    name="my_custom_agent",
    description="Does something cool",
    version="1.0.0",
)
class MyAgent(BaseAgent):
    name = "my_custom_agent"

    async def run(self, **kwargs):
        return AgentResult(agent_name=self.name, success=True, output="done")
```

## Plugin Manifest

`plugin.yaml` lets you declare agents and hooks declaratively:

```yaml
name: my-plugin
version: 1.0.0
description: A custom agent plugin
author: Steph
agents:
  - class: MyAgent
    module: my_agent
hooks:
  before_run: my_hooks.setup
  after_run: my_hooks.cleanup
```

Load a manifest programmatically:

```python
from crucible.plugins import PluginLoader
loader = PluginLoader()
loader.load_from_manifest("examples/custom_plugin/plugin.yaml")
```
