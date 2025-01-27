from botocore.client import Config
import os

endpoint = 'https://tos-s3-cn-beijing.volces.com'
ak = 'AKLTYzgzOGY2NzFjZTlmNDE0MmIyMmZiOGY4YTIzYWQ5MWU'
sk = 'WlRnM05XSTVaR1E0T1RnNE5EVmpZMkU1WlRWak4ySTJOR05tWTJZNU16SQ=='

import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(local_file_path, bucket_name, s3_key):
    """
    使用 boto3 的 upload_file 方法上传文件到 S3
    :param local_file_path: 本地文件路径
    :param bucket_name: S3 存储桶名称
    :param s3_key: 上传到 S3 的目标键（Key）
    """
    try:
        # 创建 S3 客户端
        s3 = boto3.client('s3',
                          endpoint_url=endpoint,
                          aws_access_key_id=ak,
                          aws_secret_access_key=sk,
                          config=Config(
                              s3={
                                  'addressing_style': 'virtual',
                                  'payload_signing_enabled': False  # 禁用签名计算
                              },
                              signature_version='s3v4',
                              # connect_timeout=2,
                              # read_timeout=5,
                              retries={
                                  'max_attempts': 3,
                                  'mode': 'standard'  # 设置为自适应模式
                              }
                          )
                          )

        # 上传文件
        s3.upload_file(local_file_path, bucket_name, s3_key)
        print(f"文件 '{local_file_path}' 成功上传到 '{bucket_name}/{s3_key}'")

    except NoCredentialsError:
        print("AWS 凭证未配置或无效")
    except Exception as e:
        print(f"上传失败: {str(e)}")


if __name__ == "__main__":
    # 配置参数
    bucket = "qc-service-beijing"  # 替换为你的 S3 存储桶名称
    key = "non-empty.txt"        # S3 目标路径（Key）

    os.remove(key)
    # 第一次上传：空文件
    with open("empty.txt", "w") as f:
        f.write("")  # 创建一个空文件
    upload_to_s3("./empty.txt", bucket, key)

    # 第二次上传：非空文件（覆盖同名文件）
    with open("empty.txt", "w") as f:
        f.write("This is a non-empty file.")
    upload_to_s3("./empty.txt", bucket, key)