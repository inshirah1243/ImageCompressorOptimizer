# Image Compressor & Optimizer

A beginner-friendly Flask web application that compresses JPG, JPEG, and PNG images with Pillow. It shows the original and compressed file sizes, the percentage change, and provides a download button.

## Features

- Upload JPG, JPEG, or PNG images (up to 16 MB)
- Choose a quality value from 1 to 100
- View original size, compressed size, and percentage reduction
- Download the optimized image
- Docker configuration on port `5000`
- Kubernetes configuration with 2 replicas and NodePort `30088`
- Jenkins pipeline template for build, push, and Kubernetes deployment

## Run locally with Python

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the application:

   ```powershell
   python app.py
   ```

4. Open `http://localhost:5000`, choose an image, set a quality value, and click **Compress Image**.

## Run with Docker

Build and start the container:

```powershell
docker build -t image-compressor-optimizer .
docker run --rm -p 5000:5000 image-compressor-optimizer
```

Then open `http://localhost:5000`.

## Kubernetes and Jenkins setup

Before deploying manually, replace `DOCKERHUB_USERNAME` in `deployment.yaml` with your Docker Hub username.

For Jenkins, replace the `DOCKERHUB_USERNAME` value in `Jenkinsfile` and add these credentials in Jenkins:

- `docker-hub-credentials`: a Username with password credential for Docker Hub.
- `kubeconfig-file`: a Secret file credential containing your Kubernetes kubeconfig.

The Jenkins agent needs Docker and `kubectl` installed and permission to access the Kubernetes cluster. The pipeline builds an image, pushes it with the Jenkins build number and `latest` tags, then applies the Kubernetes files. The application is exposed as a NodePort service on port `30088`.

## Note about quality

For JPEG files, quality is passed directly to Pillow. PNG is lossless, so the selected value is mapped to PNG compression level; the visual image is not degraded, and the size change may be modest.
