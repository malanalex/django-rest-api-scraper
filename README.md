# django mini-crawler
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

