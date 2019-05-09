import json
from DatabaseDAO import DatabaseDAO, dao
from JSONEncoder import JSONEncoder

# count = -1

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
    # global count
    # count = count + 1
    count = -1

    parameters = event["queryStringParameters"]
    dao.connectToDatabase()



    if (parameters["type"] == "find_one"):
        movie = dao.getOneMovie(parameters["title"])
    elif (parameters["type"] == "find_from_to"):
        movie = dao.getMovieFromTo(parameters["genre"], parameters["start"], parameters["end"])
        count = dao.countAll(parameters["genre"])
    elif (parameters["type"] == "find_many"):
        movie = dao.getManyMovies(parameters["query"], parameters["number"])
    elif (parameters['type'] == "topRated"):
        movie = dao.getTopRated(parameters["num"], parameters["minVote"])
    

    # movie = getMovie().get()
    movie = JSONEncoder().encode(movie)



    return {
        "statusCode": 200,
        "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                    },
        "body": json.dumps({
            "movie": movie,
            "count": count,
        }),
    }
