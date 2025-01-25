# Create Lilypad Module

Create Lilypad modules.

- [Build a Job Module](https://docs.lilypad.tech/lilypad/developer-resources/build-a-job-module) – How to build a Lilypad job module
- [JS CLI Wrapper](https://docs.lilypad.tech/lilypad/developer-resources/js-cli-wrapper-local) – How to run the Lilypad CLI wrapper locally

Create Lilypad Module works on macOS, Windows, and Linux.

If something doesn’t work, please [file an issue](https://github.com/DevlinRocha/create-lilypad-module/issues/new).

If you have questions or need help, please ask in [GitHub Discussions](https://github.com/DevlinRocha/create-lilypad-module/discussions).

## Quick Overview

To create a new Lilypad module, install our CLI tool:

```sh
pip install create-lilypad-module
```

If you've previously installed `create-lilypad-module`, you should to ensure that you're using the latest version:

```sh
pip install --upgrade create-lilypad-module
```

Now run `create-lilypad-module`:

```sh
create-lilypad-module
```

The CLI will ask for the name of your project and your GitHub username. Alternatively, you can run:

```sh
create-lilypad-module project_name github_username
cd project_name
```

Output:

```
project_name
├── .gitignore
├── constants.py
├── download_model.py
├── lilypad_module.json.tmpl
├── README.md
├── run_inference.py
└── run.py
```
