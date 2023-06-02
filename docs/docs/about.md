####

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

###

Документация к проекту находится ниже, данная часть написана для того, чтобы вы понимали зачем это все и как я к этому пришел.

Это уже вторая версия проекта по сбору вакансий с сайта UZT.LT и организации рассылки уведомлений о новых вакансиях в телеграм бота.

Проект имеет образовательный и исследовательский характер для меня как начинающего пайтон разработчика.

В первой версии я ставил для себя задачи:

- иметь возможность собрать нужные мне данные с сайта UZT.LT (сайт службы занятости Республики Литва);
- сохранить данные в базу данных, чтобы иметь возможность обратиться к ним далее;
- разработать простейшего бота, который позволит пользователю получать уведомления о новых вакансиях, в интересующих категориях;
- сканировать сайт биржи с определенной периодичностью, после каждого сканирования производить рассылку подписчикам в боте;

По мере решения этих задач появлялось множество вопросов и неохобходимость в изучении новых технологий и библиотек.

Почему был выбран именно UZT.LT? Во-первых я интересовался вакансиями для джуниор разработчика пайтон, но сайт сделан не совсем удобно для того, чтобы ежедневно отслеживать появление новых вакансий (нет возможности открыть вакансию в новой странице, долгая загрузка сайта при переходе на страницу назад и т.д.).
Во-вторых сайт использует технологию ASP.NET и написан так, что собрать информацию с него на тот момент для меня представлялось крайне сложным делом. Конечно, можно было использовать selenium, и это избавило бы от многих велосипедов, которые мне пришлось изобретать. Но, проект ведь образовательный и исследовательский. Поэтому было решено пойти более сложным и долгим путем.

Первоначально данные сохранялись в базу данных sqlite. Работа с базой была организована с помощь SQLAlchemy. Интересен был декларативный подход и использование ORM. Позже я решил использовать в качестве хранилища базу данных PostgreSQL.

После того как проект был протестирован на локальном компьютере, я разместил его в облачном сервисе EC2 AWS.
Возник вопрос, как запускать части сервиса. Были опробованы screen и tmux. Второй удобнее, на мой взгляд, но все равно не совсем удобно. Поэтому было решено изучить Docker для создания контейнеров, и docker compose для создания контейнеров работающих в связке.

Плюсом первой версии было то, что все операции с базой данных выполнялись в пределах одного компьютера. Все сервисы работали с одной базой данных.

По-мере тестирования сервиса, стало понятно, что основная часть затраченного времени приходится на сканирование сайта и сбор информации о вакансиях. Чтобы ускорить процесс сбора, я использовал мультипроцессинг. Процесс сбора ускорился в 5-6 раз, однако вскоре я обнаружил, что мой граббер размещенный на серве и грабящий сайт биржи 4 разa в день, с периодичностью 2 часа, не может соединиться с сайтом. Был ли он забанен администраторами сайта или же просто это было совпадением с тем, что на сайте была применена защита cloudflare я не знаю. На локальной машине грабер продолжал прекрасно работать.

Начиная писать вторую версию, я решил использовать не изученные мной ранее технологии. А именно Django и REST.

Проект задумывался таким, чтобы бот и грабер имели доступ к удаленной базе через API.

Для реализации этого проекта был выбран фреймворк Django версии 4.2. Он имеет удобную ORM. Имеет готовую админку, с авторизацией, возможностью просмотра и редактирования данных в базе. А также готовые решения для создания API: Django restframework и Django Ninja. Быть может я не совсем разобрался с документацией первого фрейморка, но простота и гибкость работы с Ninja мне более пришлись по душе, и работа продолжилась именно с этой библиотекой.

На данный момент сервис протестирован в работе на локальной машине и планируется его перенос на облако AWS для дальнейшего тестирования.
