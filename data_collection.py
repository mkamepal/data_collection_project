import boto3
import pandas as pd
from flask import Flask, request, jsonify
import io
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    aws_session_token='',
    region_name='us-east-1'
    )

# Initialize S3 client
s3_client = session.client('s3')

# S3 bucket name and file key
bucket_name = 'prompts-dataset'
file_key = 'data-collection.xlsx'

@app.route('/put', methods=['POST'])
def put_data():
    print("hey i am here in put function")
    data = request.json
    print(data)
    new_data = pd.DataFrame([data])

    # Save the new data to an Excel file
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            new_data.to_excel(writer, index=False)
        data_to_upload = output.getvalue()

    # Upload the new Excel file to S3
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