from pathlib import Path
import shutil
import sys
import os
from typing import Callable, Optional, Union
import requests
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from InquirerPy import inquirer
from InquirerPy.utils import InquirerPyStyle

from jay_ai.cli_types import LLMProvider, STTProvider, TTSProvider
from jay_ai.agent_template import get_agent_template
from jay_ai.utils import fetch_site_url, fetch_headers

console = Console()


def init_cli_command(getenv: Callable[[str, Optional[str]], Optional[str]] = os.getenv):
    def select_and_configure_provider(
        provider_enum: Union[type[STTProvider], type[LLMProvider], type[TTSProvider]],
        provider_display_name: str,
        env_var_inputs: dict,
        provider_api_keys: dict,
    ):
        display_labels = [provider.value.display_label for provider in provider_enum]

        chosen_label = inquirer.select(
            message=f"Select your {provider_display_name} provider",
            qmark="",
            instruction="(arrow keys to choose, then Enter)",
            pointer="❯",
            amark="",
            choices=display_labels,
            style=InquirerPyStyle(
                {
                    "question": "bold fg:#1E90FF",
                    "instruction": "italic",
                    "answer": "bold fg:#1E90FF",
                }
            ),
        ).execute()

        console.clear()

        chosen_provider = next(
            (p for p in provider_enum if p.value.display_label == chosen_label), None
        )
        for provider_env_var in chosen_provider.value.env_var_keys:
            key = provider_env_var.env_var_key
            if key not in env_var_inputs:
                existing_val = getenv(key, None)
                if existing_val:
                    console.print(f"Using the '{key}' that's already in .env")
                    env_var_inputs[key] = existing_val
                    provider_api_keys[key] = existing_val
                else:
                    # Ask the user for the new key
                    if provider_env_var.is_json:
                        console.print(
                            Panel.fit(
                                f"[bold]Enter JSON credentials for {chosen_provider.value.display_label}. "
                                "Paste them below (single line):[/bold]"
                            ),
                            style="#1E90FF",
                        )
                    else:
                        console.print(
                            Panel.fit(
                                f"[bold]Enter API key for {chosen_provider.value.display_label}:[/bold]"
                            ),
                            style="#1E90FF",
                        )
                    user_input = Prompt.ask(f"[bold]{key}[/bold]")
                    console.clear()
                    env_var_inputs[key] = user_input
                    provider_api_keys[key] = user_input

        return chosen_provider

    website_url = fetch_site_url()
    console.clear()

    # Check JAY_API_KEY
    jay_api_key = getenv("JAY_API_KEY", None)
    if jay_api_key:
        console.print("Using the JAY_API_KEY already defined in .env")
    else:
        console.print(
            Panel.fit(
                f"[bold]Retrieve your Jay API key at: [/bold][underline]{website_url}/dashboard/agent/settings[/underline]",
            ),
            style="#1E90FF",
        )
        jay_api_key = Prompt.ask("[bold]Enter your Jay API key[/bold]")
        console.clear()

    # Check JAY_DEVELOPER_ID
    jay_dev_id = getenv("JAY_DEVELOPER_ID", None)
    if jay_dev_id:
        console.print("Using the JAY_DEVELOPER_ID already defined in .env")
    else:
        console.print(
            Panel.fit(
                f"[bold]Retrieve your Jay Developer ID at: [/bold][underline]{website_url}/dashboard/agent/settings[/underline]",
            ),
            style="#1E90FF",
        )
        jay_dev_id = Prompt.ask("[bold]Enter your Jay Developer ID[/bold]")
        console.clear()

    # Check whether the user has Ngrok installed
    if shutil.which("ngrok") is None:
        console.print(
            "[red]Error: Ngrok is not installed. Please install it from https://ngrok.com/[/red]"
        )
        sys.exit(1)

    # We'll build a dictionary of every environment variable that the user enters.
    env_var_inputs = {"JAY_API_KEY": jay_api_key, "JAY_DEVELOPER_ID": jay_dev_id}

    # Let the user pick STT, LLM, TTS providers
    provider_api_keys = {}
    stt_provider = select_and_configure_provider(
        STTProvider, "speech-to-text", env_var_inputs, provider_api_keys
    )
    llm_provider = select_and_configure_provider(
        LLMProvider, "LLM", env_var_inputs, provider_api_keys
    )
    tts_provider = select_and_configure_provider(
        TTSProvider, "text-to-speech", env_var_inputs, provider_api_keys
    )

    console.print("[bold]Fetching agent ID from the dashboard...[/bold]")

    # Get the agent IDs from the database
    headers = fetch_headers(env_var_inputs["JAY_API_KEY"])
    try:
        resp = requests.get(f"{website_url}/api/agents/getAgentIds", headers=headers)
        if resp.status_code != 200:
            console.print(
                f"[red]Error retrieving agent IDs from {website_url}/api/agents/getAgentIds: "
                f"{resp.status_code} {resp.text}[/red]"
            )
            sys.exit(1)
        data = resp.json()
        agent_ids = data.get("agentIds", [])
        if len(agent_ids) == 0:
            console.print(
                "[red]Error: Could not find an agent ID. Please report this to the developers.[/red]"
            )
            sys.exit(1)
        elif len(agent_ids) > 1:
            console.print(
                "[red]Error: Exactly one agent ID is required, but we found more than one. You should update to the latest Jay package version. If the issue persists, please report it to the developers.[/red]"
            )
            sys.exit(1)
        agent_id = agent_ids[0]
    except Exception as e:
        console.print(f"[red]Error fetching agent IDs: {e}[/red]")
        sys.exit(1)

    # Create or overwrite agent
    agent_py_content = get_agent_template(
        agent_id=agent_id,
        stt_provider=stt_provider,
        llm_provider=llm_provider,
        tts_provider=tts_provider,
    )
    agent_file_path = Path("agent/main.py")
    if not agent_file_path.exists():
        agent_file_path.parent.mkdir(parents=True, exist_ok=True)
        with agent_file_path.open("w", encoding="utf-8") as f:
            f.write(agent_py_content)
        console.print(f"[green]Agent was created at: {str(agent_file_path)}.[/green]")
    else:
        existing = agent_file_path.read_text(encoding="utf-8")
        if existing.strip() != agent_py_content.strip():
            overwrite = Confirm.ask(
                f"[bold yellow]Agent already exists at: {str(agent_file_path)}. Overwrite?[/bold yellow]"
            )
            if overwrite:
                with agent_file_path.open("w", encoding="utf-8") as f:
                    f.write(agent_py_content)
                console.print("Agent file was overwritten.")
            else:
                console.print("Skipping overwrite of agent.")

    # Create or update the .env file
    dot_env_path = Path(".env")
    if dot_env_path.exists():
        lines_to_append = []

        for key, new_value in env_var_inputs.items():
            old_value = getenv(key, None)
            if old_value is None:
                # This key doesn't exist in .env (or system env), so add it
                lines_to_append.append(f"{key}={new_value}")

        if lines_to_append:
            to_append = ["", "# The following lines were added by `jay init`:"]
            to_append.extend(lines_to_append)
            with dot_env_path.open("a", encoding="utf-8") as f:
                f.write("\n".join(to_append) + "\n")
            console.print("[green]Appended new environment variables to .env[/green]")
    else:
        # Create a new .env file
        with dot_env_path.open("w", encoding="utf-8") as f:
            content_lines = [f"{k}={v}" for k, v in env_var_inputs.items()]
            f.write("# Environment variables for your Jay agent\n")
            f.write("\n".join(content_lines) + "\n")
        console.print("[green]Created a new .env file[/green]")

    # Fetch existing env var keys from DB
    try:
        resp = requests.get(f"{website_url}/api/envVars/get", headers=headers)
        if resp.status_code != 200:
            console.print(
                f"[red]Error retrieving environment variables from DB: "
                f"{resp.status_code} {resp.text}[/red]"
            )
            sys.exit(1)
        data = resp.json()
        existing_db_envvars = data.get("envVars", [])
        db_keys = [item["key"] for item in existing_db_envvars]
    except Exception as e:
        console.print(f"[red]Error calling envVars/get: {e}[/red]")
        sys.exit(1)

    # Determine which env vars are new or would be overwritten
    keys_to_save = [k for k in list(provider_api_keys.keys()) if k not in db_keys]
    keys_already_saved = [k for k in list(provider_api_keys.keys()) if k in db_keys]

    if not keys_to_save:
        console.print(
            "[yellow]No environment variables to store in Jay's database. Skipping DB update.[/yellow]"
        )
        console.print("[green]Initialization complete.[/green]")
        return

    if keys_already_saved:
        console.print(
            Panel.fit(
                f"[bold yellow]The following environment variable keys are already stored "
                f"in Jay's database and will not be overwritten:[/bold yellow]\n"
                f"[bold]{', '.join(keys_already_saved)}[/bold]\n\n"
                f"To overwrite them manually, go to:\n"
                f"[underline]{website_url}/dashboard/agent/settings[/underline]"
            )
        )

    console.print(
        Panel.fit(
            f"[bold]We will store the following environment variable keys in Jay's database:[/bold]\n"
            f"{', '.join(keys_to_save)}"
        )
    )
    proceed = Confirm.ask("[bold]Confirm?[/bold]")
    if proceed:
        # Save the new env vars
        vars_to_save = [{"key": k, "value": provider_api_keys[k]} for k in keys_to_save]

        payload = {"variables": vars_to_save}
        try:
            save_resp = requests.post(
                f"{website_url}/api/envVars/save", json=payload, headers=headers
            )
            if save_resp.status_code != 200:
                console.print(
                    f"[red]Error saving environment variables: "
                    f"{save_resp.status_code} - {save_resp.text}[/red]"
                )
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error saving environment variables: {e}[/red]")
            sys.exit(1)

        console.print(
            Panel.fit(
                "[bold green]Your credentials have been stored in Jay's database. [/bold green]\n"
                f"You can view/modify them at [underline]{website_url}/dashboard/agent/settings[/underline].\n\n"
                "[bold green]Project successfully initialized![/bold green]"
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[yellow]Understood. You can always update environment variables manually "
                f"at [underline]{website_url}/dashboard/agent/settings[/underline][/yellow]"
            )
        )
        console.print("[green]Initialization complete.[/green]")
