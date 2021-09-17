import boto3


class SQS():

    def __init__(self, queue_name, *args, **kwargs):
        
        self.sqs = boto3.client('sqs')

        list_response = self.sqs.list_queues(QueueNamePrefix=queue_name)

        queue_urls = list_response.get('QueueUrls')
        
        if queue_urls:
            self.queue_url = queue_urls[0]
            
        else:
            create_response = self.sqs.create_queue(QueueName=queue_name)
            self.queue_url = create_response['QueueUrl']
            
        print(f"QUEUE list_response {list_response}")
        print(f"QUEUE self.queue_url {self.queue_url}")
        

    def send_message(self, message_body):

        send_response = self.sqs.send_message(QueueUrl=self.queue_url,
                                              MessageBody=message_body)
        
        print(f"QUEUE send_response {send_response}")


    def receive_message(self):

        receive_response = self.sqs.receive_message(QueueUrl=self.queue_url,
                                                    MaxNumberOfMessages=1,
                                                    VisibilityTimeout=1)
        
        messages = receive_response.get('Messages')
        
        print(f"QUEUE receive_response {receive_response}")
        print(f"QUEUE messages {messages}")
        
        if messages:
            
            message = messages[0]
            message_body = message.get('Body')
            receipt_handle = message['ReceiptHandle']
            delete_response = self.sqs.delete_message(QueueUrl=self.queue_url,
                                                      ReceiptHandle=receipt_handle)
                                             
            print(f"QUEUE message {message}")
            print(f"QUEUE message_body {message_body}")
            print(f"QUEUE receipt_handle {receipt_handle}")                                    
            print(f"QUEUE delete_response {delete_response}")
            
            return message_body


    def purge(self):
        
        purge_response = self.sqs.purge_queue(QueueUrl=self.queue_url)
    
        print(f"QUEUE purge_response {purge_response}")
    
    

def test():

    queue = SQS('m1-task-queue')
    
    queue.send_message('Hello quokka!')
    
    message = queue.receive_message()
    
    print(f"QUEUE test message {message}")
    
    queue.purge()
    
    # queue = SQS('m1-result-queue')
    

# test()