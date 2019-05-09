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


    # Globasl conn
    global dao
    # global count
    # count = count + 1

    count = -1

    body = json.loads(event["body"])
    dao.connectToDatabase()

    output = ""
    movie = []
    exist = ""
    rate = ""

    if (body["type"] == "favorite"):
        try:
            email = body["email"]
            title = body["title"]
            dao.addToFavorite(email, title)
        except:
            output = "error"
    elif (body["type"] == "watchlist"):
        try:
            email = body["email"]
            title = body["title"]
            dao.addToWatchlist(email, title)
        except:
            output = "error"
    elif (body["type"] == "getFavorite"):
        movie = dao.getFavorite(body["email"], body["start"], body["end"])
        count = dao.countList("favorite", body["email"])
    elif (body["type"] == "getWatchlist"):
        movie = dao.getWatchlist(body["email"], body["start"], body["end"])
        count = dao.countList("watchlist", body["email"])
    elif (body["type"] == "inFavorite"):
        if dao.whetherInList(body["email"], body["title"], "favorite"):
            exist = True
        else:
            exist = False
    elif (body["type"] == "inWatchlist"):
        if dao.whetherInList(body["email"], body["title"], "watchlist"):
            exist = True
        else:
            exist = False
    elif (body["type"] == "removeFavorite"):
        dao.removeFavorite(body["email"], body["title"])
    elif (body["type"] == "removeWatchlist"):
        dao.removeWatchlist(body["email"], body["title"])
    elif (body["type"] == "rateMovie"):
        if body["rate"] == "0":
            rate = dao.rateMovie(body["email"], body["title"], body["rate"])
        else:
            dao.rateMovie(body["email"], body["title"], body["rate"])

    else:
        output = "error"





    return {
        "statusCode": 200,
        "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                    },
        "body": json.dumps({
            # "message": "hello world",
            "output": output,
            "movie": movie,
            # "event": parameters["type"],
            "count": count,
            "exist": exist,
            "rate": rate,
            # "location": ip.text.replace("\n", "")
        }),
    }
