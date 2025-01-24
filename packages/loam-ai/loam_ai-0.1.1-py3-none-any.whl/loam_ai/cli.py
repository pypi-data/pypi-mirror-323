import click
from rich.console import Console
from rich.table import Table
from .models import MODEL_CONFIGS
import base64
import json

from .client import BedrockClient

import logging

console = Console()
logging.basicConfig(level=logging.INFO, format="%(message)s")


@click.group()
def main():
    """AWS Bedrock CLI - Invoke AI models through AWS Bedrock"""
    pass


@main.command(name="list-models")
@click.option("--provider", help='Filter by provider (e.g., "anthropic")')
@click.option(
    "--output",
    type=click.Choice(["TEXT", "IMAGE", "EMBEDDING"]),
    help="Filter by output type",
)
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
def list_models(provider, output, profile, region):
    """List available foundation models"""
    try:
        client = BedrockClient(profile_name=profile, region_name=region)
        models = client.list_models(provider=provider, output_modality=output)

        table = Table(title="Available Foundation Models")
        table.add_column("Model ID", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Name", style="blue")
        table.add_column("Input", style="magenta")
        table.add_column("Output", style="magenta")

        for model in models:
            table.add_row(
                model.get("modelId", "N/A"),
                model.get("providerName", "N/A"),
                model.get("modelName", "N/A"),
                ", ".join(model.get("inputModalities", [])),
                ", ".join(model.get("outputModalities", [])),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing models: {str(e)}[/red]")


@main.command()
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
def session(profile, region):
    """Display current session information"""
    try:
        client = BedrockClient(profile_name=profile, region_name=region)
        info = client.get_session_info()

        table = Table(title="AWS Session Information")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Profile", info["profile"] or "default")
        table.add_row("Region", info["region"])
        table.add_row("Auth Type", info["credential_type"])

        if info["available_profiles"]:
            table.add_row("Available Profiles", "\n".join(info["available_profiles"]))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting session info: {str(e)}[/red]")


@main.command()
@click.option(
    "--model-id",
    "-m",
    required=True,
    help="Bedrock model ID (e.g., anthropic.claude-2:latest)",
)
@click.option("--prompt", "-p", required=True, help="Prompt to send to the model")
@click.option(
    "--temperature",
    "-t",
    default=0.7,
    type=float,
    help="Temperature (0-1) - higher means more creative",
)
@click.option(
    "--max-tokens", default=1000, type=int, help="Maximum number of tokens to generate"
)
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Show debug output of streaming chunks",
)
def invoke(model_id, prompt, temperature, max_tokens, profile, region, debug):
    """Invoke a Bedrock model with the specified parameters"""
    try:
        client = BedrockClient(profile_name=profile, region_name=region)

        if debug:
            console.print(f"Using profile: [cyan]{client.profile or 'default'}[/cyan]")
            console.print(f"Region: [cyan]{client.region}[/cyan]")
            console.print(f"Model: [cyan]{model_id}[/cyan]\n")

        generator = client.invoke_model(
            model_id=model_id,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            debug=debug,
        )

        if debug:
            console.print("\n[green]Response:[/green]")

        for chunk in generator:
            console.print(chunk, end="")

        print()  # newline at the end

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command(name="converse")
@click.option(
    "--model-id",
    "-m",
    required=True,
    help=(
        "Bedrock model ID (e.g. anthropic.claude-2:latest), "
        "or an inference profile ARN (e.g. "
        "arn:aws:bedrock:us-east-1:123456789123:inference-profile/...)"
    ),
)
@click.option(
    "--messages-file",
    "-f",
    type=click.Path(exists=True),
    help=(
        "Path to a JSON file containing a list of messages. "
        'Each message is {"role": "user"|"assistant"|"system", "content": [{"text": "..."}]}.'
    ),
)
@click.option(
    "--max-tokens",
    default=200,
    type=int,
    help="Maximum number of tokens to generate in the response",
)
@click.option(
    "--temperature",
    default=0.7,
    type=float,
    help="Temperature (0-1) - higher means more creative",
)
@click.option(
    "--top-p",
    default=0.9,
    type=float,
    help="Controls the diversity of generated text (0-1)",
)
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
@click.option("--debug", is_flag=True, default=False, help="Show debug output")
def converse(
    model_id, messages_file, max_tokens, temperature, top_p, profile, region, debug
):
    """
    Use the conversation API (converse_stream) with a list of messages (chat format).
    This is often required for Anthropic or other chat-based models/inference profiles.
    """
    client = BedrockClient(profile_name=profile, region_name=region)
    if debug:
        console.print(f"Using profile: [cyan]{client.profile or 'default'}[/cyan]")
        console.print(f"Region: [cyan]{client.region}[/cyan]")
        console.print(f"Model: [cyan]{model_id}[/cyan]\n")

    # 1) Load messages from file:
    if messages_file:
        with open(messages_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        console.print("[red]No messages file provided. Exiting.[/red]")
        return

    if debug:
        console.print("\n[green]Response:[/green]\n")

    try:
        generator = client.converse_model(
            model_id=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
            debug=debug,
        )

        for chunk in generator:
            console.print(chunk, end="")
        print()  # newline

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command(name="generate-embeddings")
@click.option(
    "--model-id",
    "-m",
    required=True,
    help="Bedrock embedding model ID (e.g., amazon.titan-embed-text-v2:0 or cohere.embed-multilingual-v3)",
)
@click.option(
    "--texts",
    "-t",
    multiple=True,
    required=False,
    help="Input text(s) to generate embeddings for. Use multiple --texts flags for multiple inputs.",
)
@click.option(
    "--image",
    "-i",
    type=click.Path(exists=True),
    required=False,
    help="Path to the input image to generate embeddings for.",
)
@click.option(
    "--input-file",
    "-f",
    type=click.Path(exists=True),
    help="Path to a file containing input texts (one per line). Overrides --texts if provided.",
)
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
@click.option("--debug", is_flag=True, default=False, help="Show debug output")
def generate_embeddings(model_id, texts, image, input_file, profile, region, debug):
    """Generate embeddings for the specified text(s) and/or image using a Bedrock embedding model."""
    if debug:
        console.print(f"Using profile: [cyan]{profile or 'default'}[/cyan]")
        console.print(f"Region: [cyan]{region}[/cyan]")
        console.print(f"Model: [cyan]{model_id}[/cyan]\n")
        console.print(f"Texts: {texts}")
        console.print(f"Image: {image}")
        console.print(f"Input file: {input_file}")
        console.print()
    try:
        # Get model configuration
        config = MODEL_CONFIGS.get(model_id)
        if not config:
            raise ValueError(f"Unsupported model ID: {model_id}")

        # Determine input texts
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                input_texts = [line.strip() for line in f if line.strip()]
        else:
            input_texts = list(texts)

        # Validate input based on model capabilities
        if image and not config.features.supports_images:
            console.print(
                f"[red]The model '{model_id}' does not support image inputs.[/red]"
            )
            return

        if config.provider.lower() == "amazon":
            if image and len(input_texts) > 1:
                console.print(
                    "[red]Amazon embedding models currently support only single text input when using image embedding. Please provide one text or use a different model.[/red]"
                )
                return
            if not input_texts and not image:
                console.print(
                    "[red]No input provided. Use --texts, --image, or both to provide inputs.[/red]"
                )
                return
        else:
            # Add additional provider-specific validations if necessary
            pass

        # Optionally, validate text length against max_context_length
        for idx, text in enumerate(input_texts, start=1):
            if (
                config.features.max_context_length
                and len(text) > config.features.max_context_length
            ):
                console.print(
                    f"[red]Input text {idx} exceeds the maximum context length of {config.features.max_context_length} characters for this model.[/red]"
                )
                return

        # Read and encode image if provided
        input_image = None
        if image:
            with open(image, "rb") as image_file:
                input_image = base64.b64encode(image_file.read()).decode("utf8")

        client = BedrockClient(profile_name=profile, region_name=region)
        embeddings = client.generate_embeddings(
            model_id=model_id,
            texts=input_texts if input_texts else None,
            image=input_image,
            debug=debug,
        )

        if debug:
            console.print(f"[green]Embeddings:[/green] {embeddings}")
            console.print(f"[green]Input Texts:[/green] {input_texts}")
            console.print(f"[green]Input Image:[/green] {image}")

        console.print(embeddings)

    except Exception as e:
        console.print(f"[red]Error generating embeddings: {str(e)}[/red]")


@main.command(name="list-inference-profiles")
@click.option("--profile", help="AWS profile name")
@click.option("--region", help="AWS region")
def list_inference_profiles(profile, region):
    """List available Inference Profiles"""
    try:
        client = BedrockClient(profile_name=profile, region_name=region)
        profiles = client.list_inference_profiles()

        table = Table(title="Available Inference Profiles")
        table.add_column("Inference Profile ARN", style="cyan")
        table.add_column("Inference Profile Name", style="green")

        for p in profiles:
            table.add_row(
                p.get("inferenceProfileArn", "N/A"),
                p.get("inferenceProfileName", "N/A"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing inference profiles: {str(e)}[/red]")


if __name__ == "__main__":
    main()
