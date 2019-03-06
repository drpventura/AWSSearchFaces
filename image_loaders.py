import requests

def get_image_from_url(imgurl):
    """
    Loads and returns the bytes of the image from the specified url
    :param imgurl: the url
    """
    resp = requests.get(imgurl)
    imgbytes = resp.content
    return imgbytes

def get_image_from_file(filename):
    """
    Loads and returns the bytes of the image from the specified file
    :param filename: the name of the file
    Based on
       https://docs.aws.amazon.com/rekognition/latest/dg/example4.html,
       last access 10/3/2017
    """
    with open(filename, 'rb') as imgfile:
        return imgfile.read()

def get_image(img):
    """
    Loads and returns the image either from a URL or a file
    :param img: string that is either the URL or file
    :return:
    """
    if img.lower().startswith('http'):
        return get_image_from_url(img)
    else:
        return get_image_from_file(img)
