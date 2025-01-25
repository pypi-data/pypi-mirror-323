from os import path
import pandas as pd
import boto3

def upload_parquet_to_aws(
        data_to_upload: str | pd.DataFrame, 
        full_parquet_path: str,
        aws_access_key: str, 
        aws_secret_key: str, 
        aws_region: str, 
        aws_directory: str, 
        s3_folder: str, 
        sheet_name: str = 'Sheet1', 
        header_index: int = 0,
        csv_separator: str = ','): 

    """
        Function gets pull path of a csv/excel file or DataFrame object, converts data to a parquet file and uploads the parquet to AWS S3 folder
        
        data_to_upload: either string with an absolute path to csv/excel file to read data from or DataFrame object
        full_parquet_path: string, an absolute path to a parquet file to save data to
        aws_access_key: string, access key to connect to AWS
        aws_secret_key: string, secret key to connect to AWS
        aws_region: string, region to connect to AWS
        aws_directory: string, directory in S3 bucket 
        s3_folder: string, folder in S3 bucket to upload file to
        sheet_name: string, default to 'Sheet1', sheet name in excel file to read data from
        header_index: integer, default to 0, header index to read data
        csv_separator: string, default to ',', separator used in csv file
    """

    # check if data to upload is Dataframe
    if isinstance(data_to_upload, pd.DataFrame):
        data_df = data_to_upload
    else:
        if '.xls' in data_to_upload.lower():
            data_df = pd.read_excel(data_to_upload, sheet_name= sheet_name, header= header_index)
        #If file is csv
        elif '.csv' in data_to_upload.lower():
            data_df = pd.read_csv(data_to_upload, header= header_index, sep= csv_separator)
        else:
            raise Exception('Not appropriate data to upload. Should be either csv/excel file path or a Dataframe object')
    
    create_parquet(data_df, full_parquet_path)
    upload_file_to_aws(full_parquet_path, aws_access_key, aws_secret_key, aws_region, aws_directory, s3_folder + path.split(full_parquet_path)[1])


def create_parquet(data_df: pd.DataFrame, file_path: str):
    if '.parquet' in file_path.lower():
        data_df.to_parquet(file_path, compression='snappy', index=False, engine='fastparquet')
    else:
        raise Exception('Parquet file path should have .parquet extension')
    
def upload_file_to_aws(file_path, aws_access_key, aws_secret_key, aws_region, aws_directory, s3_folder):       
    """
        Function gets pull path of a csv/excel file or DataFrame object, converts data to a parquet file and uploads the parquet to AWS S3 folder
        
        full_path: an absolute path to a file to upload to aws
        aws_access_key: string, access key to connect to AWS
        aws_secret_key: string, secret key to connect to AWS
        aws_region: string, region to connect to AWS
        aws_directory: string, directory in S3 bucket 
        s3_folder: string, folder in S3 bucket to upload file to + file name with extension
    """
    # Upload file to S3 bucket
    if path.exists(file_path):

        session = boto3.Session(
            aws_access_key_id= aws_access_key,
            aws_secret_access_key= aws_secret_key,
            aws_session_token= '',
            region_name= aws_region
            )
        
        #Creating S3 Resource From the Session.
        resource = session.resource('s3')

        session= resource.Object(aws_directory, s3_folder)
        result = session.put(Body=open(file_path, 'rb'))
        
    else:
        raise Exception(f"File does not exist: {file_path}")
