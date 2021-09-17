import boto3


TASK_QUEUE_NAME = 'm1-task-queue'


sqs = boto3.client('sqs')


list_response = sqs.list_queues(QueueNamePrefix=TASK_QUEUE_NAME)

print(f"QUEUE list_response {list_response}")


queue_urls = list_response.get('QueueUrls')

if queue_urls:
    queue_url = queue_urls[0]
    
else:
    create_response = sqs.create_queue(QueueName='m1-task-queue')
    queue_url = create_response['QueueUrl']

print(f"QUEUE queue_url {queue_url}")



receive_response = sqs.receive_message(QueueUrl=queue_url,
                                       MaxNumberOfMessages=1,
                                       VisibilityTimeout=1)

messages = receive_response.get('Messages')

print(f"QUEUE receive_response {receive_response}")
print(f"QUEUE messages {messages}")

if messages:
    
    message = messages[0]
    receipt_handle = message['ReceiptHandle']
    delete_response = sqs.delete_message(QueueUrl=queue_url,
                                         ReceiptHandle=receipt_handle)
                                     
    print(f"QUEUE message {message}")
    print(f"QUEUE receipt_handle {receipt_handle}")                                    
    print(f"QUEUE delete_response {delete_response}")