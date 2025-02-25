import boto3
import logging
import json
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
import uuid
from typing import Dict, Any, List, Optional
from .config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, folder: str = "media") -> Dict[str, Any]:
        """Upload a file to S3 bucket"""
        try:
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            object_name = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            # Read file content
            content = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Body=content,
                Bucket=self.bucket_name,
                Key=object_name,
                ContentType=file.content_type
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
            return {
                "file_url": url,
                "content_type": file.content_type,
                "file_size": len(content)
            }
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
    
    def delete_file(self, file_url: str) -> bool:
        """Delete a file from S3 bucket"""
        try:
            # Extract key from URL
            object_key = file_url.split(f"{self.bucket_name}.s3.amazonaws.com/")[1]
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False

class DynamoDBService:
    def __init__(self):
        self.dynamo_client = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        )
        self.view_counts_table = self.dynamo_client.Table('post_view_counts')
        self.user_activity_table = self.dynamo_client.Table('user_activity')

    def increment_view_count(self, post_id: int) -> int:
        """Increment and return the view count for a post"""
        try:
            response = self.view_counts_table.update_item(
                Key={'post_id': str(post_id)},
                UpdateExpression="ADD view_count :val",
                ExpressionAttributeValues={':val': 1},
                ReturnValues="UPDATED_NEW"
            )
            return int(response.get('Attributes', {}).get('view_count', 0))
        except Exception as e:
            logger.error(f"DynamoDB error: {e}")
            return 0
    
    def log_user_activity(self, user_id: int, activity_type: str, metadata: Dict[str, Any]) -> bool:
        """Log user activity in DynamoDB"""
        try:
            self.user_activity_table.put_item(
                Item={
                    'user_id': str(user_id),
                    'timestamp': int(datetime.now().timestamp()),
                    'activity_type': activity_type,
                    'metadata': json.dumps(metadata)
                }
            )
            return True
        except Exception as e:
            logger.error(f"DynamoDB log error: {e}")
            return False

class SQSService:
    def __init__(self):
        self.sqs_client = boto3.client(
            'sqs',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value()
        )
        self.notification_queue_url = "https://sqs.{}.amazonaws.com/123456789012/blog-notifications".format(settings.AWS_REGION)
    
    def send_notification(self, notification_type: str, payload: Dict[str, Any]) -> bool:
        """Send notification to SQS queue"""
        try:
            message_body = json.dumps({
                "type": notification_type,
                "timestamp": int(datetime.now().timestamp()),
                "payload": payload
            })
            
            self.sqs_client.send_message(
                QueueUrl=self.notification_queue_url,
                MessageBody=message_body
            )
            return True
        except Exception as e:
            logger.error(f"SQS error: {e}")
            return False

# Initialize AWS services
s3_service = S3Service()
dynamodb_service = DynamoDBService()
sqs_service = SQSService()
