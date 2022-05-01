# TechConf Registration Website

## Project Overview

The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:

- The web application is not scalable to handle user load at peak
- When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
- The current architecture is not cost-effective

In this project, you are tasked to do the following:

- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:

- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App

1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
     - `POSTGRES_URL`
     - `POSTGRES_USER`
     - `POSTGRES_PW`
     - `POSTGRES_DB`
     - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function

1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

   **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.

   - The Azure Function should do the following:
     - Process the message which is the `notification_id`
     - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
     - Query the database to retrieve a list of attendees (**email** and **first name**)
     - Loop through each attendee and send a personalized subject message
     - After the notification, update the notification status with the total number of attendees notified

2. Publish the Azure Function

### Part 3: Refactor `routes.py`

1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Development and testing Cost Analysis

| Azure Resource          | Service Tier                      | Monthly Cost |
| ----------------------- | --------------------------------- | ------------ |
| Azure Postgres Database | Single server, Basic 1 vCore, 5GB | $48.07       |
| Azure Service Bus       | Basic tier, 0 million/month       | $0           |
| Azure Functions         | Consumption plan                  | $0           |
| Azure App Service       | Free tier F1 1GB ram, 1GB storage | $0           |
| Azure Storage Account   | General purpose v1                | $24.01       |
| Estimated monthly Cost  |                                   | $72.08       |

## Production Cost Analysis

| Azure Resource          | Service Tier                               | Monthly Cost |
| ----------------------- | ------------------------------------------ | ------------ |
| Azure Postgres Database | Single server, General purpose Gen 5       | $397.07      |
| Azure Service Bus       | Standard                                   | $9.81        |
| Azure Functions         | Premium 1 Core 3.5GB Ram 250GB Storage     | $365.07      |
| Azure App Service       | Standard S2 2 Cores 3.5GB Ram 50GB Storage | $138.70      |
| Azure Storage Account   | General purpose v1                         | $24.01       |
| Estimated monthly Cost  |                                            | $934.67      |

## Architecture Explanation

I choose both Azure App Service and Azure Functions because they have the folloing advatanges
Azure App Service:

- Easy and fast to deploy web app because we don't care about operating system, hardware,..
- Save of cost. The price to deploy an app is free (Free tier F1 1GB ram, 1GB storage).
- The app will be available 99,95% of the time.
- Auto-scaling

Azure Functions

- Easily use it to incorporate with Azure Service Bus, Azure Event Hub,...
- Save of cost. We only pay as we execute the function.
- Easily scale the function if we need

Using Azure Wep App for frontend and Azure Functions for backend to reduce error due to http timeout. This architecture is scalable, cheap
and performing web app with microservices that easy to maintain. Besides, using Azure Service Bus to decouple application and service
from each other. The message will be added to the queue of Service Bus, it sends the email to attendees and update status when the function is
triggered.
