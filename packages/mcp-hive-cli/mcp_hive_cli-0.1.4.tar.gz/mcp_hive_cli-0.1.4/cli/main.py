import click
import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


@click.group()
def cli():
    """MCP Agent CLI - Create and manage MCP agents

    Run 'mcp-hive --help' to see all available commands.
    Run 'mcp-hive COMMAND --help' to see detailed help for a specific command.
    """
    pass


@cli.command(help="Create a new MCP agent with the specified configuration")
@click.argument("name")
@click.option(
    "--hives",
    "-h",
    multiple=True,
    help="MCP hive URLs (can be specified multiple times). Defaults to http://localhost:8000/sse",
)
@click.option(
    "--system-prompt",
    "-s",
    help="System prompt for the agent. Defaults to a generic assistant prompt",
)
@click.option(
    "--model",
    "-m",
    help="LLM model to use. Defaults to claude-3-5-sonnet-20240620",
)
def create_agent(name, hives, system_prompt, model):
    """Create a new MCP agent with the specified configuration.

    Args:
        name: Name of the agent to create

    Examples:
        mcp-hive create-agent myagent
        mcp-hive create-agent myagent --hives http://hive1:8000/sse --hives http://hive2:8000/sse
        mcp-hive create-agent myagent --system-prompt "You are a helpful assistant"
    """
    # Create agent directory
    agent_dir = Path(name)
    agent_dir.mkdir(exist_ok=True)

    # Default config values
    config = {
        "hives": list(hives) if hives else ["http://localhost:8000/sse"],
        "system_prompt": system_prompt
        or "You are an expert assistant. Your goal is to help the user with their query.",
        "model": model or "claude-3-5-sonnet-20240620",
    }

    # Write config.yaml
    config_path = agent_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)

    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader("templates/agent"))

    # Generate agent.py from template
    agent_template = env.get_template("mcp_client.py.jinja")
    agent_path = agent_dir / "agent.py"
    with open(agent_path, "w") as f:
        f.write(agent_template.render())

    # Generate requirements.txt from template
    req_template = env.get_template("client.requirements.txt.jinja")
    req_path = agent_dir / "requirements.txt"
    with open(req_path, "w") as f:
        f.write(req_template.render())

    # Generate .env from template
    env_template = env.get_template("client.env.jinja")
    env_path = agent_dir / ".env"
    with open(env_path, "w") as f:
        f.write(env_template.render(**{}))

    click.echo(f"✨ Created new agent '{name}'")
    click.echo(f"📁 Location: {agent_dir.absolute()}")
    click.echo("\nTo start the agent, run `mcp-hive run {name}`\n")


@cli.command(help="Run an MCP agent")
@click.argument("agent_name")
def run_agent(agent_name):
    """Run an MCP agent from the specified directory.

    Args:
        agent_name: Name of the agent to run

    Examples:
        mcp-hive run myagent
    """
    import subprocess
    import sys
    from pathlib import Path

    agent_path = Path(agent_name) / "agent.py"
    if not agent_path.exists():
        click.echo(f"Error: agent.py not found in {agent_name}", err=True)
        sys.exit(1)

    click.echo(f"🚀 Starting agent from {agent_name}")
    subprocess.run([sys.executable, "agent.py"], cwd=agent_name)


def main():
    cli()


if __name__ == "__main__":
    main()
