## ToDo

### API service

- endpoints for manage category +
- endpoints for manage subscriber (fix: change id to telegram_id) +
- endpoints for manage category/{category_id}/jobs/create +
- manage bulk_creation for categories +
- manage docs for API on Home page +

### Webscraping service

- UZTScraper class +
- Algorithm for webscraper (open startpage, get categories, walk all categories,
  scrap all pages, send data in every category to API for saving) +

### Miscleanos

- telebot: - get subscribers and create subscribers +
- API: Update subscriber - last_upd_date +
- telebot: manage subscription: to_add, to_remove +
- API:authorisation. create token +
- sendler: get users, get categories, get jobs +
- telebot: hide categories +
- sendler: filter only new jobs +
- API: parameter "from" to jobs +
- sendler: to mail +
- API, Webscraper: remove unused fields +
- Docs: add all dependencies +
- Docs: update API endpoints +
- Docs: add description of the project
- Docker: create dockerfile for sendler and webscraper service +
- Docker: network for services. Telebot and api +
- **Docker: create dockercompose and up services on local machine**
- **Docs write manual to all services**
