import os
import boto3,json
import subprocess

access_key="aws-access-key"
secret_key="aws-secret-key"
region_name = "aws-region-name"

s3 = boto3.client('s3', region_name = region_name,  aws_access_key_id = access_key, aws_secret_access_key=secret_key )
lambdac = boto3.client('lambda', region_name = region_name,  aws_access_key_id = access_key, aws_secret_access_key=secret_key)

input_bucket= "input-bucket-name"
output_bucket= "stage-1-bucket-name"


def lambda_handler(event, context):
    video_key = event['Records'][0]['s3']['object']['key']
    local_file_path = os.path.join("/tmp", os.path.basename(video_key)) #/tmp/test_6.mp4
    try:
        s3.download_file(input_bucket, video_key, local_file_path)
        print(f'downloaded file from s3 input to {local_file_path}')
    except Exception as e:
        print(f'Error downloading file from s3 {e}')

    filename = os.path.basename(local_file_path)
    outfile = os.path.splitext(filename)[0] + '.jpg'
    outdir = os.path.join("/tmp",outfile)
    print(outfile,outdir)

    try:
        split_cmd = 'ffmpeg -ss 0 -i ' +local_file_path+ ' -vframes 1 ' + outdir + ' -y'
        subprocess.check_call(split_cmd, shell=True)
        print('succesfull check_call')
    except subprocess.CalledProcessError as e:
        print('Error in subprocess check_call',e.output)
        return { 'statusCode': 400, 'body': json.dumps('Error in ffmpeg') }

    print(f'Img saved as: {outdir}') #/tmp/test_6

    s3.upload_file(outdir, output_bucket, outfile)

    try:
        payload = {"image_file_name": outfile, "bucket_name":output_bucket}
        lambdac.invoke(FunctionName= 'face-recognition', Payload=json.dumps(payload) , InvocationType= 'Event')
        print('Success invoking...')
    except subprocess.CalledProcessError as e:
        print('Error involing lambda',e.output)
        return { 'statusCode': 400, 'body': json.dumps(e) }

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
