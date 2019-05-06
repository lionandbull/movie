# FindYourMoive
Demo Link: https://lionandbull.github.io/movie-react/


> **Content**
> 1. Introduction
> 0. Ranking


## Introduction
Our project is to build a movie website that provides basic information of movies including movie name, movie synopsis, movie trailer and movie poster, and two searching engines. The first searching engine is used for searching movie by exact or fuzzy movie name. The second searching engine is an advanced one. Supposed there is a fragment of a movie coming out from your head, but you don’t know what exactly name it is. In this situation, our second advanced searching engine could help you to find what you want. You only need type the scenario showed up in your head, translate it to words, we can base on your input to find the most likely movie. Furthermore, for the two searching engines, we will rank all the possible results to users as well.


## Ranking


### TF-IDF & Cosine Similarity



Based on the indexing results of on title, plot and script, here we merge the results together and measure a rank of the search results. (refer to [queryWorker.py](https://github.com/2019-Spring-Information-Retrieval/backend/blob/master/queryWorker.py))


For word frequency indexes, we use TF-IDF (skLearn) to measure the ranking scores; while for positional indexes, we use Cosine Similarity (numpy) to measure the ranking scores. (refer to [rankWorker.py](https://github.com/2019-Spring-Information-Retrieval/backend/blob/master/rankWorker.py#L167))


### Learning Index Weights

Based on the ranking scores of different indexes, we measure the weighted sum of ranking scores as the final ranking scores of every candidate search result. (refer to [rankWorker.py](https://github.com/2019-Spring-Information-Retrieval/backend/blob/master/rankWorker.py#L11))

We use Logistic Regression to learn the weights of every ranking score, where the loss function meansuring distance between target ranking order and predicted ranking order. (refer to []())


### Labs Features

In this project, we also explore some amazing features to boost the searching results, with the help of Neural Network.


#### Latent Answer Detecting

The feature of Latent Answer Detecing aiming to extract some valuable phrases from document, which would likely to be the potential answer of searching question, or related context of user-descripted conditions. The idea is simple that some phrases might be summarization or details for the whole text, which is more likely to be queried.

Given a text as input, the model will output a sequence of B-I-O labels for every token in the text. The phrase started with 'B' and ended with the last 'I' is taken as one valuable phrases. (trained model refer to [checkpoint.ck](https://drive.google.com/open?id=1He2n7msauGPDNHqXwSTH6CiJqKNqZVLp) and code refer to [Answer_Tagging_Pytorch.ipynb](https://drive.google.com/open?id=1WjDMs_RH7R1xSHzM3hQd3tuOj0gZZJdq))



#### Question Word Generating

The feature of Qustion Word Generating aiming to generate some complement words with query words, which would extend the original query words of searching. The idea is strainforwad that query words might be different to the expression of related content, which required to add more "guessing words" to search the target.

Given a short text as input, the model will output a list of predicted query words. The original words of input text and model-generated words will togather to treated as query words for searching. (code refer to [Question_Generating_Pytorch.ipynb](https://drive.google.com/open?id=1O6os8qgnBxFe-UOaAQizG_IUFOx8x0U8))






