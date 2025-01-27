import os
import json
import asyncio
import boto3
from typing import Any
from botocore.config import Config

class KimtraceSQSClient:
    @staticmethod
    def get_config() -> dict:
        return {
            "region": os.getenv("KIMTRACE_REGION", "RegionNotSet"),
            "access_key_id": os.getenv("KIMTRACE_ACCESS_KEY_ID", "AccessKeyIdNotSet"),
            "secret_access_key": os.getenv("KIMTRACE_SECRET_ACCESS_KEY", "SecretAccessKeyNotSet"),
            "queue_url": os.getenv("KIMTRACE_SQS_URL", "QueueUrlNotSet")
        }

    @staticmethod
    def get_sqs_client():
        config = KimtraceSQSClient.get_config()
        return boto3.client(
            'sqs',
            region_name=config["region"],
            aws_access_key_id=config["access_key_id"],
            aws_secret_access_key=config["secret_access_key"],
            config=Config(connect_timeout=1, read_timeout=1, retries={'max_attempts': 0})
        )

    @staticmethod
    async def send(msg: Any) -> None:
        timeout_ms = 10
        
        async def send_message():
            try:
                msg_dict = msg.to_dict() if hasattr(msg, 'to_dict') else msg
                formatted_msg = json.dumps(msg_dict, indent=2)
                config = KimtraceSQSClient.get_config()
                client = KimtraceSQSClient.get_sqs_client()
                
                # Use asyncio.to_thread to run the blocking SQS operation in a thread
                await asyncio.to_thread(
                    client.send_message,
                    QueueUrl=config["queue_url"],
                    MessageBody=formatted_msg
                )
            except Exception:
                pass

        try:
            # Race between the send operation and timeout
            await asyncio.wait_for(
                send_message(),
                timeout=timeout_ms/1000
            )
        except asyncio.TimeoutError:
            # Timeout occurred, but we don't care about the response (fire and forget)
            pass