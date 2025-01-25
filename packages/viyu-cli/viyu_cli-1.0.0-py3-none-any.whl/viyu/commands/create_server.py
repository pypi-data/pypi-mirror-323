import os
import shutil
import subprocess

def create_server(project_name):
    """
    Creates a server project structure for a custom framework.
    
    :param project_name: Name of the server project to be created.
    """
    try:
        # Step 1: Validate the project name
        validate_project_name(project_name)

        # Step 2: Check if the project directory already exists
        if os.path.exists(project_name):
            print(f"❌ Error: `{project_name}` already exists.")
            return

        # Step 3: Proceed with project creation
        print(f"Creating server project: `{project_name}`...")

        # Define the directory structure for the new project
        structure = {
            project_name: {
                "__init__.py": "# Initialize the server project",
                "main.py": "# Entry point for your custom framework server",
                "apps": {
                    "__init__.py": "# Initialize the apps module",
                },
                "config": {
                    "__init__.py": "# Initialize the configuration module",
                    "settings.py": "# Define your global project settings here",
                    "routes.py": "# Define your app routes here",
                },
                "templates": {},  # For HTML or other templates
                "static": {},     # For static files like CSS, JS, images
                "logs": {},       # Directory to store log files
                "README.md": f"# {project_name.capitalize()}\n\nWelcome to the `{project_name}` server project.",
                "requirements.txt": "# Add your project dependencies here\n# Example:\n# my-custom-framework>=1.0.0",
            }
        }

        # Step 4: Recursively create the directory structure
        create_structure(".", structure)

        # If successful, print the success messages
        print(f"✅ Project `{project_name}` created successfully!")
        print(f"📂 Navigate to your project folder: `cd {project_name}`")
        print(f"🛠️ Create your first app using: `viyu add <app_name>`")
    
    except ValueError as ve:
        # Handle invalid project name error
        print(f"❌ {ve}")  # Display specific error message for invalid project name
        rollback_creation(project_name)  # Rollback on failure
    except Exception as e:
        # Handle any other unexpected errors
        print(f"❌ Failed to create server project: {str(e)}")  # Display general error message
        rollback_creation(project_name)  # Rollback on failure
    else:
        # If no error occurred, we return (no rollback needed)
        return


def validate_project_name(project_name):
    """
    Validates the project name to ensure it meets the naming conventions.
    :param project_name: The name of the project to validate.
    :raises ValueError: If the project name is invalid.
    """
    if not project_name.isidentifier():
        raise ValueError(f"❌ Invalid project name: `{project_name}`. "
                         "Project names must be valid Python identifiers. "
                         "Project names should only contain letters, numbers, and underscores, and cannot start with a number.")
    print(f"Project name `{project_name}` is valid.")

def create_structure(base_path, structure):
    """
    Recursively creates directories and files as per the defined structure.
    :param base_path: The base path where the project should be created.
    :param structure: A dictionary defining the file/folder structure to create.
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        try:
            # Check if the folder or file already exists before attempting to create it
            if os.path.exists(path):
                print(f"❌ Error: `{path}` already exists.")
                rollback_creation(base_path)  # Rollback if the folder or file exists
                return  # Stop the creation process if folder or file exists

            if isinstance(content, dict):  # If content is a dictionary, it represents a directory
                try:
                    os.makedirs(path, exist_ok=True)  # Create the directory (if it doesn't exist)
                except PermissionError:
                    print(f"❌ Permission error: Unable to create directory `{path}` due to insufficient permissions. Trying with sudo.")
                    run_with_sudo(path)  # Attempt with sudo
                    continue  # Skip creation if permission error occurs

                create_structure(path, content)  # Recursively create subdirectories and files
            else:  # If content is a string, it represents a file with content
                try:
                    with open(path, "w") as f:
                        f.write(content)
                except PermissionError:
                    print(f"❌ Permission error: Unable to create file `{path}` due to insufficient permissions. Trying with sudo.")
                    run_with_sudo(path)  # Attempt with sudo
                    continue  # Skip file creation if permission error occurs
        
        except Exception as e:
            print(f"❌ Error creating `{path}`: {e}")
        
        finally:
            print(f"Attempted to create: `{path}`")

def run_with_sudo(path):
    """
    Attempts to create the file or directory with sudo if permission issues occur.
    :param path: The path of the file or directory to create.
    """
    try:
        subprocess.run(['sudo', 'mkdir', '-p', path], check=True)  # Try creating directory with sudo
        print(f"✅ Created `{path}` with sudo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error with sudo: {str(e)}")

def rollback_creation(project_name):
    """
    Rolls back the creation process by deleting the partially created project directory if an error occurs.
    :param project_name: The name of the project to delete.
    """
    try:
        # Clean up by deleting the partially created project directory
        if os.path.exists(project_name):
            shutil.rmtree(project_name)  # Remove the entire project directory and its contents
            print(f"⚠️ Rollback: Deleted the partially created project `{project_name}`.")
    except Exception as e:
        # If the rollback fails, show an error message
        print(f"❌ Rollback failed: {str(e)}")
