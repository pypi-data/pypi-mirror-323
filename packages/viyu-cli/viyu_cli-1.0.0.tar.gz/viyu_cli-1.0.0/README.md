
## How the Commands Work

### 1. `viyu create_project <project_name>`

- The `create_project` command accepts the name of the project to be created.
- The system ensures that the project name is a valid Python identifier and checks if a project with the same name already exists.
- Once the name is validated, the command creates the project directory and initializes basic files and folders necessary for a server project.

### 2. `viyu add_app <app_name>`

- The `add_app` command creates a new app within the existing project by adding a directory with the app name and initializing necessary files such as `models.py`, `views.py`, etc.
- The app is added under the `apps/` directory of the project, and the tool ensures that no duplicate apps are created.

## Development

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/viyu-cli.git
    cd viyu-cli
    ```

2. Install the dependencies:
    ```bash
    pip install -e .
    ```

3. You can now use the `viyu` command in your terminal to create projects and apps!

## Contributing

Feel free to submit issues and pull requests to improve the tool.
