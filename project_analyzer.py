import os
import json
import yaml
import magic
from typing import Dict, List, Any

class ProjectAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.mime = magic.Magic(mime=True)
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze the project and return its characteristics."""
        project_type = self._detect_project_type()
        dependencies = self._analyze_dependencies()
        entry_points = self._find_entry_points()
        ports = self._detect_ports()
        
        return {
            'project_type': project_type,
            'dependencies': dependencies,
            'entry_points': entry_points,
            'ports': ports,
            'environment': self._analyze_environment(),
            'build_requirements': self._analyze_build_requirements()
        }
    
    def _detect_project_type(self) -> str:
        """Detect the type of project based on its files."""
        files = os.listdir(self.project_path)
        
        if 'package.json' in files:
            return 'nodejs'
        elif 'requirements.txt' in files:
            return 'python'
        elif 'pom.xml' in files:
            return 'java'
        elif 'Gemfile' in files:
            return 'ruby'
        elif 'composer.json' in files:
            return 'php'
        elif 'go.mod' in files:
            return 'go'
        elif 'Cargo.toml' in files:
            return 'rust'
        else:
            return 'unknown'
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze project dependencies."""
        dependencies = {
            'runtime': [],
            'dev': [],
            'build': []
        }
        
        project_type = self._detect_project_type()
        
        if project_type == 'nodejs':
            self._analyze_nodejs_dependencies(dependencies)
        elif project_type == 'python':
            self._analyze_python_dependencies(dependencies)
        elif project_type == 'java':
            self._analyze_java_dependencies(dependencies)
        
        return dependencies
    
    def _analyze_nodejs_dependencies(self, dependencies: Dict[str, List[str]]):
        """Analyze Node.js project dependencies."""
        package_json_path = os.path.join(self.project_path, 'package.json')
        if os.path.exists(package_json_path):
            with open(package_json_path) as f:
                package_data = json.load(f)
                dependencies['runtime'].extend(package_data.get('dependencies', {}).keys())
                dependencies['dev'].extend(package_data.get('devDependencies', {}).keys())
    
    def _analyze_python_dependencies(self, dependencies: Dict[str, List[str]]):
        """Analyze Python project dependencies."""
        requirements_path = os.path.join(self.project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            with open(requirements_path) as f:
                dependencies['runtime'].extend(
                    line.strip() for line in f
                    if line.strip() and not line.startswith('#')
                )
    
    def _analyze_java_dependencies(self, dependencies: Dict[str, List[str]]):
        """Analyze Java project dependencies."""
        pom_path = os.path.join(self.project_path, 'pom.xml')
        if os.path.exists(pom_path):
            # Basic Maven dependency analysis
            with open(pom_path) as f:
                content = f.read()
                # Simple regex-based dependency extraction
                import re
                deps = re.findall(r'<dependency>.*?<artifactId>(.*?)</artifactId>', content, re.DOTALL)
                dependencies['runtime'].extend(deps)
    
    def _find_entry_points(self) -> List[str]:
        """Find potential entry points for the application."""
        entry_points = []
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(('.js', '.py', '.java', '.rb', '.php')):
                    entry_points.append(os.path.join(root, file))
        
        return entry_points
    
    def _detect_ports(self) -> List[int]:
        """Detect potential ports used by the application."""
        ports = []
        
        # Common port patterns in configuration files
        port_patterns = [
            r'port\s*=\s*(\d+)',
            r'PORT\s*=\s*(\d+)',
            r':(\d+)',
            r'port:\s*(\d+)'
        ]
        
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(('.js', '.py', '.java', '.rb', '.php', '.yml', '.yaml', '.json', '.conf')):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        content = f.read()
                        for pattern in port_patterns:
                            import re
                            matches = re.findall(pattern, content)
                            ports.extend(int(match) for match in matches if match.isdigit())
        
        return list(set(ports))
    
    def _analyze_environment(self) -> Dict[str, str]:
        """Analyze environment variables and configuration."""
        env_vars = {}
        
        # Look for common environment files
        env_files = ['.env', '.env.example', 'config.env']
        for env_file in env_files:
            env_path = os.path.join(self.project_path, env_file)
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            env_vars[key] = value
        
        return env_vars
    
    def _analyze_build_requirements(self) -> Dict[str, Any]:
        """Analyze build requirements and tools needed."""
        build_reqs = {
            'tools': [],
            'commands': [],
            'environment': {}
        }
        
        project_type = self._detect_project_type()
        
        if project_type == 'nodejs':
            build_reqs['tools'].extend(['node', 'npm'])
            build_reqs['commands'].append('npm install')
        elif project_type == 'python':
            build_reqs['tools'].extend(['python', 'pip'])
            build_reqs['commands'].append('pip install -r requirements.txt')
        elif project_type == 'java':
            build_reqs['tools'].extend(['java', 'maven'])
            build_reqs['commands'].append('mvn clean install')
        
        return build_reqs 
