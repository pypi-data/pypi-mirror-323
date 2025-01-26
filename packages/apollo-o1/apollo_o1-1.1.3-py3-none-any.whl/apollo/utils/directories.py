import os
import questionary
from halo import Halo

spinner = Halo(spinner="dots")


def get_subdirectories(base_path):
    """Retrieve immediate subdirectories of a given base path, excluding .git."""
    return {
        d: os.path.join(base_path, d)
        for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and d != ".git"
    }


def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        spinner.start(f"Creating directory: {path}")
        os.makedirs(path)
        spinner.succeed(f"Created directory: {path} successfully!")


def create_readme(path, repo_name, repo_description):
    # Write the README.md file
    spinner.start("Creating README.md")
    readme_path = os.path.join(path, "README.md")

    with open(readme_path, "w") as readme_file:
        readme_file.write(f"# {repo_name}\n\n{repo_description}")
    spinner.succeed(f"README.md created in '{path}'!")


def detect_directory():
    """
    Detect the directory to use for creating a local repository.
    Prioritizes the Developer folder and its subdirectories.
    """
    home_directory = os.path.expanduser("~")
    default_developer_path = os.path.join(home_directory, "Developer")

    def handle_subdirectories(base_path):
        """
        Handle subdirectories within a given base path.
        """
        while True:
            subdirectories = get_subdirectories(base_path)
            if not subdirectories:
                spinner.info(
                    f"Reached end of subdirectories list... Using '{base_path}' as the directory for the local repository."
                )
                return base_path

            directory_choice = questionary.select(
                "Select a subdirectory to use or create a new one:",
                choices=list(subdirectories.keys()) + ["Use Current Directory", "Create a New Directory"],
            ).ask()

            if directory_choice == "Use Current Directory":
                spinner.info(
                    f"Using '{base_path}' as the directory for the local repository."
                )
                return base_path
            elif directory_choice == "Create a New Directory":
                new_directory = questionary.path(
                    "Enter the path for the new directory:"
                ).ask()
                create_directory(new_directory)
                return new_directory
            else:
                # Navigate into the selected subdirectory
                base_path = subdirectories[directory_choice]

    # Check if Developer directory exists
    if os.path.exists(default_developer_path):
        use_developer = questionary.confirm(
            f"A 'Developer' directory exists at {default_developer_path}. Would you like to use it to create your local repo?"
        ).ask()

        if use_developer:
            return handle_subdirectories(default_developer_path)

    # Offer to create the Developer directory if it doesn’t exist
    if not os.path.exists(default_developer_path):
        create_folder = questionary.confirm(
            "A 'Developer' folder does not exist. Would you like to create one? You can house all future projects here."
        ).ask()

        if create_folder:
            create_directory(default_developer_path)
            return default_developer_path

    # Fallback to detecting subdirectories in the home directory
    spinner.info("Falling back to detecting subdirectories in the home directory...")
    return handle_subdirectories(home_directory)


# def locate_local_repo(repo_name):
#     """
#     Locate a local repository based on the name of the remote GitHub repository.

#     :param repo_name: Name of the remote GitHub repository to find locally.
#     :return: Path to the local repository if found, otherwise None.
#     """
#     home_directory = os.path.expanduser("~")
#     search_paths = [os.path.join(home_directory, "Developer"), home_directory]  # Add prioritized search paths

#     spinner.start(f"Searching for local repository matching '{repo_name}'...")

#     for base_path in search_paths:
#         for root, dirs, _ in os.walk(base_path):  # Traverse directories recursively
#             if repo_name in dirs:  # If a directory matches the repo name
#                 repo_path = os.path.join(root, repo_name)
#                 spinner.succeed(f"Found local repository: {repo_path}")
#                 return repo_path

#     spinner.fail(f"No local repository found matching '{repo_name}'.")
#     return None


# search_paths, using_default_path params not in use see: config.py cache_search_paths notes
def locate_local_repo(
    repo_name,
    search_paths=None,
    using_default_paths=False,
    max_displayed_paths=10,
):
    """
    Locate a local repository based on the name of the remote GitHub repository.

    :param repo_name: Name of the remote GitHub repository to find locally.
    :param search_paths: A list of prioritized paths to search for the repository.
    :param using_default_paths: Boolean indicating if the user is using default search paths.
    :return: Path to the local repository if found, otherwise None.
    """
    if not search_paths:
        home_directory = os.path.expanduser("~")
        search_paths = [
            os.path.join(
                home_directory,
                "/Users/dj/Developer/dj-labs/engineering/packages/apollo-o1",
            ),
            home_directory,
        ]  # Default paths

    spinner.start(f"Searching for local repository matching '{repo_name}'...")

    searched_paths = []  # Keep track of paths that were searched

    for base_path in search_paths:
        for root, dirs, _ in os.walk(base_path):  # Traverse directories recursively
            searched_paths.append(root)  # Log the path being searched

            if repo_name in dirs:  # If a directory matches the repo name
                repo_path = os.path.join(root, repo_name)
                spinner.succeed(f"Found local repository: {repo_path}")
                return repo_path

    # Log the paths that were searched if no repository is found
    spinner.fail(f"No local repository found matching '{repo_name}'.")
    print(f"\nPaths searched (max displayed paths = {max_displayed_paths}):")

    # Limit the number of paths displayed
    displayed_paths = searched_paths[:max_displayed_paths]

    for path in displayed_paths:
        print(f"  - {path}")

    # Indicate if some paths were not displayed
    if len(searched_paths) > max_displayed_paths:
        print(
            f"\n...and {len(searched_paths) - max_displayed_paths} more paths not displayed."
        )

    return None
