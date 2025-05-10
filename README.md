### !!! Early Development Stage !!! ###
# DockerBuilder 🐋

DockerBuilder is an intelligent project containerization assistant that automatically analyzes your projects and generates optimized Docker configurations. It helps developers quickly containerize their applications without manual Dockerfile creation.

## 👨‍💻 Developer

This project is developed and maintained by [FOUNDATION-AI-BASED](https://github.com/FOUNDATION-AI-BASED), a developer focused on simplifying tools with modern UIs.

## 🌟 Features

- **Smart Project Analysis**: Automatically detects project type, dependencies, and requirements
- **Intelligent Path Detection**: Automatically finds the correct project root directory
- **Docker Configuration Generation**: Creates optimized Dockerfile and docker-compose.yml files
- **Multiple Output Formats**: Export configurations as ZIP or TAR archives
- **Web Interface**: User-friendly web UI for easy project upload and configuration
- **Customizable**: Fine-tune generated configurations to match your needs
- **Language Support**: Supports multiple programming languages and frameworks
- **macOS Compatibility**: Automatically removes _MACOS folders from uploaded projects

## 🧪 Tested Project Types

## ⚠️ Untested Project Types

### Python
- ❌ Pyramid
- ❌ Tornado
- ❌ Sanic
- ❌ Complex Django applications with custom middleware
- ❌ Projects with multiple Python versions
- ❌ Django
- ❌ Flask
- ❌ FastAPI


### Node.js
- ❌ NestJS
- ❌ Nuxt.js
- ❌ Vue.js with custom configurations
- ❌ Complex monorepo structures
- ❌ Projects with multiple Node.js versions
- ❌ Express.js
- ❌ React
- ❌ Next.js

### Other Languages
- ❌ Java Spring Boot
- ❌ Ruby on Rails
- ❌ PHP Laravel
- ❌ Go applications
- ❌ Rust applications

### Complex Scenarios
- ❌ Microservices architectures
- ❌ Multi-container applications
- ❌ Projects with custom build processes
- ❌ Projects requiring specific system dependencies
- ❌ Projects with complex environment configurations

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/docker-builder.git
cd docker-builder
```

2. Start the application using Docker:
```bash
docker-compose up -d
```

3. Access the web interface at `http://localhost:3000`

## 🛠️ Usage

1. Upload your project through the web interface
2. Wait for the analysis to complete
3. Review the generated Docker configurations
4. Download the configuration package
5. Use the generated files to build and run your containerized application

## 🔧 Requirements

- Docker
- Docker Compose
- Python 3.8+
- Node.js 14+

## 📦 Installation

### Using Docker (Recommended)

```bash
docker-compose up -d
```

### Manual Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Start the application:
```bash
python app.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Docker for the amazing containerization platform
- All contributors who have helped improve this project 
