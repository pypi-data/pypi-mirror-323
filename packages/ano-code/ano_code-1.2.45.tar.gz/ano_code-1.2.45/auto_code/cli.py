
from ai_assistant.llm_cli import openai_client
from ai_assistant.prompt_llm import AIAssistant
from file_processing.error_handling import Failure, Ok
from ai_assistant.consts import COMMANDS
from file_processing import file_handling
from ai_assistant.llm_cli import openai_client
from ai_assistant.prompt_llm import AIAssistant
from ai_assistant.consts import COMMANDS
from rich.console import Console
from rich.theme import Theme
from yaspin import yaspin
from openai import APIConnectionError
import click


from requests import Response




custom_theme = Theme({"success": "green", "failure": "bold red", "fun": "purple"})


console = Console(theme=custom_theme)




@yaspin(text="Generating code documentation...")
def prompt(code: str):
    loader = yaspin()
    loader.start()
    assistant = AIAssistant(openai_client)
    result = assistant.run_assistant(code, COMMANDS["w_doc"])
    loader.stop()
    return result




@yaspin(text="Generating code documentation...")
def prompt(code: str)-> Failure | Ok:
    try:
        loader = yaspin()
        loader.start()
        assistant = AIAssistant(openai_client)
        result = assistant.run_assistant(code, COMMANDS["w_doc"])
        success = Ok(result)
        loader.stop()
        return success
    except APIConnectionError:
        failure = Failure("Network error, please check your internet connection")
        return failure
    except Exception as error:
        failure = Failure(error)
        return failure
    finally:
        loader.stop()

@click.group()
def cli():
    pass



@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('url', type=str)
@click.argument('repo_id', type=str)
def sniffer(directory, url, repo_id)-> Response:
    file_handling.run_req(directory, url, repo_id)


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def write_doc(directory):
    source_code = file_handling.process_directory(directory)
    response = prompt(source_code)
    if type(response) == Ok:
        file_handling.create_markdown_file("./documentation", response.data)
        console.print("check for: documentation.md at the root of your project 📁", style="fun")
        console.print("Thanks for using ano-code 😉.", style="fun")
    else:
        console.print(response.data, style="failure")


cli.add_command(write_doc)
cli.add_command(sniffer)


if __name__ == "__main__":
    write_doc()
    
