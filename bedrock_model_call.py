import boto3
import botocore.config
import json
from datetime import datetime 

def blog_generation(blogtopic:str) -> str:
    # prompt = f"""<s>[INST]Human:Write a detailed 200 words blog post about {blogtopic} 
    # Assistant:[/INST]
    # """
    # body = {
    #     "inputs": prompt,
    #     "parameters": {
    #         "maxTokens": 512,
    #         "temperature": 0.5,
    #         "top_p": 0.9,
    #         "stop": ["</s>"]
    #     }
    # }
    prompt = f"""<s>[INST]Human:Write a detailed 200 words blog post about {blog_topic} 
    Assistant:[/INST]
    """
    body = {
        "prompt": prompt,
        "max_gen_len": 256,
        "temperature": 0.5,
        "top_p": 0.9,
        "stop": ["</s>"]
    }

response = bedrock_runtime.invoke_model(
    modelId='meta.llama3-2-3b-instruct-v1:0', # Or your Provisioned ARN
    contentType='application/json',
    accept='application/json',
    body=json.dumps(body)
)

    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            config=botocore.config.Config(
                read_timeout=300,
                max_pool_connections=5000,
                retries={'max_attempts': 3}
            )
        )
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId='meta.llama3-8b-instruct-v1:0'
        )

        response_content = response.get('body').read()
        response_json = json.loads(response_content)
        print("Bedrock response:", response_json)

        blog_details = response_json['generation']
        return blog_details

    except Exception as e:
        print(f"Error : {e}")
        return ""

def save_blog_details_to_s3(s3_bucket,s3_key,blog_details):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=blog_details)
        print(f"Blog post saved to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving blog post to S3: {e}")     

def  lambda_handler(event, context):

    event = json.loads(event['body'])
    blogtopic = event['blog_topic']
    generate_blog = blog_generation(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key = f"blog-posts/{current_time}.txt"
        s3_bucket = "blogbucket3"  # Replace with your S3 bucket name
        save_blog_details_to_s3(s3_bucket, s3_key, blog_details=generate_blog)
    else:
        print("Failed to generate blog post.")
    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generation is completed')
    } 
