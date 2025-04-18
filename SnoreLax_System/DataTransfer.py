import pymssql
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

    # This class contains methods to save data to SQL database and Azure Blob Storage
    # Credentials and connection strings have been removed due to security concerns

    # The saved data and recordings are then used on the web application
   
class DataTransfer():

        # Save data to SQL database
    def save_to_database(filename, type, duration):
        conn = pymssql.connect(
        server='SERVER',
        user='USERNAME',
        password='PASSWORD',
        database='DATABASE',
        as_dict=True
        )

        rec_url = ""
        if (type == "Talking"):
            rec_url = DataTransfer.save_recording_to_blob_storage(filename)

        currentDate = datetime.now().strftime("%Y-%m-%d")
        query = f"('{type}','{currentDate}', '{duration}', '{rec_url}');"
        cursor = conn.cursor()

        SQL_QUERY = f"""
            INSERT INTO sound_events (Type, Datetime, Duration_seconds, Rec_Link) VALUES
            {query}
            """

        cursor.execute(SQL_QUERY)
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Recording {filename} has been fully processed.\n\n")


        # Saves Talking recordings to Azure Blob Storage
    def save_recording_to_blob_storage(filename):
        conn_string = "CONNECTION_STRING"
        blob_service_client = BlobServiceClient.from_connection_string(conn_string)
        container_name = "sleeprecordings"
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{filename}")
        with open(filename, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            print(f"\nUploaded {filename} to Azure Blob Storage.\n\n")
        
        rec_url = f"https://stsnorelax.blob.core.windows.net/{container_name}/{filename}"
        
        return rec_url