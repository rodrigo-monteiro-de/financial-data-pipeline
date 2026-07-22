from pathlib import Path
import os

from s3_client import get_s3_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data_lake" / "bronze"

BUCKET_NAME = "financial-data-pipeline-rmonteiro-dev"
#BUCKET_NAME = os.getenv("AWS_S3_BUCKET")

def upload_directory(directory:Path) ->None:

    s3 = get_s3_client()

    txt_files = list(directory.glob("*.txt"))

    if not txt_files:
        print("Txt file not found")
        return 

    for file in txt_files:
        s3_key = f"bronze/{file.name}"

        print(f"Sending file {file.name}...")

        s3.upload_file(
            Filename = str(file),
            Bucket = BUCKET_NAME,
            Key = s3_key,
        )

        print(f"Uploaded: {file.name}")

if __name__ == "__main__":
    upload_directory(
        Path("data_lake/bronze")
    )