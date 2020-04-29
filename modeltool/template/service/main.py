import json
import os
import glob
import logging
import time
from flask import request
from utility.tools import FlaskLambda, get_passwd
from read_model import Model_sklearn
from database import insert_model_stats, connect_to_db


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
'''
The FlaskLambda object that is created is the entry point for the lambda. The
LambdaTool deployer expects this to be called 'lambda_handler'
'''
lambda_handler = FlaskLambda(__name__)

db_url = os.environ.get("db_url", None)
db_port = os.environ.get("db_port", None)
db_user = os.environ.get("db_user", None)
db_schema = os.environ.get("dB_schema", None)
lambda_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME", None)
db_password = get_passwd()

logger.info(str(os.environ))


def get_current_date():
    current_time = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return int(current_time)


@lambda_handler.route('/predict', methods=['POST'])
def post_predict():
    database_engine, cursor = connect_to_db(db_user, db_password, db_url, db_schema)
    file_list = glob.glob('models/*')

    if len(file_list) != 1:
        logger.warning('strange number of models')

    model_file = file_list[0]
    if '.pkl' in model_file:
        clf = Model_sklearn()

    json_data_dict = request.get_json(force=True)
    # After parsing, access it like any other dictionary
    features = json_data_dict['features']
    start = time.time()
    predictions = clf.predict(model_file, features).tolist()[0]
    logger.info(predictions)
    end = time.time()
    response_time = round((end - start) * 1000, 2)

    insert_model_stats(
        response_time, model_file.split('/')[-1],
        round(predictions, 3),
        database_engine,
        cursor,
        lambda_name
    )

    database_engine.close()
    return {'predictions': predictions}


@lambda_handler.route('/', methods=['GET'])
def get_test():
    xx = '''<html xmlns="http://www.w3.org/1999/xhtml">
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ping test</title>
</head>
<body>
<div class="container"> 

<div>lambda Name: {valvue} </div>
   <div> post the input features to /predict </div>
</div>

</body>
</html>
'''
    return (
        xx,
        200,
        {'Content-Type': 'text/html'}
    )


@lambda_handler.route('/answer', methods=['GET'])
def get_answer():
    '''
    Example of getting someething from function.properties

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    return (
        os.environ.get('ANSWER', '9'),
        200,
        {'Content-Type': 'text/html'}
    )


@lambda_handler.route('/food', methods=['GET', 'POST'])
def food():
    '''
    A contrived example function that will return some meta-data about the
    invocation.

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    data = {
        'form': request.form.copy(),
        'args': request.args.copy(),
        'json': request.json
    }
    return (
        json.dumps(data, indent=4, sort_keys=True),
        200,
        {'Content-Type': 'application/json'}
    )


if __name__ == '__main__':
    lambda_handler.run(debug=True)
