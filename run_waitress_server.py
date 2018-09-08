import os
from waitress import serve
from fare import app

serve(app,host="0.0.0.0",port=os.environ["PORT"])