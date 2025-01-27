import subprocess
from pathlib import Path

def build_docker_image(project_dir: Path, tag: str = "latest", port: int = 8000) -> None:
    """
    Build a Docker image for the Python application.
    
    Args:
        project_dir: Path to the project root directory
        tag: Docker image tag
        port: Port to expose for the REST API
    """
    dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir -e .

EXPOSE {port}

CMD ["python", "-m", "aibaba_ai_cli", "serve", "--port", "{port}"]
"""
    
    dockerfile_path = project_dir / "Dockerfile"
    dockerfile_path.write_text(dockerfile_content)

    image_name = f"aibaba-ai-app:{tag}"
    
    try:
        subprocess.run(
            ["docker", "build", "-t", image_name, str(project_dir)],
            check=True,
        )
        print(f"\nDocker image built successfully: {image_name}")
        print(f"To run the container: docker run -p {port}:{port} {image_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image: {e}")
    finally:
        dockerfile_path.unlink(missing_ok=True)  # Clean up the temporary Dockerfile 