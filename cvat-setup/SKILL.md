---
name: cvat-setup
description: Detailed workflow for installing Intel CVAT on WSL2 (Ubuntu 24.04) with GPU acceleration and Nuclio (serverless) AI auto-labeling support.
---

# CVAT Setup for WSL2 with GPU Acceleration

This skill provides a proven workflow for setting up Intel CVAT (Computer Vision Annotation Tool) on WSL2 (Ubuntu 24.04) with full NVIDIA GPU support and Nuclio serverless function for AI-assisted labeling.

## 1. Prerequisites (Host & WSL2)

Before proceeding, ensure the following are installed and working:
- **Windows**: Latest NVIDIA Driver (Game Ready or Studio).
- **WSL2**: Ubuntu 24.04.
- **Docker Engine**: Installed directly in Ubuntu (not Docker Desktop).

Verify host GPU access:
```bash
nvidia-smi
```

## 2. NVIDIA Container Toolkit Setup

Docker must be configured to use the NVIDIA runtime by default.

1. **Install Toolkit**:
   ```bash
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   ```

2. **Configure Docker Daemon**:
   Edit `/etc/docker/daemon.json` to include:
   ```json
   {
       "default-runtime": "nvidia",
       "runtimes": {
           "nvidia": {
               "path": "nvidia-container-runtime",
               "args": []
           }
       }
   }
   ```
   *Note: Using `"default-runtime": "nvidia"` is critical for Docker Compose to reliably detect the GPU.*

3. **Restart Docker**:
   ```bash
   sudo systemctl restart docker
   ```

## 3. CVAT Configuration (GPU + Serverless)

To enable GPU in CVAT and Nuclio, create a `gpu.yml` file in the CVAT root directory.

### Create `gpu.yml`:
```yaml
services:
  cvat_server:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,video
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu, utility]

  cvat_worker_annotation:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,video
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu, utility]

  nuclio:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,video
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu, utility]
```

## 4. Launching CVAT

Run CVAT with the combined configuration files:
```bash
docker compose \
  -f docker-compose.yml \
  -f components/serverless/docker-compose.serverless.yml \
  -f gpu.yml \
  up -d
```

## 5. Verification

Check if NVIDIA libraries are correctly loaded inside the worker container:
```bash
docker exec -it cvat_worker_annotation ldconfig -p | grep nvidia
```
*Expected output: Success if `libnvidia-ml.so.1` or similar libraries are listed.*

## 6. Accessing CVAT

- **Web UI**: `http://localhost:8080`
- **Nuclio Dashboard**: `http://localhost:8070`
- **First Time**: Create a superuser:
  ```bash
  docker exec -it cvat_server python3 manage.py createsuperuser
  ```
