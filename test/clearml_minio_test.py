import os
from pathlib import Path
from clearml import Task

# Ensure agent installs S3 driver on remote execution
Task.add_requirements("clearml[s3]")
Task.add_requirements("boto3")


def upload_test_artifacts(
    api_host: str = "https://api-clearml.itdevops.id.vn",
    access_key: str = "Q5JTQYI12NHB3YT80UAF3GW6U5Q3WS",
    secret_key: str = "CM1-VzzdmIA12nVIAtrRYkHpDcN5b5OcdCRrD_s0_q6rrtA_UwC-OwH0M3ToBEw6LdQ",
    project_name: str = "MinIO-Test",
    task_name: str = "upload-artifact",
    use_agent: bool = True,
) -> None:
    os.environ.setdefault("CLEARML_API_HOST", api_host)
    os.environ.setdefault("CLEARML_API_ACCESS_KEY", access_key)
    os.environ.setdefault("CLEARML_API_SECRET_KEY", secret_key)
    os.environ.setdefault("CLEARML_WEB_HOST", "https://clearml.itdevops.id.vn")
    # Lưu ý: Direct S3 được cấu hình trên agent (env + clearml.conf). Script không set S3 env để tránh xung đột.

    # Use two existing files under test/ directory
    base_dir = Path(__file__).parent
    test_file_1 = base_dir / "error_messages.json"
    test_file_2 = base_dir / "404-not-found.svg"

    task = Task.init(project_name=project_name, task_name=task_name)
    if use_agent and task.execute_remotely(queue_name="default", exit_process=True):
        return

    task.upload_artifact("test_error_messages_json", artifact_object=str(test_file_1))
    task.upload_artifact("test_404_not_found_svg", artifact_object=str(test_file_2))
    print("Uploaded artifacts (2 repo files)")

    # Nếu chạy local (use_agent=False), có thể xác minh trực tiếp bằng boto3 tại đây.
    if not use_agent:
        try:
            import boto3  # type: ignore

            s3 = boto3.client(
                "s3",
                endpoint_url="https://minio.itdevops.id.vn",
                aws_access_key_id="dev-minioadmin",
                aws_secret_access_key="dev-minioadmin",
                region_name="us-east-1",
            )
            resp = s3.list_objects_v2(Bucket="clearml", Prefix=f"{project_name}/")
            keys = [obj["Key"] for obj in resp.get("Contents", [])]
            print("MinIO objects:", keys)
        except Exception as ex:
            print("MinIO verification failed:", ex)


def main() -> None:
    upload_test_artifacts()


if __name__ == "__main__":
    main()


