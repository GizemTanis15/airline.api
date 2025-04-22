from flask import Flask
from flasgger import Swagger

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Test API",
        "description": "Testing Flasgger visibility",
        "version": "1.0"
    }
}


@app.route('/hello')
def hello():
    """Test Hello
    ---
    responses:
      200:
        description: Returns hello
    """
    return "hello"
swagger = Swagger(app, config=swagger_config, template=template)
if __name__ == '__main__':
    app.run(debug=True)
