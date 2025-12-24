import logging
import json
from pathlib import Path
from observability.logging import get_logger, log_event

try:
    from azure.storage.blob import BlobServiceClient
    from azure.core.exceptions import ResourceExistsError
except ImportError:
    # Fallback for environments where azure-storage-blob isn't installed
    BlobServiceClient = None

logger = get_logger(__name__)

class AzureRunStorage:
    def __init__(self, connection_string=None, container_name="simulation-runs"):
        self.connection_string = connection_string or os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = container_name
        self.client = None
        self.container_client = None
        
        if self.connection_string and BlobServiceClient:
            try:
                self.client = BlobServiceClient.from_connection_string(self.connection_string)
                self.container_client = self.client.get_container_client(self.container_name)
                # Ensure container exists
                try:
                    self.container_client.create_container()
                except ResourceExistsError:
                    pass
                logger.info(f"Connected to Azure Blob Storage container: {self.container_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Storage: {e}")
                self.client = None
        else:
            if not BlobServiceClient:
                logger.warning("azure-storage-blob library not installed. Cloud storage disabled.")
            else:
                logger.warning("AZURE_STORAGE_CONNECTION_STRING not found. Cloud storage disabled (local mode only).")

    def is_enabled(self):
        return self.client is not None

    def upload_run(self, run_id, source_dir):
        """
        Uploads all files in source_dir to runs/{run_id}/...
        """
        if not self.is_enabled():
            logger.info("Cloud storage disabled; skipping upload.")
            return False

        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Source directory {source_dir} does not exist")
            return False

        logger.info(f"Uploading run {run_id} to Azure...")
        upload_count = 0
        
        try:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    # Calculate relative path for blob name
                    relative_path = file_path.relative_to(source_path)
                    blob_name = f"runs/{run_id}/{relative_path}"
                    
                    with open(file_path, "rb") as data:
                        self.container_client.upload_blob(name=blob_name, data=data, overwrite=True)
                    upload_count += 1
            
            logger.info(f"Successfully uploaded {upload_count} files for run {run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload run {run_id}: {e}")
            return False

    def download_run(self, run_id, dest_dir):
        """
        Downloads all files for a run_id to dest_dir
        """
        if not self.is_enabled():
            return False
            
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        prefix = f"runs/{run_id}/"
        logger.info(f"Downloading run {run_id} from Azure...")
        
        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            count = 0
            for blob in blobs:
                blob_name = blob.name
                # Remove prefix to get local relative path
                relative_path = blob_name[len(prefix):]
                local_file_path = dest_path / relative_path
                
                # Create parent dirs
                local_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(local_file_path, "wb") as f:
                    data = self.container_client.download_blob(blob.name).readall()
                    f.write(data)
                count += 1
                
            logger.info(f"Downloaded {count} files for run {run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download run {run_id}: {e}")
            return False
