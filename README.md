## About project

This introductory section is written to give you an understanding of the project's purpose and the path I took to arrive here.

This is the second version of a project that aims to scrape job vacancies from UZT.LT and organize notifications about new job postings via a Telegram bot.

For me, as an aspiring Python developer, this project is both educational and exploratory.

In the first version, my objectives were:

- To have the ability to collect the data I need from the UZT.LT site (a job service website from the Republic of Lithuania).
- To store the data in a database so I can access it later.
- To develop a simple bot that allows users to receive notifications about new job vacancies in their areas of interest.
- To scan the job site at regular intervals and, after each scan, send out notifications to the bot subscribers.

As I worked to achieve these goals, numerous questions arose, and there was a need to learn new technologies and libraries.

Why did I choose UZT.LT specifically? Firstly, I was interested in junior Python developer positions. However, the site's design makes it inconvenient for daily tracking of new job postings (e.g., no option to open a job posting in a new page, slow page load times when navigating back, etc.). Secondly, the site employs ASP.NET technology and is structured in such a way that scraping data from it was a significant challenge for me at that time. I could have used Selenium, which would have made many tasks much simpler. However, given the educational and research-focused nature of this project, I decided to take a more complicated and time-consuming route.

Originally, the data was stored in a SQLite database, with SQLAlchemy facilitating the database operations. I was particularly interested in its declarative approach and the use of Object-Relational Mapping (ORM). As the project evolved, I transitioned to a PostgreSQL database for data storage.

After locally testing the project, I deployed it on the Amazon EC2 cloud service. This raised a question about how to launch different parts of the service. I experimented with both 'screen' and 'tmux', finding the latter to be more convenient, albeit still not entirely satisfactory. As a result, I decided to explore Docker for creating containers and Docker Compose to manage containers that need to work together.

A significant advantage of the first version was that all database operations were confined to a single machine; all services interacted with one unified database.

During the service testing phase, it became apparent that the bulk of time was spent on scanning the job site and collecting vacancy data. To expedite this process, I employed multiprocessing, which increased the speed of data collection by 5 to 6 times. However, I soon discovered that my web scraper, hosted on the server and set to scrape the job site four times a day at two-hour intervals, could no longer connect to the site. I couldn't definitively determine whether it had been banned by the site administrators or if the connectivity issues were due to the implementation of Cloudflare protection on the site. Interestingly, the scraper continued to function flawlessly on my local machine.

Starting with the second version, I decided to delve into technologies that were previously unexplored by me - specifically, Django and REST.

The project was envisioned such that the bot and the scraper would be able to access a remote database via an API.

To implement this, I chose Django 4.2 as my framework. It offers a user-friendly ORM, comes with an inbuilt admin panel that includes authentication, and provides the ability to view and edit database records. Additionally, it comes with ready-made solutions for creating APIs: Django Rest Framework and Django Ninja. Although I might not have fully grasped the documentation of the first framework, the simplicity and flexibility of Ninja seemed more appealing, prompting me to proceed with this library.

At the present moment, the service has been tested locally and I'm planning to migrate it to AWS Cloud for further testing.

# Scraping jobs from portal.uzt.lt

The service enables the aggregation of job postings from the portal.uzt.lt, storing the gathered data in a database.
This information is subsequently used to distribute notifications of new job vacancies on the site via a Telegram bot.

Service consists of 4 parts: database with REST API, scraper, sender, and telegram bot.

## Installation

Clone the project from GitHub:

```bash
git clone https://github.com/judecabra/parsing_uzt_2.git
```

After cloning the repository, it is important to perform the configuration of all the services before proceeding. Once the configuration is completed, you can run the command source docker-up-start from the root folder of the project. This command will restart all the containers with the updated configurations.

Please make sure to follow the configuration steps for each service as mentioned in the documentation, and then proceed with running the docker-up-start command to start the containers.

## Configuration

#### API

Rename file api/parsing_uzt_2/.env.dist to .env

Inside .env replace DJANGO_SECRET_KEY with random string.
You can generate one with:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Navigate to the root directory of your project, parsing_uzt_2, and run the command:

```bash
source docker-up-start
```

This will create containers for your services and automatically start the containers parsing_uzt_2-api-1, parsing_uzt_2-nginx-1, and parsing_uzt_2-telebot-1. It will also create containers parsing_uzt_2-webscraper-1 and parsing_uzt_2-sendler-1, but won't start them. You will configure their startup later according to your schedule.

**At this stage, your services are not yet set up for operation.**
You need to create a superuser for the API service (which runs on Django) and obtain an API key to allow your services to interact with the API service.

Therefore, after creating the containers and automatically starting some of them, you need to run some commands:

```bash
docker exec -it parsing_uzt_2-api-1 sh
```

In shell of the container, run:

```bash
cd api
python manage.py createsuperuser
```

Follow the prompts in the command line to create a superuser.

After creating the superuser, you will have access to the admin part of the API service.

In your browser, navigate to http://localhost/admin. If everything is configured correctly, you will see a login form. Enter the username and password of the superuser you created earlier.

After logging in, you will see the names of the tables in our service. We are interested in the "Tokens" table. Click on the "Add" link in the "Tokens" row. This will open a form to create a new token. To create a token, select a user from the dropdown list. You don't need to enter a key as it will be automatically generated. Then click "Save". After that, the form will be closed, and you will see the newly created token in a row like this:

```
User: admin Key: 6DIzCbxuQ5PJBPZV9yci9cSPjY4zrY-e0x3lFJSCvaoBwejiLB1p9ckQbqE
```

The key **6DIzCbxuQ5PJBPZV9yci9cSPjY4zrY-e0x3lFJSCvaoBwejiLB1p9ckQbqE** is your token. Save it as you will need it for further configuration of the services.

#### Telegram bot

The Telegram bot serves as a simple service for subscribing and unsubscribing to notifications about new job vacancies in specific categories.

Assuming you have already created a Telegram bot, let's proceed with the integration. If you haven't created a bot yet, please refer to the documentation you provided (https://core.telegram.org/bots/features#botfather) for instructions on how to create a Telegram bot.

To configure the telebot service, you'll need the tokens from your Telegram bot and the API service. Let's proceed with the setup:

Go to the parsing_uzt_2/telebot/app directory.

Rename the file .env.dist to .env. This file will store your configuration.

Open the .env file using a text editor.

Replace the placeholder values with your actual tokens:

**BOT_TOKEN** - Replace it with your Telegram bot token obtained from BotFather.

**API_KEY** - Replace it with your API token obtained from the API service's admin panel (Look for the configuration section or settings related to API authentication).

Save the changes to the .env file.

By providing the correct tokens, the telebot service will be able to authenticate with both the Telegram API and your API service.

#### Webscraping

To configure the webscraper, follow these steps:

- Go to the parsing_uzt_2/webscraper/app directory.

- Rename the .env.dist file to .env.

- Open the .env file and update the following variables with the appropriate values:
  **API_KEY** - Replace it with your API token obtained from the API service's admin panel.

- Save the changes to the .env file.

To configure the webscraper to interact with the API service running on a different machine or server, follow these steps:

- Go to the parsing_uzt_2/webscraper/app directory.

- Open the .env file.

- Locate the API_BASE_URL variable and update it with the appropriate URL and port where the API service is accessible. For example, if the API service is running on a server with IP address 192.168.1.100 and port 8000, you would set API_BASE_URL=http://192.168.1.100:8000.

- Save the changes to the .env file.

Now, the webscraper will send the scraped data to the specified API service at the provided base URL and port.

If all the services are running on the same machine, you can leave the API_BASE_URL setting unchanged, as it is already configured with the default Docker network address

**To schedule a task** in cron to start the service, you can follow these steps:

Open the cron configuration file by running the command: crontab -e.
Add a new line to the file with the schedule and command to start the container. For example:

```bash
*/5 * * * * /usr/bin/docker start -a parsing_uzt_2-webscraper-1
```

This example will start the container parsing_uzt_2-webscraper-1 every 5 minutes. Adjust the schedule as per your requirements.
Save the file and exit the editor.

### Sendler

To configure the Sendler service, follow these steps:

- Go to the parsing_uzt_2/sendler/app directory.

- Rename the .env.dist file to .env.

- Open the .env file.

- Replace the placeholders for the API token and the bot token with the actual tokens you obtained earlier.
  Replace API_KEY with the API token obtained from the API service's admin panel.
  Replace BOT_API_TOKEN with the token obtained from BotFather for your Telegram bot.

- **Optionally,** if the API service is running on a different server or accessible at a different URL, you can update the API_BASE_URL variable with the appropriate base URL and port.

- Save the changes to the .env file.

Now, the Sendler service is configured with the necessary tokens and API base URL. It will be able to communicate with the API service and the Telegram bot to send notifications about new vacancies.

**To schedule a task** in cron to start the service, you can follow these steps:

Open the cron configuration file by running the command: crontab -e.
Add a new line to the file with the schedule and command to start the container. For example:

```bash
*/5 * * * * /usr/bin/docker start -a parsing_uzt_2-sendler-1
```

This example will start the container parsing_uzt_2-sendler-1 every 5 minutes. Adjust the schedule as per your requirements.
Save the file and exit the editor.
