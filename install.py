import os, sys
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ascii_logo = """
__     ___     _            _     _
\ \   / (_) __| | ___  ___ | |   (_)_ __   __ _  ___
 \ \ / /| |/ _` |/ _ \/ _ \| |   | | '_ \ / _` |/ _ \
  \ V / | | (_| |  __/ (_) | |___| | | | | (_| | (_) |
   \_/  |_|\__,_|\___|\___/|_____|_|_| |_|\__, |\___/
                                          |___/
"""

def install_package(*packages):
    subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

def setup_rich_console():
    install_package("requests", "rich", "ruamel.yaml")
    from rich.console import Console
    from rich.panel import Panel
    from rich.box import DOUBLE
    from translations.translations import translate as t

    console = Console()
    width = max(len(line) for line in ascii_logo.splitlines()) + 4
    welcome_panel = Panel(
        ascii_logo,
        width=width,
        box=DOUBLE,
        title="[bold green]🌏[/bold green]",
        border_style="bright_blue"
    )
    console.print(welcome_panel)
    return console, Panel, t

def setup_chinese_language():
    from translations.translations import DISPLAY_LANGUAGES
    from core.config_utils import update_key
    update_key("display_language", "zh-CN")

def install_torch():
    # Install PyTorch version suitable for Colab environment
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "torch==2.0.0",
        "torchaudio==2.0.0",
        "--index-url",
        "https://download.pytorch.org/whl/cu118"
    ])

def install_requirements(console, Panel, t):
    try:
        # First install basic pip packages
        basic_packages = [
            "librosa>=0.10.0",
            "pytorch-lightning>=2.0.0",
            "lightning>=2.0.0",
            "transformers>=4.39.0",
            "moviepy>=1.0.0",
            "numpy>=1.26.0",
            "openai>=1.0.0",
            "opencv-python>=4.0.0",
            "openpyxl>=3.1.0",
            "pandas>=2.0.0",
            "pydub>=0.25.0",
            "PyYAML>=6.0.0",
            "replicate>=0.33.0",
            "requests>=2.32.0",
            "resampy>=0.4.0",
            "spacy>=3.7.0",
            "yt-dlp",
            "json-repair",
            "ruamel.yaml",
            "autocorrect-py",
            "ctranslate2>=4.0.0",
            "edge-tts",
            "syllables",
            "pypinyin",
            "g2p-en"
        ]

        for package in basic_packages:
            try:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    package
                ])
                console.print(f"✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                console.print(f"× Failed to install {package}: {str(e)}", style="red")
                raise

        # Then install git packages
        git_packages = [
            "demucs[dev] @ git+https://github.com/adefossez/demucs",
            "whisperx @ git+https://github.com/m-bain/whisperx.git@7307306a9d8dd0d261e588cc933322454f853853"
        ]

        for package in git_packages:
            try:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    package
                ])
                console.print(f"✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                console.print(f"× Failed to install {package}: {str(e)}", style="red")
                raise
    except subprocess.CalledProcessError as e:
        console.print(Panel(t("❌ Failed to install requirements:") + str(e), style="red"))
        raise

def main():
    # Setup console
    console, Panel, t = setup_rich_console()
    console.print(Panel.fit(t("🚀 Starting Installation"), style="bold magenta"))
    
    # Set Chinese language
    setup_chinese_language()
    
    # Install PyTorch with CUDA support
    console.print(Panel(t("🎮 Installing PyTorch with CUDA support..."), style="cyan"))
    install_torch()
    
    # Install other dependencies
    console.print(Panel(t("Installing dependencies..."), style="cyan"))
    install_requirements(console, Panel, t)
    
    # Installation complete message
    success_text = (
        t("✅ Installation completed!\n\n") +
        t("You can now use VideoLingo.")
    )
    console.print(Panel(success_text, style="bold green"))

if __name__ == "__main__":
    main()
