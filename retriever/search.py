from elasticsearch_dsl import Document, Text,  Integer

class DocumentIndex(Document):
    id = Integer()
    title = Text()
    content = Text()

    class Index:
        name = 'my_document_index'