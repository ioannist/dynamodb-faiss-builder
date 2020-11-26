import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('bc-content_group-contents')

def scan_faiss_pending():
    
    scan_kwargs = {
        'IndexName': "faissPending-index" # sparse index of faiss pending entries
    }

    faiss_pending_entries = []
    done = False
    start_key = None
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        faiss_pending_entries.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None
    
    return faiss_pending_entries

def update_content_vec(content_group: str, content_id: str, vec: str, faiss_id: int):
    table.update_item(
        Key={
            'content_group': content_group,
            'content_id': content_id
        },
        UpdateExpression='SET vec_content = :vec_content, faiss_id_content = :faiss_id',
        ExpressionAttributeValues={
            ':vec_content': vec,
            ':faiss_id': faiss_id
        }
    )

