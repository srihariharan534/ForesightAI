# 08. Deployment Guide

## Introduction
ForesightAI is containerized for consistent deployment across environments.

## Purpose
To provide instructions for deploying the system locally and to production.

## Detailed Explanation
**Local Deployment (Docker Compose):**
1. Copy `.env.example` to `.env`.
2. Run `docker-compose up --build`.
3. Access API at `http://localhost:8000/docs`.

**Production Deployment:**
1. Provision a PostgreSQL RDS instance.
2. Build the Docker image: `docker build -t foresightai .`
3. Push to ECR/DockerHub.
4. Deploy to Kubernetes using Helm or AWS ECS.
5. Ensure `ENVIRONMENT=production` is set.

## Diagrams
*(See `architecture/Deployment_Diagram.md`)*

## Tables
| Environment | Database | MLflow Backend |
|-------------|----------|----------------|
| Local | PostgreSQL (Docker) | SQLite |
| Production | AWS RDS | AWS RDS + S3 |

## Examples
- Generating a production build: `make build`

## Best Practices
- Never commit the `.env` file or secrets.
- Use a reverse proxy (NGINX/Traefik) for SSL termination in production.

## Future Improvements
- Terraform scripts for automated AWS/GCP infrastructure provisioning.
