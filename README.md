# Serverless Notification System

## Overview
The Serverless Notification System is an event-driven, decoupled architecture designed to reliably process and send out user notifications. By leveraging cloud-native serverless components, it ensures high availability, scalability, and resilience without the overhead of managing infrastructure.

This project represents a "mini version" of a robust notification system often found in major enterprise environments. It incorporates professional practices like producer-consumer patterns, structured logging, input validation, internal retry strategies, and structural understanding of Dead Letter Queues (DLQs).

## Architecture
The system employs an asynchronous Producer-Consumer pattern:

1. **Producer (API Handler):** Acts as the entry point, receiving client requests (e.g., via API Gateway). It performs strict model validation and immediately queues the payload into an SQS Queue for asynchronous processing, allowing rapid API responses.
2. **Message Broker (SQS):** Decouples the frontend API from backend delivery systems. It securely stores notification events to handle traffic spikes and protects downstream services from being overwhelmed.
3. **Consumer (Worker Handler):** An event-driven Lambda function that polls the SQS queue. It processes each event sequentially (or concurrently depending on AWS batching), routing notifications via Amazon SES (Simple Email Service) or simulating pushes.

## Tech Stack
- **Python 3.x**
- **AWS Lambda:** Serverless execution for API routing and event processing
- **Amazon SQS:** Message queuing / Broker service
- **Amazon SES:** Cloud email delivery service
- **boto3:** AWS SDK for Python

## Features
- **Decoupled Design:** High resilience ensuring no blocking calls exist between incoming requests and final outbound delivery.
- **Fail-safe Retries & DLQ:** Incorporates soft-retries during execution and falls back to infrastructure level retries and Dead Letter Queue routing for "poison pill" messages.
- **Structured Logging:** Centralized logging module formatting outputs correctly.
- **Modular Services:** Clean separation of concerns (Handlers vs. Services vs. Utilities).
- **Input Validation:** Strict defensive programming on incoming payloads rejecting malformed data early.

## Folder Structure
```text
serverless_notifier/
├── README.md
├── requirements.txt
└── src/
    ├── handlers/
    │   ├── api_handler.py          # API Endpoint entry (Producer Lambda)
    │   └── worker_handler.py       # SQS Event processor (Consumer Lambda)
    ├── services/
    │   ├── email_service.py        # Abstracted SES integration
    │   ├── notification_service.py # Core logical orchestrator
    │   └── sqs_service.py          # Abstracted SQS publisher
    └── utils/
        ├── config.py               # Environment variables fallback configs
        ├── logger.py               # Standardized logging formatter
        └── validator.py            # API request payload validation logic
```

## How It Works (Step-by-Step)
1. **Intake Request:** A client sends a POST request (`{"email": "...", "message": "..."}`) which hits the `api_handler`.
2. **Data Validation:** The Handler uses the Validator utility to ensure standard integrity checking before executing deeper code.
3. **Queuing Strategy:** Instead of attempting to send the email synchronously, the data payload is passed to the SQS Service and appended onto the queue.
4. **Immediate Client Response:** The API Handler returns an HTTP `202 Accepted` cleanly indicating receipt.
5. **Consumption Loop:** SQS pushes batches of messages to the `worker_handler` (Consumer Lambda).
6. **Processing & Delivery:** The Worker unwraps the SQS record and triggers the Notification Service, sending the actual message through Amazon SES and firing simulated pushes.
7. **Resilience & DLQ Routing:** If any errors emerge (e.g., SES is throttling,.etc), the internal retry loop engages. If all transient retries fail, a fatal error cascades back to Lambda/SQS logic, pushing the message onto a Dead Letter Queue (DLQ) for subsequent recovery or manual observation without dropping data.

---
> **Note:** This codebase is structurally inspired by real-world scalable systems designed intentionally to survive faults and segregate responsibilities neatly. It demonstrates cloud architecture literacy, Python modularity, and clean error resolution concepts for robust production thinking.
