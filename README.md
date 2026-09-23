# Retail Platform

## Application

Retail platform application used for enterprise release, hotfix, deployment, and rollback practice.

## Current Version

4.2.0

## Application Port

8081

## Endpoints

- `/` - Application information
- `/health` - Application health status
- `/payment` - Payment processing status
- `/version` - Application version and environment information

## Docker

Build the application image:

```bash
docker build -t retail-app:4.2.0 .