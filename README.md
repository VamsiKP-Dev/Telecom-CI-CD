# Telecom CI‑CD — Customer & Billing Microservices

**Human-friendly README** — clear, step‑by‑step instructions so anyone can run, test, debug, and CI/CD this small Dockerized project.

---

## Project overview

This repository contains two tiny Flask microservices that demonstrate a simple CI/CD workflow using **Docker Compose** and **Jenkins**:

* **Customer Service** (port `5000`) — returns customer data.
* **Billing Service** (port `5001`) — calls the Customer Service to compute a bill.

They are deliberately minimal so you can focus on the integration, Dockerization, and CI pipeline.

---

## What you will learn

* How to run multiple services with Docker Compose.
* How services communicate inside a Docker network using service names.
* How to hook this into a Jenkins pipeline that builds, starts, tests, and tears down the system.

---

## Prerequisites

Make sure you have the following installed and working on the machine where you run the project:

1. **Docker Desktop** (Windows / macOS) or **Docker Engine** (Linux).
2. **Docker Compose** (v2 recommended). On Docker Desktop, `docker compose` / `docker-compose` is available.
3. **curl** or any HTTP client (Postman / Browser) for testing endpoints.
4. (Optional) **Jenkins** server if you want to run the pipeline.

> Windows special note: If you plan to run Jenkins as a Windows service and have Jenkins execute Docker commands, run the Jenkins service under a **real Windows user account** (not LocalSystem) that can access Docker Desktop. See the "Jenkins integration" section.

---

## Repository structure

```
Telecom_CI-CD/
├─ customer_service/
│  ├─ app.py                # Flask app for Customer Service
│  ├─ requirements.txt
│  └─ Dockerfile
├─ billing_service/
│  ├─ app.py                # Flask app for Billing Service (calls customer-service)
│  ├─ requirements.txt
│  └─ Dockerfile
├─ docker-compose.yml
```

> The important thing is the two service directories and the compose file at the repo root (or the subfolder path if your repo uses one).

---

## Important design details

* Services talk to one another using the **Docker Compose service name** as the hostname, e.g. `http://customer-service:5000/customers/1`.
* Use the plural route `/customers/<id>` in both places so the Billing Service and Customer Service agree on the path.
* Each Flask app binds to `0.0.0.0` so the container exposes the port to the host.

---

## How to run locally (fastest)

1. Open a terminal and change into the project directory where `docker-compose.yml` lives. Example:

```bash
cd "C:\Users\Dell\Desktop\DevOps\Coder-Range\Jenkins + Docker\Devops-Liveproject-main\Telecom_CI-CD"
```

2. Start the services (builds the images if needed):

```bash
# build then start (detached)
docker-compose up -d --build
```

3. Confirm containers are running:

```bash
docker ps
```

You should see two containers similar to:

```
telecom_ci-cd-customer-service-1   Up (0.0.0.0:5000->5000)
telecom_ci-cd-billing-service-1    Up (0.0.0.0:5001->5001)
```

4. Test endpoints (use curl or a browser):

**Customer service**

```bash
curl http://localhost:5000/customers/1
# Expected JSON:
# {"name":"Alice","status":"active"}
```

**Billing service**

```bash
curl http://localhost:5001/bill/1
# Expected JSON:
# {"customer":"Alice","status":"active","bill_amount":100}
```

5. Stop and remove containers (cleanup):

```bash
docker-compose down
```

---

## How the services communicate (why your code was failing earlier)

* Inside a Docker Compose network, `localhost` refers to *the container itself*, not other containers. To call another service, use its **service name** from `docker-compose.yml`, e.g. `customer-service`.

* Example (correct):

```python
CUSTOMER_SERVICE_URL = "http://customer-service:5000/customers"
```

* Also ensure the **path** matches the route your Customer Service exposes (`/customers/<id>`).

---

## Jenkins pipeline (example)

This repo includes a Declarative `Jenkinsfile` that does the following steps:

1. Checkout the repo.
2. Build images and start services with Docker Compose.
3. Wait briefly, then test both services using `curl`.
4. Tear down the environment in the `post` section.

**Important Jenkins notes (Windows agents):**

* Jenkins must be able to talk to Docker. If you run Jenkins as a Windows Service under `LocalSystem`, it **cannot** access Docker Desktop's named pipe. Change the Jenkins service to run under a real Windows user account.
* Replace any `timeout /t` commands with a non-interactive wait such as `ping 127.0.0.1 -n 6 >nul` in `bat` blocks.

**Example snippet (inside `dir('Telecom_CI-CD')` on Windows agent):**

```groovy
bat '''
    docker-compose down || exit 0
    docker-compose build
    docker-compose up -d
'''

bat '''
    ping 127.0.0.1 -n 6 >nul
    curl -f http://localhost:5000/customers/1
'''
```

> If your `docker-compose.yml` is in a subfolder of the repo, use `dir('<subfolder>')` in Jenkins to change to that folder before running compose commands.

---

## Troubleshooting checklist

If something fails, follow this checklist in order:

1. **Are containers running?**

   * `docker ps` — check the two service containers are `Up`.
2. **Are ports bound to localhost?**

   * `docker ps` shows `0.0.0.0:5000->5000` and `0.0.0.0:5001->5001`.
3. **Does Customer Service respond?**

   * `curl http://localhost:5000/customers/1` → should return JSON. If 404, make sure path is `/customers/1`.
4. **Does Billing Service make the request to the right hostname/path?**

   * Inside `billing_service/app.py`, ensure `CUSTOMER_SERVICE_URL = "http://customer-service:5000/customers"` (service name must match compose).
5. **Check logs**

   * `docker logs <container-name>` — copy and review the stack trace.
6. **If using Jenkins on Windows**

   * Make Jenkins service run under your Windows user account (Services → Jenkins → Log On tab).
7. **Compose file location**

   * If `docker-compose.yml` sits in a subfolder of your repository, Jenkins must `dir()` into that folder before running `docker-compose`.

---

## Common fixes (copy/paste)

**Rebuild & restart**

```bash
docker-compose down
docker-compose up -d --build
```

**View logs for billing service**

```bash
# list containers for exact name
docker ps
# then
docker logs <billing-container-name>
```

**Fix billing service to use service name (edit file)**

```python
# billing_service/app.py
CUSTOMER_SERVICE_URL = "http://customer-service:5000/customers"
```

---

## Adding a `/health` endpoint (recommended)

A simple health endpoint helps Jenkins or other orchestrators confirm a service is healthy.

Add to each Flask app:

```python
@app.route('/health')
def health():
    return jsonify({"status":"ok"}), 200
```

Then Jenkins can poll `http://localhost:5000/health` and `http://localhost:5001/health` to ensure readiness.

---

## What to commit to Git

* `customer_service/` directory (app.py, requirements.txt, Dockerfile)
* `billing_service/` directory (app.py, requirements.txt, Dockerfile)
* `docker-compose.yml`
* `README.md` (this file!)

---

## Example `docker-compose.yml` (simple)

```yaml
services:
  customer-service:
    build: ./customer_service
    container_name: customer-service
    ports:
      - "5000:5000"

  billing-service:
    build: ./billing_service
    container_name: billing-service
    ports:
      - "5001:5001"
    depends_on:
      - customer-service
```

---

## FAQs

**Q: Why does `localhost` work from my browser but not from inside the container?**
A: From your host machine (the browser), `localhost:5000` is the host-bound port from Docker and routes to the container. From inside a container, `localhost` refers to *that container*, not the host or other containers.

**Q: I changed code — why doesn’t the new code show up?**
A: You must rebuild the image: `docker-compose up -d --build` or run `docker-compose build` then `docker-compose up -d`.

**Q: Why do container names look different from Jenkins logs?**
A: Docker Compose names containers based on the project name and service name. If your project directory or `COMPOSE_PROJECT_NAME` changes, the final container name will change as well.

---

## Final notes

This project is a tiny but practical example of multi‑service Docker development and simple CI/CD. It’s deliberately simple so you can extend any part (add databases, auth, tests, or Kubernetes deployment) as your next step.

---
