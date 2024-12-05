# Signal Bot with ATAK Integration 

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

A Signal bot that sends geolocation and target information (CoT) to an ATAK (Android Team Awareness Kit) client. Dockerized and ready to be operational in minutes. Built with Docker, Docker Compose, Python, [Confluent Kafka](https://github.com/confluentinc/confluent-kafka-python), and [Signal CLI REST API](https://github.com/bbernhard/signal-cli-rest-api).
## High-Level Architecture

The project uses a **Pub/Sub pattern** and **microservice architecture**. It comprises five services:

- **`signal-rest-api`**: Provides REST endpoints to consume messages from Signal.
- **`signal-listener-publisher`**: A Python app that listens for messages on a WebSocket connection and pushes events to a Kafka queue.
- **`kafka`**: Acts as a broker to store tasks (messages) from Signal.
- **`subscriber-cot-sender`**: A Python app that retrieves messages from Kafka, transforms them to XML (CoT format), and sends them to a TAK server.
- **`tak-server`**: A server that communicates with ATAK devices (ATAK, WinTAK, iTAK) over TCP.

![High Level Architecture Diagram](https://i.imghippo.com/files/jahm1536n.png)

## Tools used


Docker related:
- [Docker](https://www.docker.com/) and [docker-compose](https://github.com/docker/compose) for containerization and orchestration
- [signal-cli-rest-api docker image](https://hub.docker.com/r/bbernhard/signal-cli-rest-api) to comunicate with Signal servers and get messages
- [confluent kafka docker image](https://hub.docker.com/r/confluentinc/cp-kafka) as a brocker setup and comunication betwen sevices
- [taky](https://github.com/tkuester/taky) for comunication with ATAK clients
- [kafka-ui docker image](https://hub.docker.com/r/provectuslabs/kafka-ui) for monitoring kafka in development
- [dozzle docker image](https://hub.docker.com/r/amir20/dozzle) for monitoring docker containers, logging

Python related:
- [confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python) for kafka comunication
- [aiohttp]() to manage async http and websocket conections
- [pytest](https://pypi.org/project/pytest/) to create test
- [watchdog](https://pypi.org/project/watchdog/) for hot reload during development 
- [uv](https://github.com/astral-sh/uv) for package and project managment
- [ruff](https://github.com/astral-sh/ruff) linter and code formatter
## Design Philosophy

This project uses a **Pub/Sub microservice architecture** to ensure **modularity**, **scalability**, and **resilience**. **Kafka** acts as the central **message broker**, decoupling services and enabling **asynchronous communication**. Each service handles a specific task, making the system easier to **develop**, **test**, and **maintain**. **Docker** and **Docker Compose** provide consistent environments, simplifying **deployment** and **scaling**. This architecture allows **independent scaling** of services, efficient handling of **high-throughput messaging**, and **fault tolerance**, as services can recover or restart without affecting the entire system. By isolating functionality, it’s easier to **extend** the system with new **features** or **integrations** in the future.
# Steps to Run the Project

Follow these steps to set up and run the project.

#### Prerequisites
1. Install [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/).

For this project yoy will need:
- **Docker Engine**: 19.03.0 or later
- **Docker Compose**: 1.27.0 or later


#### Setup and Run
1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/v-fol/atak-signal-bot.git
   cd atak-signal-bot
   ```

2. Edit the `.env` file and add your Signal phone number.
```bash
# Example
BOT_PHONE_NUMBER=+38099999999
```
For other environment settings look `docs/ENV.MD`

3. Build and start the Docker containers:
   ```bash
   docker compose up --build
   ```
   - If you are using Docker Compose version 2 or later, you can use `docker compose` (without a hyphen).  
   - For older versions of Docker Compose, use the hyphenated command:
     ```bash
     docker-compose up --build
     ```

4. Open the following URL in your browser to register your device with Signal.
   ```
   http://localhost:8080/v1/qrcodelink?device_name=signal-api
   ```
   Open Signal on your mobile phone, go to Settings > Linked devices and scan the QR code using the + button.

5. Determine your local IP address to configure the TAK client:
   - **Linux**: Run `hostname -I` or `ip a` in the terminal. The IP address will typically be under `inet` for your active network interface.  
   - **Windows**: Open Command Prompt or PowerShell and run `ipconfig`. Look for the "IPv4 Address" under your active network adapter.  
   - **MacOS**: Open Terminal and run `ifconfig`. Your IP address will be listed under your active interface (e.g., `en0` or `en1`) next to `inet`.

6. In the ATAK client, navigate to **Settings > Network Preferences > TAK Server**, and add a new TAK server with the following details:
   - **IP**: Use the local IP address from step 5.
   - **Port**: `8087`
   - **Connection Type**: `TCP`

   This step connects your ATAK client to the TAK server running in the project.

Now the project should be up and running, and the ATAK client will start receiving CoT events from the system!

7. Now you can test the bot, send a message in Signal to your number you entered in step 2. from another account in format - <lat> <lon> <name> (latitude, longitude, name separated with sapces) for example:
```bash
40.7128 74.0060 Tank
40.7128 -74.0060 New trench
```
**You should see a marker in your ATAK client on thouse coordinates**
## Demo
[Watch the demo video](docs/media/demo.mp4)
## Project file structure
```javascript
├── docs                              
│   ├── media
│   │   ├── hla-diagram.svg
├── kafka-data                        # Directory for storing Kafka broker data and logs
├── signal-cli-config                 # Configuration files and data for Signal CLI and REST service
├── signal-listener-publisher         # Service for listening to Signal bot messages and publishing to Kafka
│   ├── app                           
│   │   ├── tests                     # Unit and integration tests
│   │   │   ├── __init__.py           
│   │   │   ├── test_client.py        
│   │   │   ├── test_message_processor.py 
│   │   │   └── test_publisher.py     
│   │   ├── __init__.py               
│   │   ├── client.py                 # Handles HTTP/WebSocket client for comunicating with Signal REST API
│   │   ├── config.py                 # Configuration settings and environment variables
│   │   ├── message_processor.py      # Processes messages received from the Signal bot
│   │   ├── publisher.py              # Publishes processed messages to Kafka
│   │   ├── watcher.py                # Watches file changes in dev mode
│   │   └── main.py                   
│   ├── Dockerfile                    # Docker image definition for the signal-listener-publisher service
│   ├── Dockerfile.test               # Dockerfile for running tests in a containerized environment
│   ├── pyproject.toml                # Python project configuration (dependencies, build system)
│   └── uv.lock                       # Lock file for dependencies
├── subscriber-cot-sender             # Service for subscribing to Kafka and sending CoT events
│   ├── app                           
│   │   ├── __init__.py               
│   │   ├── broker_subscriber.py      # Subscribes to Kafka messages
│   │   ├── config.py                 # Configuration settings and environment variables
│   │   ├── tcp_client.py             # Handles TCP communication with TAK server
│   │   ├── http_client.py            # Handles HTTP comunications with Signal REST API
│   │   ├── xml_transformer.py        # Transforms data into XML format (Cursor-on-Target event format)
│   │   ├── watcher.py                # Watches file changes in dev mode
│   │   └── main.py                   
│   ├── Dockerfile                    # Docker image definition for the subscriber-cot-sender service
│   ├── pyproject.toml                # Python project configuration (dependencies, build system)
│   └── uv.lock                       # Lock file for dependencies
├── tak-server                        # TAK server service (provides communication with ATAK clients)
│   └── Dockerfile                    
├── docker-compose.test.yml           # Docker Compose configuration for running tests
├── docker-compose.yml                # Docker Compose configuration for the entire application stack
├── .gitignore                        
├── .env                              # Environment variables for the Docker Compose setup
└── README.md                         
```