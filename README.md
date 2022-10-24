Django REST API Crawler
========================

### Description
-   Link scraping API using Django REST Framework;
-   Custom exception handlers;
-   Best practices for configuration split and project structure;

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
    git clone https://github.com/dontpayfull/django-assesment-be-alexmalan.git
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
        ```

5. **Make migrations**:
    ```bash
    python manage.py makemigrations
    ```

6. **Migrate**:
    ```bash
    python manage.py migrate
    ```

## Run

-   Run APP using command:
    ```bash
    python manage.py runserver <optional_port_id>
    ```
- Localhost resources:
    * localhost:<port_id>/admin/ - admin login page
    * localhost:<port_id>/api/page/   - endpoints
    
## Postman Configuration

### Library Import
* Find the django-rest-crawler.postman_collection.json in the root directory
- Open Postman
   - File
      - Import
         - Upload files
            - Open

### Environment Variables
* Environments
   - Add
      - Variable: csrftoken
      - Type: default
   - Save

## Files
* `core` - Django settings files
* `common/` - Django common functionality
* `apps/` - Back-end code
* `venv/` - Virtual environment files used to generate requirements;
    
# Logic Requirements

## django mini-crawler
Urmatorul mini proiect are ca obiectiv evaluarea cunostintelor de backend folosind python, django,   django-rest-framework, celery, docker, docker-compose.

## Requirement
Să se implementeze un mini-crawler, ce va avea ca input un URL, va descărca contentul paginii, si va salva toate link-urile găsite in pagina respectivă.

Se dau următoarele 2 modele:
```python
class Page(models.Model):
	# url = models.CharField... # the input URL
	# added_at = DateTimeField (auto now add)
	# processed_at = DateTimeField (populate after the links are parsed)
	# stats = JSONField() # some counters 


class PageLink(models.Model):
	# page = ForeignKey catre Page
	# href = models.CharField...
	# rel = models.CharField # rel attribute on <a href
    # title = models.CharField # title attribute on <a href
	
```

### Avem nevoie de:
* **implementarea modelelor** `Page` si `PageLink`
* un **REST API** ce implementeaza endpoint-urile CRUD pentru modelul `Page` 
	* de folosit django-rest-framework
	* nu este necesara autentificare
	* endpoint-ul de listare `Page` va trebui sa listeze si toate link-urile paginii
* un **task de download** ce primeste ca intrare un `Page.pk` , 
	* descarca contentul html al paginii
	* il salveaza undeva persistent pentru a-l folosi urmatorul task
* un **task de parsing**, ce primeste ca intrare un `Page.pk` :
	*  preia contentul descarcat anterior
	* extrage link-urile gasite in sursa html, si creaza cate un `PageLink` pentru fiecare link gasit 
	* actualizeaza Page.stats cu urmatorul JSON: `{total_links: 10, unique_links: 5}`
	* seteaza Page.processed_at = now
* **2 workeri** ce vor executa cele 2 task-uri (download/parse) pe cozi diferite
* o comanda de management ce ia  ca parametru de intrare  un URL, si face call catre endpoint-ul REST de creare page.
* **reteta docker compose** cu urmatoarele containere:
	* rabbitmq
	* worker de download
	* worker de parsare links
	* rest api
	* o baza de date (pate fi orice, mysql, postgres, chiar si un volum cu sqlite montat pe toate celelalte containere)



### Flow de crawling

1. Se face POST catre endpoint-ul de creare `Page` cu un singur argument: `url`
2. Dupa salvarea `Page`-ului in DB, se trimit automat la broker task-urile de download si parsing
3. endpoint-ul de listare `Page` trebuie sa returneze următoarele field-uri:
	* `pk`
	* `url`
	* `stats`
	* `added_at`
	* `processed_at`
	* `links` -> lista cu toate link-urile extrase din pagina

###  Alte informatii 
* un `Page` va ave unul sau mai multe `PageLink` 
* pentru download-ul unui `Page.url` se va folosi un apel http catre respectivul url
* Link-urile ce trebuie extrase din conținutul paginilor descarcate sunt de forma
 ```
    <a href="https://www.emag.ro/resigilate?ref=hdr_resigilate" title="Resigilate" rel="nofollow">
        Resigilate
    </a>
```
* din care se extrage
	*  `a[href]` -> se salveaza pe -> `PageLink.href` 
 	*  `a[rel]` -> se salveaza pe -> `PageLink.rel` (optional, popate sa fie gol)
 	*  `a[title]` -> se salveaza pe -> `PageLink.title` (optional, poate sa fie gol)

