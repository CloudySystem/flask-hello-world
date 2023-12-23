from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KubeOps Challenge</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
