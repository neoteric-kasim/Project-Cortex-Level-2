import os
from azure.storage.filedatalake import DataLakeServiceClient
from datetime import datetime


class ADLSService:
    def __init__(self):
        self.connection_string = os.getenv("ADLS_CONNECTION_STRING")
        self.file_system_name = os.getenv("FILE_SYSTEM_NAME")

        # ✅ Fail early if env not loaded
        if not self.connection_string:
            raise ValueError("ADLS_CONNECTION_STRING is not set")

        if not self.file_system_name:
            raise ValueError("FILE_SYSTEM_NAME is not set")

        self.service_client = DataLakeServiceClient.from_connection_string(
            self.connection_string
        )

        self.file_system_client = self.service_client.get_file_system_client(
            self.file_system_name
        )

    def upload_file(self, file_name: str, file_content: bytes):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_path = f"raw/uploads/{timestamp}_{file_name}"

        file_client = self.file_system_client.get_file_client(file_path)

        file_client.create_file()
        file_client.append_data(file_content, offset=0, length=len(file_content))
        file_client.flush_data(len(file_content))

        return file_path

    def list_files(self, directory: str):
        paths = self.file_system_client.get_paths(path=directory)
        return [p.name for p in paths]