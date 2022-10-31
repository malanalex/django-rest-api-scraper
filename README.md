Django REST API Crawler
========================

### Description
-   Link scraping API using Django REST Framework;
-   Custom exception handlers;
-   Flower implementation for task monitoring;
-   Task retry with exponential backoff;
-   Logging with custom base logger;
-   Best practices for configuration split and project structure;

### Important
-  *This implementation is not production ready, it's just a proof of concept*
-  There is an issue with Docker if you are using a M1/M2 Macbook which is why you have to force the config: --platform=linux/amd64

### Possible improvements
-  Enhanced error tracking with Sentry;
-  Validation of the URLs + duplicate checks;
-  Better scraping and requests mechanism;
-  Further scraping options - with the current links as a starting point;
 
## Code quality

### Static analysis
- Static code analysis used: https://deepsource.io/

### Pylint
- Pylint used to maintain code quality;
- Current status: `Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)`

### Requirements

-   It is assumed that you have Python. If not, then download the latest versions from:
    * [Python](https://www.python.org/downloads/)
    * [PostgreSQL](https://www.postgresql.org/download/)
	* [Docker](https://www.docker.com/)
	* [RabbitMQ](https://www.rabbitmq.com/download.html/)
    
### Installation

1. **Clone git repository**:
    ```bash
    git clone https://github.com/alexmalan/django-rest-api-scraper.git
    ```

2. **Create virtual environment**
	- You can use `virtualenv` or `venv` or conda environment for this.
    ```bash
    python -m venv $(pwd)/venv
    source venv/bin/activate
    ```

3. **Install requirements**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Add environment variables**
    - Create a file named `.env` in project root directory
    - Add and fill next environment variables with your local database config:
        ```.env
        SECRET_KEY=
        DATABASE_NAME=
        DATABASE_USER=
        DATABASE_PASSWORD=
        DATABASE_HOST=
        DATABASE_PORT=
        CELERY_BROKER_URL=
        CELERY_RESULT_BACKEND=
        ```

5. **Make migrations**:
    ```bash
    python manage.py makemigrations
    ```

6. **Migrate**:
    ```bash
    python manage.py migrate
    ```

## Run Local
- The following instructions will help you run the program on local machine.
- The program is designed to run with:
    * RabbitMQ as a broker
    * Celery as a task queue
    * Redis as a result backend
    * Flower as task monitoring

- There are 2 queues:
    * `download_queue` - for downloading source html code
    * `parse_queue` - for parsing html

- For each queue we will start a Celery worker. Open 4 Terminals and run one process in each as described below:
-   Run RabbitMQ using command:
    ```bash
    sudo rabbitmq-server
    ```
-   Run Redis using command:
    ```bash
    brew services start redis
    ```  
-   Run Flower monitoring using command:
    ```bash
    celery -A crawler flower
    ```   
    * Flower will be available at http://localhost:5555/
-   Run DOWNLOAD WORKER using command:
    ```bash
    celery --app=core.celery worker -Q download_queue -E
    ```
-   Run PARSE WORKER using command:
    ```bash
    celery --app=core.celery worker -Q parse_queue -E
    ```
-   Run APP using command:
    ```bash
    python manage.py runserver <optional_port_id>
    ```
- Localhost resources:
    * localhost:<port_id>/admin/ - admin login page
    * localhost:<port_id>/api/page/   - endpoints

## Run Docker
- The following instructions will help you run the program on docker.
- The Docker will run the following:
    * Django server
    * RabbitMQ as a broker
    * Redis as backend
    * Worker1 Celery as parse_queue
    * Worker2 Celery as download_queue
    * Postgres as database
    * Flower as task monitoring
    * PgAdmin as a database management tool

- For each queue we will start a Celery worker. Open 4 Terminals and run one process in each as described below:
-   Run Docker buil using command:
    ```bash
    docker build .
    ```
-   Run Docker Compose using command:
    ```bash
    docker-compose up -d
    ```  
-   The application should run now
    * Flower will be available at http://localhost:5555/
    * PgAdmin will be available at http://localhost:5050/
        * username: admin@admin.com
        * password: root
        - You can add a new server:
            - Register > Server
                - General:
                    * Name: postgres
                - Connection:
                    * Host name/address: DATABASE_HOST from .env
                    * Port: DATABASE_PORT from .env
                    * Maintenance database: postgres
                    * Username: DATABASE_USER from .env
                    * Password: DATABASE_PASSWORD from .env
                - Save
        - You can query the tables:
            - postgres > Schemas > public > Tables > table > View/Edit data > All rows
## Postman Configuration

### Library Import
* Find the django-rest-crawler.postman_collection.json in the root directory
- Open Postman
   - File
      - Import
         - Upload files
            - Open

#### Note
- There are the LOCAL and DOCKER endpoint options

### Environment Variables
* Environments
   - Add
      - Variable: csrftoken
      - Type: default
   - Save

### Run tips
- Try not to run the same page multiple times since you might get a 511(Network Authentication Required)
- You might get blocked for multi-requests to the same site as this app does not use PROXYs
- For Proxy please check: https://www.zyte.com/

## Files
* `core` - Django settings files
* `common/` - Django common functionality
* `apps/` - Back-end code
* `venv/` - Virtual environment files used to generate requirements;

## Test
Run command:
* python manage.py test -k --verbosity 2
* python manage.py test {app_name} -k --verbosity 2
    * [Important] 
        * To use same database for test and development `-k ( -keepdb )`
            - otherwise, django will try to create a separate new db '{db_name}_test'
        * Optional `--verbosity 2`
            - displays the result foreach test
        * If tests are not working make sure all migrations are done : 
            `python manage.py migrate`

## Design Notes
### Flow
- The flow of execution goes like this:
    1. User sends a POST request to the endpoint `/api/page/` with a JSON body containing the URL to be scraped.
    2. The request is received by the PageCreateView which first validates the payload and duplicates cases for the url.
    3. If the payload is valid the scrape_job task is called from /tasks.
    4. The scrape_job task is responsible for downloading the HTML of the URL and parsing it for links by chaining the crawl_data and parse_data tasks.
    5. If the task executed successfully, a Page record is created in the Page table and a batch of PageLink record is created in the PageLink table.
    6. The user received a 204 response.
