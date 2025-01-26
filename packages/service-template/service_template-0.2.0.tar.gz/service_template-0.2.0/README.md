# **Service Template Project**

## A Python-based service template designed to streamline the creation of scalable, well-structured microservices. This project provides a robust starting point for building RESTful APIs, complete with best practices for code organization, logging, dependency management, and more.

## **Features**

- 📂 **Clean Architecture**: Predefined folder structure for easy scalability and maintainability.
- ⚙️ **Customizable CLI**: Includes a CLI for generating services with click and rich formatting.
- 🔧 **Built-in Tools**:
  - FastAPI for API development.
  - SQLModel for database interactions.
  - Uvicorn for fast and efficient server hosting.
- 📜 **Logging**: Centralized and configurable logging system.
- 🧪 **Pre-configured Testing**: Pytest setup with sample tests.
- 🐳 **Dockerized**: Ready-to-use `Dockerfile` for containerized deployments.
- 🛠️ **CI/CD Ready**: Includes a `Makefile` and GitHub pre-commit hooks for formatting and linting (`isort`, `black`, `mypy`, `flake8`).
- 📖 **Configuration**: Environment management via `.env` files.

---

## **Getting Started**

### **Prerequisites**

1. Python 3.10+ installed.

---

### **Installation**

1. Install the package:

   ```bash
   python -m pip install service-template
   ```

---

### **Running the template**

1. Create and enter your project directory:

   ```bash
   mkdir new-project
   cd new-project
   ```

2. Create your project directory:

   ```bash
   service-template init
   ```

---

## **Contributing**

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

---
