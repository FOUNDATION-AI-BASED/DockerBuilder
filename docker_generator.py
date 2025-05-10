import os
import yaml
from typing import Dict, List, Any

class DockerGenerator:
    def __init__(self, analysis_result: Dict[str, Any]):
        self.analysis = analysis_result
        self.output_dir = 'output'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate(self, host: str = '0.0.0.0', port: str = '5000') -> List[str]:
        """Generate Docker configurations based on analysis."""
        generated_files = []
        
        # Generate Dockerfile
        dockerfile_path = os.path.join(self.output_dir, 'Dockerfile')
        self._generate_dockerfile(dockerfile_path, host, port)
        generated_files.append(dockerfile_path)
        
        # Generate docker-compose.yml
        compose_path = os.path.join(self.output_dir, 'docker-compose.yml')
        self._generate_compose(compose_path, host, port)
        generated_files.append(compose_path)
        
        # Generate .dockerignore
        dockerignore_path = os.path.join(self.output_dir, '.dockerignore')
        self._generate_dockerignore(dockerignore_path)
        generated_files.append(dockerignore_path)
        
        return generated_files
    
    def _detect_framework(self) -> str:
        """Detect the framework being used in the project."""
        files = [f['path'] for f in self.analysis.get('files', [])]
        dependencies = self.analysis.get('dependencies', [])
        
        # Python frameworks
        if 'requirements.txt' in files:
            if any('django' in dep.lower() for dep in dependencies):
                return 'django'
            elif any('flask' in dep.lower() for dep in dependencies):
                return 'flask'
            elif any('fastapi' in dep.lower() for dep in dependencies):
                return 'fastapi'
        
        # JavaScript/Node.js frameworks
        if 'package.json' in files:
            if any('next' in dep.lower() for dep in dependencies):
                return 'nextjs'
            elif any('react' in dep.lower() for dep in dependencies):
                return 'react'
            elif any('vue' in dep.lower() for dep in dependencies):
                return 'vue'
            elif any('express' in dep.lower() for dep in dependencies):
                return 'express'
        
        return 'unknown'
    
    def _generate_dockerfile(self, output_path: str, host: str, port: str):
        """Generate Dockerfile based on project type and framework."""
        dockerfile_content = []
        project_type = self.analysis.get('type', 'unknown')
        framework = self.analysis.get('framework', 'unknown')
        
        # Common environment variables
        dockerfile_content.extend([
            f'ENV HOST={host}',
            f'ENV PORT={port}',
            f'EXPOSE {port}'
        ])
        
        if project_type == 'python':
            dockerfile_content.extend([
                'FROM python:3.9-slim',
                'WORKDIR /app',
                '',
                '# Install system dependencies',
                'RUN apt-get update && apt-get install -y \\',
                '    libmagic1 \\',
                '    && rm -rf /var/lib/apt/lists/*',
                '',
                '# Copy requirements first to leverage Docker cache',
                'COPY requirements.txt .',
                'RUN pip install --no-cache-dir -r requirements.txt',
                '',
                '# Copy project files',
                'COPY . .',
                '',
                '# Set proper permissions',
                'RUN chown -R nobody:nogroup /app',
                '',
                '# Switch to non-root user',
                'USER nobody',
                '',
                f'ENV HOST={host}',
                f'ENV PORT={port}',
                f'EXPOSE {port}',
                '',
                '# Run the application with the specified port',
                f'CMD ["gunicorn", "--bind", "{host}:{port}", "--workers", "4", "--timeout", "120", "app:app"]'
            ])
        
        elif project_type == 'javascript':
            dockerfile_content.extend([
                'FROM node:16-alpine',
                'WORKDIR /app',
                '',
                '# Install dependencies',
                'COPY package*.json ./',
                'RUN npm install',
                '',
                '# Copy project files',
                'COPY . .',
                '',
                f'ENV HOST={host}',
                f'ENV PORT={port}',
                f'EXPOSE {port}',
            ])
            
            # Framework-specific commands
            if framework == 'nextjs':
                dockerfile_content.extend([
                    'RUN npm run build',
                    f'CMD ["npm", "start", "--", "-p", "{port}"]'
                ])
            elif framework == 'react':
                dockerfile_content.extend([
                    'RUN npm run build',
                    f'CMD ["npm", "start", "--", "-p", "{port}"]'
                ])
            elif framework == 'vue':
                dockerfile_content.extend([
                    'RUN npm run build',
                    f'CMD ["npm", "run", "serve", "--", "--port", "{port}"]'
                ])
            elif framework == 'express':
                dockerfile_content.extend([
                    f'CMD ["node", "app.js", "--port", "{port}"]'
                ])
            else:
                dockerfile_content.append(f'CMD ["npm", "start", "--", "-p", "{port}"]')
        
        else:
            # Generic Dockerfile for unknown project types
            dockerfile_content.extend([
                'FROM ubuntu:latest',
                'WORKDIR /app',
                'COPY . .',
                f'ENV HOST={host}',
                f'ENV PORT={port}',
                f'EXPOSE {port}',
                f'CMD ["echo", "Please customize this Dockerfile for your project"]'
            ])
        
        # Write Dockerfile
        with open(output_path, 'w') as f:
            f.write('\n'.join(dockerfile_content))
    
    def _generate_compose(self, output_path: str, host: str, port: str):
        """Generate docker-compose.yml with proper port mapping."""
        compose_content = [
            'version: \'3.8\'',
            '',
            'services:',
            '  app:',
            '    build: .',
            f'    ports:',
            f'      - "{port}:{port}"',
            '    environment:',
            '      - PYTHONUNBUFFERED=1',
            f'      - PORT={port}',
            f'      - HOST={host}',
            '    volumes:',
            '      - ./uploads:/app/uploads',
            '      - ./output:/app/output',
            '      - ./extracted:/app/extracted',
            '    networks:',
            '      - app-network',
            '',
            'networks:',
            '  app-network:',
            '    driver: bridge'
        ]
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(compose_content))
    
    def _generate_dockerignore(self, output_path: str):
        """Generate .dockerignore file."""
        project_type = self.analysis.get('language', 'unknown')
        framework = self._detect_framework()
        
        ignore_patterns = [
            '.git',
            '.gitignore',
            '.env',
            'node_modules',
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'env',
            'venv',
            '.venv',
            'pip-log.txt',
            'pip-delete-this-directory.txt',
            '.tox',
            '.coverage',
            '.coverage.*',
            '.cache',
            'nosetests.xml',
            'coverage.xml',
            '*.cover',
            '*.log',
            '.pytest_cache',
            '.DS_Store',
            'dist',
            'build',
            '*.egg-info',
            '.idea',
            '.vscode',
            '*.swp',
            '*.swo'
        ]
        
        # Framework-specific patterns
        if framework == 'django':
            ignore_patterns.extend([
                'staticfiles',
                'media',
                '*.sqlite3'
            ])
        elif framework in ['react', 'nextjs', 'vue']:
            ignore_patterns.extend([
                'build',
                'dist',
                '.next',
                'coverage'
            ])
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(ignore_patterns))
    
    def _detect_database_dependencies(self) -> bool:
        """Detect if the project has database dependencies."""
        db_keywords = ['mysql', 'postgres', 'mongodb', 'redis', 'sqlite']
        dependencies = self.analysis['dependencies']
        
        for deps in dependencies.values():
            for dep in deps:
                if any(keyword in dep.lower() for keyword in db_keywords):
                    return True
        return False
    
    def _get_database_service(self) -> Dict[str, Any]:
        """Get database service configuration based on detected dependencies."""
        db_services = {}
        dependencies = self.analysis['dependencies']
        
        for deps in dependencies.values():
            for dep in deps:
                if 'mysql' in dep.lower():
                    db_services['mysql'] = {
                        'image': 'mysql:8.0',
                        'environment': {
                            'MYSQL_ROOT_PASSWORD': 'root',
                            'MYSQL_DATABASE': 'app'
                        },
                        'ports': ['3306:3306']
                    }
                elif 'postgres' in dep.lower():
                    db_services['postgres'] = {
                        'image': 'postgres:13',
                        'environment': {
                            'POSTGRES_PASSWORD': 'postgres',
                            'POSTGRES_DB': 'app'
                        },
                        'ports': ['5432:5432']
                    }
                elif 'mongodb' in dep.lower():
                    db_services['mongodb'] = {
                        'image': 'mongo:latest',
                        'ports': ['27017:27017']
                    }
                elif 'redis' in dep.lower():
                    db_services['redis'] = {
                        'image': 'redis:latest',
                        'ports': ['6379:6379']
                    }
        
        return db_services 
