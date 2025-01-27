"""cli app to use AI to OCR files."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from par_ai_core.llm_config import LlmConfig, llm_run_manager
from par_ai_core.llm_image_utils import image_to_base64, try_get_image_type
from par_ai_core.llm_providers import LlmProvider, provider_env_key_names, provider_vision_models
from par_ai_core.par_logging import console_out
from par_ai_core.pricing_lookup import PricingDisplay
from par_ai_core.provider_cb_info import get_parai_callback
from pdf2image import convert_from_path
from rich.panel import Panel
from rich.text import Text

from . import __application_binary__, __application_title__, __version__

load_dotenv()
load_dotenv(Path(f"~/.{__application_binary__}.env").expanduser())

app = typer.Typer()


doc_folder = Path("./test_data").absolute()
input_file_default = doc_folder / "test1.pdf"
system_prompt_file_default = Path(__file__).parent / "system_prompt.md"


def convert_pdf_to_images(
    *,
    pdf_path: Path,
    output_path: Path | None = None,
    pages: list[int] | None = None,
) -> list[Path]:
    """convert_pdf_to_images"""

    if not output_path:
        output_path = pdf_path.parent
    output_path.mkdir(exist_ok=True, parents=True)

    console_out.print(f"Converting {pdf_path} to images and saving to {output_path}")

    ret: list[Path] = []
    image_data = convert_from_path(
        pdf_path,
        output_folder=output_path,
        first_page=pages[0] if pages else None,  # type: ignore
        last_page=pages[-1] if pages else None,  # type: ignore
    )
    if pages:
        curr_page = 0
        for i, image in enumerate(image_data):
            if pages[0] + i not in pages:
                continue
            page_num = pages[curr_page]
            curr_page += 1
            out_image_path = output_path / (pdf_path.stem + "-page" + str(page_num).zfill(3) + ".jpg")
            image.save(out_image_path, "JPEG")
            ret.append(out_image_path)
    else:
        for i, image in enumerate(image_data):
            out_image_path = output_path / (pdf_path.stem + "-page" + str(i + 1).zfill(3) + ".jpg")
            image.save(out_image_path, "JPEG")
            ret.append(out_image_path)
    return ret


def ai_ocr(
    llm_config: LlmConfig,
    system_prompt_text: str,
    pdf_path: Path,
    images: list[Path],
    output_path: Path,
) -> Path:
    """Use AI OCR to extract text from images"""

    model = llm_config.build_chat_model()
    system_prompt = (
        "system",
        system_prompt_text,
    )

    pages: list[str] = []

    for i, image in enumerate(images):
        text_file = output_path / (image.stem + f"-{llm_config.model_name}.md")
        if text_file.exists():
            pages.append(text_file.read_text(encoding="utf-8"))
            continue
        console_out.print(f"Extracting text from image {i + 1} of {len(images)}")
        image_type = try_get_image_type(image)
        image_base_64 = image_to_base64(image.read_bytes(), image_type)
        content = [
            {
                "type": "text",
                "text": "Please extract all text from the following image into markdown.",
            },
            {
                "type": "image_url",
                "image_url": {"url": image_base_64},
            },
        ]
        try:
            response = model.invoke(
                [system_prompt, ("user", content)],  # type: ignore
                config=llm_run_manager.get_runnable_config(model.name),
            )  # type: ignore
            content = str(response.content).strip()
            content = content.replace("```markdown", "").replace("```", "")
            text_file.write_text(content, encoding="utf-8")
            pages.append(str(content))
        except Exception as e:  # pylint: disable=broad-except
            pages.append(f"Error extracting text from image {i + 1}: {e}")
            console_out.print(f"[bold red]Error extracting text from image[/bold red]: {i + 1}: {e}")
    text_file = output_path / (pdf_path.stem + f"-{llm_config.model_name}.md")
    text_file.write_text("\n\n".join(pages), encoding="utf-8")
    return text_file


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"{__application_title__}: {__version__}")
        raise typer.Exit()


# pylint: disable=too-many-arguments,too-many-branches, too-many-positional-arguments
@app.command()
def main(
    ai_provider: Annotated[
        LlmProvider,
        typer.Option("--ai-provider", "-a", help="AI provider to use for processing"),
    ] = LlmProvider.OPENAI,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help="AI model to use for processing. If not specified, a default model will be used.",
        ),
    ] = None,
    ai_base_url: Annotated[
        str | None,
        typer.Option(
            "--ai-base-url",
            "-b",
            help="Override the base URL for the AI provider.",
        ),
    ] = None,
    system_prompt_file: Annotated[
        Path,
        typer.Option("--system-prompt-file", "-p", help="File containing system prompt"),
    ] = system_prompt_file_default,
    input_file: Annotated[Path, typer.Option("--input-file", "-i", help="File to process")] = input_file_default,
    pricing: Annotated[
        PricingDisplay,
        typer.Option("--pricing", "-p", help="Enable pricing summary display"),
    ] = PricingDisplay.PRICE,
    pages: Annotated[
        str | None,
        typer.Option(
            "--pages",
            help="Comma-separated page numbers or hyphen-separated range (e.g., '1,3,5-7')",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for markdown files. Default is input file directory."),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-D",
            help="Enable debug mode",
        ),
    ] = False,
    version: Annotated[  # pylint: disable=unused-argument
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """OCR files using AI."""
    if not model:
        model = provider_vision_models[ai_provider]

    if ai_provider not in [LlmProvider.OLLAMA, LlmProvider.BEDROCK]:
        key_name = provider_env_key_names[ai_provider]
        if not os.environ.get(key_name):
            console_out.print(f"[bold red]{key_name} environment variable not set. Exiting...[/bold red]")
            raise typer.Exit(1)

    if not model:
        model = provider_vision_models[ai_provider]

    if not model:
        console_out.print(f"[bold red]Model not found for AI provider {ai_provider.value}. Exiting...[/bold red]")
        raise typer.Exit(1)

    if not input_file.exists():
        console_out.print(f"Input file {input_file} does not exist. Exiting...")
        raise typer.Exit(1)

    if not system_prompt_file.exists():
        console_out.print(f"System prompt file {system_prompt_file} does not exist. Exiting...")
        raise typer.Exit(1)

    # Set output path
    output_path = output or input_file.parent
    output_path.mkdir(parents=True, exist_ok=True)

    input_ext = input_file.suffix.lower()
    if input_ext == ".pdf":
        page_list = None
        if pages:
            page_list = []
            for page_range in pages.split(","):
                if "-" in page_range:
                    start, end = map(int, page_range.split("-"))
                    page_list.extend(range(start, end + 1))
                else:
                    page_list.append(int(page_range))
            page_list.sort()
        image_files = convert_pdf_to_images(pdf_path=input_file, output_path=output_path, pages=page_list)
    elif input_ext in {".jpg", ".jpeg", ".png"}:
        if pages:
            console_out.print("Warning: --pages option is ignored for non-PDF files.")
        image_files = [input_file]
    else:
        console_out.print(
            f"Input file {input_file} has an unsupported extension. Only pdf, jpg, and png are supported. Exiting..."
        )
        raise typer.Exit(1)

    llm_config = LlmConfig(provider=ai_provider, model_name=model, temperature=0.0, base_url=ai_base_url)

    # config summary info
    console_out.print(
        Panel.fit(
            Text.assemble(
                ("AI Provider: ", "cyan"),
                (f"{ai_provider.value}", "green"),
                "\n",
                ("Model: ", "cyan"),
                (f"{model}", "green"),
                "\n",
                ("AI Provider Base URL: ", "cyan"),
                (f"{ai_base_url or 'default'}", "green"),
                "\n",
                ("System Prompt: ", "cyan"),
                (f"{system_prompt_file.name}", "green"),
                "\n",
                ("Pricing: ", "cyan"),
                (f"{pricing}", "green"),
                "\n",
                ("Input File: ", "cyan"),
                (f"{input_file}", "green"),
                "\n",
                ("Pages: ", "cyan"),
                (f"{pages or 'All'}", "green"),
                "\n",
                ("Output Directory: ", "cyan"),
                (f"{output_path}", "green"),
                "\n",
                ("Pricing: ", "cyan"),
                (f"{pricing}", "green"),
                "\n",
                ("Debug: ", "cyan"),
                (f"{debug}", "green"),
                "\n",
            ),
            title="[bold]OCR Configuration",
            border_style="bold",
        )
    )
    with get_parai_callback(show_end=debug, show_pricing=pricing):
        start_time = time.time()
        markdown_file = ai_ocr(
            llm_config,
            system_prompt_file.read_text(encoding="utf-8"),
            input_file,
            image_files,
            output_path,
        )
        end_time = time.time()
        console_out.print(f"Output file: {markdown_file.absolute()}")
        console_out.print(
            f"Total time: {end_time - start_time:.1f}s Pages per second: {len(image_files) / (end_time - start_time):.2f}"
        )
    console_out.print("Cleaning up...")
    for f in output_path.glob("*.ppm"):
        f.unlink()


if __name__ == "__main__":
    app()
