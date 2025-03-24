from config import R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET
import boto3
import io
import csv

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://06e472d2b5c60de7e7e2c7c8662427ed.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
)

def load_csv_from_r2(file_name):
    try:
        obj = s3.get_object(Bucket=R2_BUCKET, Key=file_name)
        content = obj["Body"].read().decode("utf-8").strip()
        reader = csv.reader(io.StringIO(content))
        return [row for row in reader if row] 
    except s3.exceptions.NoSuchKey:
        return []


def save_csv_to_r2(file_name, data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    s3.put_object(Bucket=R2_BUCKET, Key=file_name, Body=output.getvalue().encode("utf-8"))
