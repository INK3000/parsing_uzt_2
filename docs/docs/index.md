# Scraping jobs from portal.uzt.lt

The service enables the aggregation of job postings from the portal.uzt.lt, storing the gathered data in a database.
This information is subsequently used to distribute notifications of new job vacancies on the site via a Telegram bot.

Service consists of 4 parts: database with REST API, scraper, sender, and telegram bot.

## API service

Full API sevice documentations /api/docs

#### Category

- GET: /api/categories
- POST: /api/categories/create

#### Job

- GET: /api/category/{category_id}/jobs
- POST: /api/category/{category_id}/jobs/create

#### Subscriber

- GET: /api/subscribers
- GET: /api/subscriber/{telegram_id}
- POST: /api/subscriber/create
- POST: /api/subscriber/update
