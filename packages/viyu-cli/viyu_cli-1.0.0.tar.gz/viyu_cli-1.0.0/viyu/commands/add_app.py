import os
import shutil
import subprocess

def add_app(app_name, base_dir="apps"):
    """
    Adds a new app structure within the specified base directory.

    :param app_name: Name of the app to be created.
    :param base_dir: The directory where the app folder will be created (default: 'apps').
    """
    try:
        # Ensure app_name is valid
        if not app_name.isidentifier():
            raise ValueError(f"Invalid app name: `{app_name}`. App names must be valid Python identifiers.")
        
        print(f"Adding new app: {app_name}...")

        # Define the app directory path within the correct base_dir
        app_path = os.path.join(base_dir, app_name)

        # Check if app already exists
        if os.path.exists(app_path):
            raise FileExistsError(f"App `{app_name}` already exists at `{app_path}`.")

        # App structure
        structure = {
            "__init__.py": "",
            "models.py": "# Define your models here",
            "views.py": "# Define your views here",
            "urls.py": "# Define your app routes here",
            "admin.py": "# Register your models for the admin site here",
            "apps.py": f"from django.apps import AppConfig\n\nclass {app_name.capitalize()}Config(AppConfig):\n    name = '{app_name}'",
            "migrations": {
                "__init__.py": ""
            },
            "tests.py": "# Write your app tests here"
        }

        # Function to create the folder structure
        def create_structure(base_path, structure):
            for name, content in structure.items():
                path = os.path.join(base_path, name)
                if isinstance(content, dict):  # Create a directory
                    os.makedirs(path, exist_ok=True)
                    create_structure(path, content)
                else:  # Create a file
                    with open(path, "w") as f:
                        f.write(content)

        # Check if the base directory exists
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"The base directory `{base_dir}` does not exist. Please check the project folder structure.")
        
        # Create the app directory and structure
        create_structure(os.path.join(base_dir), structure)
        print(f"✅ App `{app_name}` added successfully!")

    except Exception as e:
        print(f"❌ Failed to add app `{app_name}`: {str(e)}")
        rollback_creation(app_name, base_dir)

def rollback_creation(app_name, base_dir="apps"):
    """
    Rolls back the creation process by deleting the partially created app directory if an error occurs.
    :param app_name: The name of the app to delete.
    :param base_dir: The base directory where the app is being created (default: 'apps').
    """
    try:
        app_path = os.path.join(base_dir, app_name)
        if os.path.exists(app_path):
            shutil.rmtree(app_path)  # Remove the entire app directory and its contents
            print(f"⚠️ Rollback: Deleted the partially created app `{app_name}`.")
    except Exception as e:
        # If the rollback fails, show an error message
        print(f"❌ Rollback failed: {str(e)}")