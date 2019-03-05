import boto3
from image_helpers import get_image

from pprint import pprint


def delete_collection(coll_name):
    """
    Attempts to delete the specified collection.
    Raises an error if the collection does not exist.
    :param coll_name: the name of the collection
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/delete-collection-procedure.html,
    # last access 3/5/2019

    from botocore.exceptions import ClientError

    client = boto3.client('rekognition')
    try:
        client.delete_collection(CollectionId=coll_name)
    except ClientError as e:
        raise e.response['Error']['Code']


def list_collections():
    """
    Returns a list of the names of the existing collections
    :return: a list of the names of the existing collections
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/list-collection-procedure.html,
    # last access 3/5/2019

    client = boto3.client('rekognition')
    response = client.list_collections()
    result = []
    while True:
        collections = response['CollectionIds']
        result.extend(collections)

        # if more results than maxresults
        if 'NextToken' in response:
            next_token = response['NextToken']
            response = client.list_collections(NextToken=next_token)
            pprint(response)
        else:
            break
    return result


def collection_exists(coll_name):
    """
    Checks to see if the collection exists
    :param coll_name: the name of the collection to check
    :return: true iff the collection already exists
    """
    return coll_name in list_collections()


def create_collection(coll_name):
    """
    Creates a collection with the specified name, if it does not already exist
    :param coll_name: the name of the collection to create
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/create-collection-procedure.html,
    # last access 3/5/2019

    client = boto3.client('rekognition')
    if not collection_exists(coll_name):
        response = client.create_collection(CollectionId=coll_name)
        print('Collection ARN: ' + response['CollectionArn'])
        if response['StatusCode'] != 200:
            raise 'Could not create collection, ' + coll_name \
                  + ', status code: ' + str(response['StatusCode'])

