from django.db import models

# Create your models here.
from elasticsearch import Elasticsearch
client = Elasticsearch(['192.168.1.110'])
