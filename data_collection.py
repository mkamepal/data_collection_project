import boto3
import pandas as pd
from flask import Flask, request, jsonify
import io
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_REGION')
    )

# Initialize S3 client
s3_client = session.client('s3')
#firehouse_client = session.client('firehose')
#delivery_stream_name = 'your-delivery-stream-name'

# S3 bucket name and file key
bucket_name = 'prompts-dataset'
file_key = 'data-collection.xlsx'

@app.route('/put', methods=['POST'])
def put_data():
    data = request.json
    new_data = pd.DataFrame([data])

    # load the existing Excel file from S3
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        contents = response['Body'].read()
        existing_data = pd.read_excel(io.BytesIO(contents))
    except s3_client.exceptions.NoSuchKey:
        # If the file does not exist, create an empty DataFrame
        existing_data = pd.DataFrame()

    # Append the new data to the existing data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Save the updated data to an Excel file
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            updated_data.to_excel(writer, index=False)
        data_to_upload = output.getvalue()

    # Upload the updated Excel file to S3
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=data_to_upload)

    return jsonify({'message': 'Data added successfully'})


@app.route('/get', methods=['GET'])
def get_data():
    # Download the Excel file from S3
    #print("I am in get function")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    #print(response['Body'])
    contents = response['Body'].read()
    df = pd.read_excel(io.BytesIO(contents))
    #data = pd.read_excel(response['Body'])
    # Convert the data to JSON format
    #data_json = data.to_json(orient='records')
    #print(df)
    df_json = df.to_json(orient='records')
    return jsonify(json.loads(df_json))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)