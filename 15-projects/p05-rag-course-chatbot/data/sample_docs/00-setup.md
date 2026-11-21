# Module 00 - Setup

## Virtual environments
A **virtual environment** (venv) is a private folder of Python packages for one project. It stops two projects that need different versions of the same package from breaking each other. Create one with `python -m venv .venv`, then activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\activate` on Windows. Install packages inside it with `pip install -r requirements.txt`.

## requirements.txt
A `requirements.txt` file lists the packages a project needs. Pin each one with `==` (for example `pandas==2.2.2`) so everyone installs exactly the same version and the code behaves the same on every machine.

## API keys and .env files
An **API key** is a secret password that lets your code use a paid online service such as Claude or OpenAI. Never write a key inside your code or commit it to Git. Put it in a `.env` file, add `.env` to `.gitignore`, and load it with the `python-dotenv` package. Share a `.env.example` file with placeholder values instead.

## Colab vs Jupyter vs VS Code
Use **Google Colab** when you need a free GPU or want zero installation. Use **Jupyter** on your laptop for exploring data step by step. Use **VS Code** when you are building a real project with several files, tests and Git.
