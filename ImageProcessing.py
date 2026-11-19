import gdown
import subprocess
import AwsConfig

img_dict = {}

def image_processing(url,img_name):

    if img_dict.get(url) is not None:
        print('already image uploaded:'+str(img_dict.get(url)))
        return img_dict.get(url)

    print('url:'+str(url))
    img_id = url.split('/')[-2]
    #prefix = 'https://drive.google.com/uc?export=download&id='
    url = f"https://drive.google.com/uc?export=download&id={img_id}"
    print('Downloading image .....'+str(img_name))
    try:
       # gdown.download(prefix + img_id, output=img_name, quiet=False, fuzzy=True)
        gdown.download(url, output=img_name, quiet=False, fuzzy=True, use_cookies=False)
        s3_url = write_image_s3(img_name)
        img_dict.update({url:s3_url})
    except Exception as ex:
        print('download exception error as : ',ex)

    return s3_url



def write_image_s3(imageName):
    s3_base_url = 'https://lstingimages.s3.ap-south-1.amazonaws.com/'
    con = AwsConfig.s3_connect()
    BUCKET = 'lstingimages'
    IMAGE_KEY = imageName
    con.upload_file(IMAGE_KEY,BUCKET,imageName,ExtraArgs={
        "ContentType": "application/jpg",
        "ContentDisposition": "inline"
    })
    ### Making S3 object public.
    con.put_object_acl(Bucket=BUCKET, Key=imageName, ACL='public-read')

    return str(s3_base_url)+imageName


class ImageProcessing:
    def __init__(self):
        pass

