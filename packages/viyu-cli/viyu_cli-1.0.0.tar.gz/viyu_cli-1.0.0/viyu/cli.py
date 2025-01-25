import os
import sys
from viyu.commands.create_server import create_server
from viyu.commands.add_app import add_app


def display_welcome_message():
    """Display the welcome message and available commands."""
    print("\n✨ Welcome to Viyu CLI! ✨")
    print("We’re thrilled to have you here! Viyu is your personal framework to simplify server and app creation.\n")
    print("Here’s how you can use Viyu CLI:")
    print("1️⃣ `viyu new <project_name>`   : Create a new server project.")
    print("2️⃣ `viyu add <app_name>`       : Add a new app to an existing project.")
    print("\n📖 Documentation: https://viyu-docs.example.com")
    print("🚀 Let’s get started! 🚀\n")


def display_help():
    """Display help message with available commands."""
    print("\n✨ Viyu CLI Help ✨")
    print("Here’s how you can use Viyu CLI:")
    print("1️⃣ `viyu new <project_name>`   : Create a new server project.")
    print("2️⃣ `viyu add <app_name>`       : Add a new app to an existing project.")
    print("\n📖 Documentation: https://viyu-docs.example.com")
    print("🚀 Let’s get started! 🚀\n")


def create_project(project_name):
    """Handle the creation of a new project."""
    try:
        create_server(project_name)
        print(f"✅ Project `{project_name}` created successfully!")
        print(f"📂 Navigate to your project folder:\n   cd {project_name}")
        print("🛠️ Create your first app using:\n   viyu add <app_name>")
    except Exception as e:
        print(f"❌ Failed to create project `{project_name}`. Error: {str(e)}")

def add_application(app_name):
    """Handle the addition of a new app to the current project."""
    try:
        current_directory = os.getcwd()

        # Validate if we're inside a Viyu project by checking for required directories
        project_folder_structure = ["apps", "config", "templates", "static", "logs", "README.md", "requirements.txt"]
        if not all(os.path.isdir(os.path.join(current_directory, folder)) for folder in project_folder_structure[:-2]) or not os.path.isfile(os.path.join(current_directory, project_folder_structure[-2])):
            print("❌ You are not inside a valid Viyu project directory.")
            print("➡️ Please navigate to a project folder or create a new project using:")
            print("   viyu new <project_name>")
            return

        # Ensure the 'apps' directory exists
        apps_folder = os.path.join(current_directory, "apps")
        if not os.path.exists(apps_folder):
            os.makedirs(apps_folder)
            print(f"✅ Created 'apps' directory at: {apps_folder}")

        # Path for the new app folder
        app_folder = os.path.join(apps_folder, app_name)

        # Prevent overwriting existing app
        if os.path.exists(app_folder):
            print(f"❌ The app `{app_name}` already exists in the 'apps' directory.")
            return

        # Create the app folder and invoke the `add_app` function
        os.makedirs(app_folder)
        add_app(app_name, app_folder)
        print(f"✅ App `{app_name}` created successfully inside the 'apps' directory!")
    
    except Exception as e:
        print(f"❌ Failed to create app `{app_name}`. Error: {str(e)}")


def main():
    try:
        # Check if '--help' is provided
        if len(sys.argv) == 2 and sys.argv[1] in ["--help", "help"]:
            display_help()
            return

        # Display the welcome message if no arguments are provided
        if len(sys.argv) == 1:
            display_welcome_message()
            return

        # Handle CLI commands
        command = sys.argv[1]

        if command == "new":
            if len(sys.argv) != 3:
                print("❌ Usage: viyu new <project_name>")
                return
            project_name = sys.argv[2]
            create_project(project_name)

        elif command == "add":
            if len(sys.argv) != 3:
                print("❌ Usage: viyu add <app_name>")
                return
            app_name = sys.argv[2]
            add_application(app_name)

        else:
            print(f"❌ Unknown command `{command}`.")
            display_welcome_message()

    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")

    finally:
        print("\n✨ Thank you for using Viyu! ✨")
        print("Happy coding! 🚀")


if __name__ == "__main__":
    main()
