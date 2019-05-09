import json
from DatabaseDAO import DatabaseDAO, dao

from JSONEncoder import JSONEncoder

count = -1

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    # context["callbackWaitsForEmptyEventLoop"] = "false"

    global dao
    global count
    count = count + 1
    user = {}
    user["email"] = event["request"]["userAttributes"]["email"]
    user["nickname"] = event["request"]["userAttributes"]["nickname"]

    dao.connectToDatabase()
    dao.insertUser(user)
    
    return event
