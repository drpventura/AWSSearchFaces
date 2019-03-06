import boto3
from pathlib import Path
from pprint import pprint
# note for my Cloud Computing students,
# image_loaders.py is the new name for image_helpers.py
from image_loaders import get_image
from typing import List

def delete_collection(coll_name: str):
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


def list_collections() -> List[str]:
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


def collection_exists(coll_name: str) -> bool:
    """
    Checks to see if the collection exists
    :param coll_name: the name of the collection to check
    :return: true iff the collection already exists
    """
    return coll_name in list_collections()


def create_collection(coll_name: str):
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
        if response['StatusCode'] != 200:
            raise 'Could not create collection, ' + coll_name \
                  + ', status code: ' + str(response['StatusCode'])


def list_faces(coll_name: str) -> List[dict]:
    """
    Return a list of faces in the specified collection.
    :param coll_name: the collection.
    :return: a list of faces in the specified collection.
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/list-faces-in-collection-procedure.html
    # last access 3/5/2019

    client = boto3.client('rekognition')
    response = client.list_faces(CollectionId=coll_name)
    tokens = True
    result = []

    while tokens:

        faces = response['Faces']
        result.extend(faces)

        if 'NextToken' in response:
            next_token = response['NextToken']
            response = client.list_faces(CollectionId=coll_name,
                                         NextToken=next_token)
        else:
            tokens = False

    return result


def add_face(coll_name: str, image: str):
    """
    Adds the specified face image to the specified collection.
    :param coll_name: the collection to add the face to
    :param image: the face image (either filename or URL)
    """

    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/add-faces-to-collection-procedure.html
    # last access 3/5/2019

    # nested function
    def extract_filename(fname_or_url: str) -> str:
        """
        Returns the last component of file path or URL.
        :param fname_or_url: the filename or url.
        :return: the last component of file path or URL.
        """
        import re
        return re.split('[\\\/]', fname_or_url)[-1]

    # rest of the body of add_face
    client = boto3.client('rekognition')
    rekresp = client.index_faces(CollectionId=coll_name,
                                 Image={'Bytes': get_image(image)},
                                 ExternalImageId=extract_filename(image))

    if rekresp['FaceRecords'] == []:
        raise Exception('No face found in the image')


def find_face_id(coll_name: str, ext_img_id: str) -> str:
    """
    Find the face_id for the specified image in the collection.
    :param coll_name: the name of the collection.
    :param ext_img_id: the ExternalImageId set for the image
    :return: the ImageId if found, or the emtpy string otherwise
    """
    face = [face for face in list_faces(coll_name) if face['ExternalImageId'] == ext_img_id]
    if face != []:
        return face[0]['ImageId']
    else:
        return ''


def delete_face(coll_name: str, face_ids: List[str]) -> str:
    """
    Deletes the specified faces from the collection.
    :param coll_name: the name of the collection
    :param face_ids: a list of face ids (see FaceId) field in collection
    :return: returns a list of the face ids that were deleted
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/delete-faces-procedure.html
    # last access 3/5/2019

    client = boto3.client('rekognition')
    response = client.delete_faces(CollectionId=coll_name,
                                   FaceIds=face_ids)
    return response['DeletedFaces']


def find_face(coll_name: str, face_to_find: str) -> List[dict]:
    """
    Searches for the specified face in the collection.
    :param face_to_find: a string that is either the filename or URL to the image containing the face to search for.
    :return:
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/search-face-with-image-procedure.html
    # last access 3/5/2019
    client = boto3.client('rekognition')

    rekresp = client.search_faces_by_image(CollectionId=coll_name,
                                           Image={'Bytes': get_image(face_to_find)})

    return rekresp['FaceMatches']


if __name__ == '__main__':
    delete_collection('Faces')
    create_collection('Faces')

    images_dir = Path('images')
    images = [str(images_dir / fname) for fname in ['portrait.jpg', 'old.jpg']]
    # images = [str(ref_images_dir / fname) for fname in ['portrait.jpg']]

    for image in images:
        add_face('Faces', image)
    pprint(list_faces('Faces'))

    # pprint(find_face('Faces', 'https://m.media-amazon.com/images/M/MV5BNDExMzIzNjk3Nl5BMl5BanBnXkFtZTcwOTE4NDU5OA@@._V1_UX214_CR0,0,214,317_AL_.jpg'))
    pprint(find_face('Faces', r'images\tampabay.jpg'))

    face_ids = [face['FaceId'] for face in list_faces('Faces')]
    pprint(face_ids)
    delete_face('Faces', face_ids)
