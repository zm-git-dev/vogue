from flask import Flask
app = Flask(__name__)
from mongo_adapter import get_client
from vogue.adapter.plugin import VogueAdapter
client = get_client(uri = "mongodb://localhost:27017")
adapter = VogueAdapter(client, db_name = 'trending')
