# Information retrieval system (Search Engine)

## Requirements

- Python 3.9+
- Django 4.2
- MongoDB

## Installation Steps

Run the following management commands for initial setup:

The Project includes single app:

- retriever

## Installation

Create a Virtual Environment

```sh
pip install virtualenv
virtualenv env
```

Activate Virtual Environment

```sh
 .\env\Scripts\activate
```

Install dependencies and Run the app

```sh
 pip install -r requirements.txt
```

Make migrations

```sh
 python manage.py makemigrations
 python manage.py migrate
```

Run the app

```sh
 cd SearchEngine
 python manage.py runserver
```

### Fronted library used: Bootstrap 5

Usage:

1. The user can insert files it can be a text file, pdf,docs, image, or any other image format. The Use can also add links of the web pages.
2. The system will index the documents and store them in the database.
3. The user can search the documents based on the query.
4. The system will return the documents that match the query.
5. The user can click on the document to view the content of the document.
