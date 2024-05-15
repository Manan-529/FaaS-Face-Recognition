import boto3
import logging
from face_recognition_code import face_recognition_function
import os

access_key="AKIA5FTZEZJVOEPYW3XG"
secret_key="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"

s3 = boto3.client('s3', region_name = 'us-east-1',  aws_access_key_id = access_key, aws_secret_access_key=secret_key )
output_bucket= "1228984473-output"

def lambda_func(event, context):
    logging.info('Entered the handler function')
    print('Entered the handler function')
    try:
        image_file_name = event.get('image_file_name')
        input_bucket = event.get('bucket_name')
        img_path=os.path.join('/tmp',image_file_name)
        print(image_file_name,input_bucket)
    except Exception as e:
        print(f'Error getting payload from event {event}',e)
        return
    
    
    try:
        s3.download_file(input_bucket, image_file_name , img_path)
        print(f'Downloaded {image_file_name} from {input_bucket} at {img_path}')
    except Exception as e:
        print(f'Error retrieving {image_file_name} from {input_bucket}',e)
        return
    
    try:
        result= face_recognition_function(img_path,'data.pt')
        print('Recognised face: ',result)
    except Exception as e:
        print(f'Error in face recoginition',e)
        return
    
    try:
        s3.put_object( Bucket=output_bucket, Key=image_file_name.split('.')[0]+'.txt', Body=result )
        print(f'Succesfully uploaded {result} to {output_bucket}')
    except Exception as e:
        print(f'Error uploading file to {output_bucket}',e)
    
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }
    
    