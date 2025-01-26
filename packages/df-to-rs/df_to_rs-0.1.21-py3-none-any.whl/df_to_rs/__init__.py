import csv
import io
import random
import string
import boto3
import time
import pandas as pd
import psycopg2
import json

class df_to_rs:
    def __init__(self, region_name, s3_bucket, aws_access_key_id=None, aws_secret_access_key=None, redshift_c=None):
        """
        region_name: AWS region name, e.g., 'ap-south-1'.
        s3_bucket: Name of the S3 bucket to upload CSV files.
        aws_access_key_id: Optional AWS access key ID. If None, uses instance role
        aws_secret_access_key: Optional AWS secret access key. If None, uses instance role
        redshift_c: psycopg2 connection object to Redshift, e.g.,
        redshift_c = psycopg2.connect(dbname=, host="hostname.ap-south-1.redshift.amazonaws.com", port=1433, user='ankit.goel', password='xxxx')
        redshift_c.set_session(autocommit=True)
        """
        self.region_name = region_name
        self.s3_bucket = s3_bucket
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.redshift_c = redshift_c

    def _get_s3_client(self):
        """Helper method to get S3 client using either credentials or instance role"""
        if self.aws_access_key_id and self.aws_secret_access_key:
            return boto3.resource('s3',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
        else:
            return boto3.resource('s3', region_name=self.region_name)

    def upload_to_redshift(self, df, dest):
        """
        Uploads the given DataFrame to the specified destination in Redshift.
        df: pandas DataFrame to be uploaded.
        dest: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        Now handles JSON columns intended for SUPER format.
        """
        s3 = None
        try:
            start_time = time.time()
            print("Generating randomized CSV filename...")
            csv_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.csv'
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Converting DataFrame to CSV in-memory...")
            
            # ✦✦ A. DataFrame Cleanups ✦✦ 
            #================================================================
            # - Special Characters handled
            # - Long length handled
            # - JSON handled
            #================================================================
            def escape_special_chars_and_truncate(s):
                if isinstance(s, str):
                    s = s.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace(',', '\\,')
                    return s[:55000]
                return s
            string_columns = df.select_dtypes(include=['string']).columns
            df[string_columns] = df[string_columns].applymap(escape_special_chars_and_truncate)

            def json_to_super(s):
                if isinstance(s, (dict, list)):
                    return json.dumps(s)[:55000]  # Apply same length restriction
                return s

            # Single applymap for all object columns
            object_columns = df.select_dtypes(include=['object']).columns
            df[object_columns] = df[object_columns].applymap(json_to_super)


            # ✦✦ B. Chunk and Upload ✦✦ 
            #================================================================
            chunk_size=1_000_000
            num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)
            if len(df) > chunk_size:
                print(f"DataFrame is large, splitting into {num_chunks} chunks.")


            s3 = self._get_s3_client()
            for chunk_num in range(num_chunks):
                chunk = df.iloc[chunk_num*chunk_size : (chunk_num+1)*chunk_size]
                csv_buffer = io.StringIO()
                chunk.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_ALL, quotechar='"', na_rep='')
                csv_buffer.seek(0)
                print(f"Time taken for preparing chunk {chunk_num}: {int(time.time() - start_time)} seconds")

                print(f"Uploading chunk {chunk_num} CSV to S3 bucket '{self.s3_bucket}'...")
                
                s3.Object(self.s3_bucket, csv_filename).put(Body=csv_buffer.getvalue())
                print(f"Time taken for uploading chunk {chunk_num}: {int(time.time() - start_time)} seconds")

                print(f"Preparing Redshift COPY command for chunk {chunk_num}...")
                columns = ','.join(df.columns)

                if self.aws_access_key_id and self.aws_secret_access_key:
                    credentials_part = f"""
                    ACCESS_KEY_ID '{self.aws_access_key_id}'
                    SECRET_ACCESS_KEY '{self.aws_secret_access_key}'
                    """
                else:
                    credentials_part = "IAM_ROLE 'default'"  # Uses instance role

                copy_query = f"""
                COPY {dest} ({columns})
                FROM 's3://{self.s3_bucket}/{csv_filename}'
                {credentials_part}
                DELIMITER ','
                IGNOREHEADER 1
                REMOVEQUOTES
                REGION '{self.region_name}';
                """
                print(f"Executing Redshift COPY command for chunk {chunk_num}...")
                self.redshift_c.cursor().execute(copy_query)
                print(f"Time taken for COPY command execution for chunk {chunk_num}: {int(time.time() - start_time)} seconds")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            if s3:  # Only attempt cleanup if s3 was created
                try:
                    print(f"Deleting CSV file '{csv_filename}' from S3...")
                    s3.Object(self.s3_bucket, csv_filename).delete()
                    print(f"Time taken: {int(time.time() - start_time)} seconds")
                except Exception as e:
                    print(f"An error occurred during cleanup: {e}")

            print("Upload to Redshift process completed.")


    def upsert_to_redshift(self, df, dest_table, upsert_columns, clear_dest_table=False):
        """
        Upserts the given DataFrame to the specified destination table in Redshift.
        Optionally clears the destination table if clear_dest_table is True.
        
        Parameters:
        - df: pandas DataFrame to be upserted.
        - dest_table: Redshift destination table, including schema, e.g., 'analytics.ship_pen'.
        - upsert_columns: List of columns to use for the upsert condition, e.g., ['id', 'name'].
        - clear_dest_table: Boolean, if True, clears the destination table before upserting.
        """
        cursor = self.redshift_c.cursor()
        staging_table = dest_table + "_stgg"

        # Check if any upsert column has nulls
        has_nulls = df[[col.replace('"','') for col in upsert_columns]].isnull().any().any()

        try:
            start_time = time.time()
            print("Creating staging table...")
            create_staging_query = f"DROP TABLE IF EXISTS {staging_table}; CREATE TABLE {staging_table} AS SELECT * FROM {dest_table} WHERE 1 = 0;"
            cursor.execute(create_staging_query)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Uploading data to staging table...")
            self.upload_to_redshift(df, dest=staging_table)

            cursor.execute("BEGIN;")
            start_time = time.time()

            if clear_dest_table:
                print("Truncating destination table...")
                #cursor.execute(f"DELETE FROM {dest_table};")
                cursor.execute(f"TRUNCATE TABLE {dest_table};")
            else:
                print("Deleting matching rows from main table...")
                if has_nulls:
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col} OR ({dest_table}.{col} IS NULL AND staging.{col} IS NULL))" for col in upsert_columns])
                else:
                    where_condition = " AND ".join([f"({dest_table}.{col} = staging.{col})" for col in upsert_columns])
                delete_query = f"DELETE FROM {dest_table} USING {staging_table} AS staging WHERE {where_condition};"
                cursor.execute(delete_query)
                print(f"Time taken: {int(time.time() - start_time)} seconds")

            print("Inserting new rows from staging table into main table...")
            insert_query = f"INSERT INTO {dest_table} SELECT * FROM {staging_table};"
            cursor.execute(insert_query)
            print(f"Time taken: {int(time.time() - start_time)} seconds")

            cursor.execute("COMMIT;")

        except Exception as e:
            print(f"An error occurred: {str(e)}. Rolling back transaction...")
            cursor.execute("ROLLBACK;")
            raise
        finally:
            try:
                start_time = time.time()
                print("Dropping staging table...")
                drop_staging_query = f"DROP TABLE IF EXISTS {staging_table};"
                cursor.execute(drop_staging_query)
                print(f"Time taken: {int(time.time() - start_time)} seconds")
            except Exception as e:
                print(f"An error occurred during staging table cleanup: {e}")

        print("Upsert to Redshift completed successfully.")


    def delete_and_insert_to_redshift(self, df, dest_table, filter_cond):
        """
        Deletes data from the specified destination table in Redshift based on the filter condition,
        and then inserts new data from the DataFrame into the table.

        Parameters:
        - df: pandas DataFrame to be inserted.
        - dest_table: Redshift destination table, including schema, e.g., 'schema_name.table_name'.
        - filter_cond: Condition to filter the data for deletion, e.g., "create_date >= CURRENT_DATE - 10".
        """
        cursor = self.redshift_c.cursor()
        try:
            # Deleting data from Redshift table based on filter_cond
            cursor.execute("BEGIN;")  # Add transaction start
            delete_query = f"DELETE FROM {dest_table} WHERE {filter_cond};"
            cursor.execute(delete_query)
            print("Data deletion completed.")
            self.upload_to_redshift(df, dest_table)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            print(f"An error occurred: {e}")
            raise # Reraising the exception for external handling if necessary
        finally:
            cursor.close()