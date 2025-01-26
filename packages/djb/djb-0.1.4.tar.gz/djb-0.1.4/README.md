# Welcome to djb!

<a href="https://github.com/djb-sh/djb">
  <img src="./docs/djb.svg" alt="djb mascot" width="300px" align="right">
</a>

**djb** combines a [Django](https://www.djangoproject.com/) ASGI server with a [Vite](https://vite.dev/)+[Vue](https://vuejs.org/) frontend server running on the [Bun](https://bun.sh/) JavaScript runtime. Here's how it  works:

* **Django** prepares data and requests HTML pages from the frontend server via [gRPC](https://grpc.io/).  
* **Frontend Server** renders and returns HTML, and prepares a JS bundle.
* **Browser** uses the JS bundle to make the page interactive.

When your project is ready to share, djb also provides tools for  deployment, making production as familiar and easy as local development.

## Create a djb Project
Quickly create a new djb project with a single command:
```bash
source <(curl -LsSf https://create.djb.sh)
```

## Create a djb Project (Step-by-Step)
Prefer a manual setup? Follow these steps to create a djb project— equivalent to the one-liner above.

Install `djb` using `pipx`:
```bash
pipx install djb
```

Create a new project:
```bash
djb create
```

Navigate to your project directory.
```bash
cd project_dir
```

Set up your development environment and dependencies.
```bash
djb up && source .djbrc
```

## Optionally Install djb in Editable Mode
Need to modify djb for your project or contribute improvements? Install djb in editable mode:
```bash
djb install editable-djb [--djb-repo-url TEXT]
```

- **Default Behavior**: Clones the official djb repository and installs it in editable mode.
- **Custom Repository**: Use `--djb-repo-url` to specify an alternative repository, such as your fork.

## Acknowledgements
This project builds on the capabilities of many open-source tools and platforms, including Django, Vite, Vue, Bun, Kubernetes, PostgreSQL, and more. Trademarks mentioned here belong to their respective owners.

## Disclaimer
djb is an independent project and is not affiliated with or endorsed by Django Software Foundation, Vite, Kubernetes, Bun, or any other organizations mentioned.

## License
djb is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Mascot Attribution
The djb mascot (dj_bun) was created for this project and is distributed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en).

<br>

---
/**dj_bun**: playin' dev and deploy since 1984 🎶
