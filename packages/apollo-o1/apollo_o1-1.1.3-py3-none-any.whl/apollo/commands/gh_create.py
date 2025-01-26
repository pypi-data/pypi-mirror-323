import os
import questionary
import subprocess
from halo import Halo
from apollo.utils.config import load_config, save_config, cache_username
from apollo.utils.directories import create_directory, detect_directory, create_readme
from apollo.utils.run_command import run_command


def gh_create():
    """Create a new GitHub repository and initialize it locally.

    \b
    Features:
        - Allows you to specify a repository name and description.
        - Option to choose whether the repository is public or private.
        - Automatically initializes the repository with a README.
        - Sets up a remote connection to GitHub using the GitHub CLI.

    \b
    Considerations:
        - Ensure you are authenticated with the GitHub CLI (`gh auth login`) before using this command.
        - Requires the GitHub CLI installed locally.
    """

    # Load configuration
    config = load_config()

    cache_username(config)

    spinner = Halo(spinner="dots")

    # Confirm or select a directory
    if config["cached_directories"]:
        choices = config["cached_directories"] + [
            "Use Current Directory",
            "Use Different Directory",
        ]
        directory_choice = questionary.select(
            "Select a directory:", choices=choices
        ).ask()

        if directory_choice == "Use Current Directory":
            parent_dir = os.getcwd()
        elif directory_choice == "Use Different Directory":
            parent_dir = detect_directory()
        else:
            parent_dir = directory_choice
    else:
        parent_dir = detect_directory()

    # Save the selected directory if not already cached
    if parent_dir not in config["cached_directories"]:
        save_dir = questionary.confirm(
            f"Would you like to save '{parent_dir}' for future use?"
        ).ask()
        if save_dir:
            spinner.start(f"Saving directory '{parent_dir}'...")
            config["cached_directories"].append(parent_dir)
            save_config(config)
            spinner.succeed(f"Directory '{parent_dir}' saved.")

    # Prompt for repository details
    repo_name = questionary.text("Enter the repository name:").ask()
    repo_description = questionary.text("Enter a description for the repository:").ask()
    private = questionary.confirm("Should the repository be private?").ask()

    # Create the repository
    visibility = "private" if private else "public"

    try:
        run_command(
            f"gh repo create {repo_name} --{visibility} --description '{repo_description}' --confirm",
            start=f"Creating {visibility} repository on GitHub using GitHub CLI...",
        )
        spinner.succeed(
            f"Created {visibility} repository on GitHub using GitHub CLI Successfully!"
        )
    except subprocess.CalledProcessError as e:
        spinner.fail(
            f"Creating {visibility} repository on GitHub using GitHub CLI failed with error: {e.stderr}"
        )

    full_path = os.path.join(parent_dir, repo_name)

    # Create the local directory structure
    create_directory(full_path)

    # Write the README.md file
    create_readme(full_path, repo_name, repo_description)

    git_url = f"https://github.com/{config["github_username"]}/{repo_name}.git"  # Adjust if using SSH

    # push the repository
    run_command("git init", cwd=full_path, start="Initializing Git repository...")
    run_command("git add README.md", cwd=full_path, start="Staging README.md...")
    run_command(
        'git commit -m "initializing repo with README"',
        cwd=full_path,
        start="Committing with message 'initializing repo with README'...",
    )
    run_command(
        "git branch -M main",
        cwd=full_path,
        start="Renaming default branch to 'main'...",
    )
    run_command(
        f"git remote add origin {git_url}",
        cwd=full_path,
        start=f"Adding remote origin: {git_url}...",
    )
    run_command(
        "git push -u origin main",
        cwd=full_path,
        start="Pushing to remote repository...",
    )

    spinner.succeed("Repository successfully created and pushed! 🥳")
