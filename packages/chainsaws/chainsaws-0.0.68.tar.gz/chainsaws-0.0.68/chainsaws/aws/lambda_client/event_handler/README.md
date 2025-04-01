# AWS Lambda Handler Utilities

A collection of utilities for AWS Lambda handlers that provides structured request handling, error management, and response formatting.

## Features

- **Simplified Lambda Handler Development**

  - Automatic request parsing and validation
  - Standardized response formatting
  - Comprehensive error handling
  - Built-in logging and monitoring support

- **Type Safety**

  - Full type hints support
  - Dataclass validation
  - IDE-friendly development

- **Error Management**
  - Structured error responses
  - External error notification support
  - Configurable error tracking
  - Traceback management

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.utils.handler_utils import aws_lambda_handler, get_body

@aws_lambda_handler()
def handler(event, context):
    # Automatically parses and validates the request body
    body = get_body(event)

    return {
        "message": "Success",
        "data": body
    }
```

## Core Components

### Event Model (LambdaEvent)

The `LambdaEvent` class provides a structured way to handle AWS Lambda event inputs:

```python
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class LambdaEvent:
    body: Optional[str]                    # Request body (raw string)
    headers: Dict[str, str]                # HTTP headers
    requestContext: RequestContext         # Request context with identity info

    # Additional fields are handled by __init__
    def __init__(self, **kwargs):
        self.body = kwargs.get('body')
        self.headers = kwargs.get('headers', {})
        self.requestContext = kwargs.get('requestContext')
        self._extra = {k: v for k, v in kwargs.items()
                      if k not in ['body', 'headers', 'requestContext']}
```

Example usage:

```python
@aws_lambda_handler()
def handler(event, context):
    # Parse event
    event_data = LambdaEvent(**event)

    # Access event data
    body = event_data.get_json_body()      # Parsed JSON body
    headers = event_data.headers           # Request headers
    source_ip = event_data.requestContext.get_source_ip()  # Client IP

    return {"data": process_request(body)}
```

### Response Model (LambdaResponse)

The `LambdaResponse` class handles response formatting with proper headers and structure:

```python
from dataclasses import dataclass

@dataclass
class LambdaResponse:
    statusCode: int = 200                  # HTTP status code
    headers: ResponseHeaders               # Response headers with CORS
    body: str                             # Response body (JSON string)
    isBase64Encoded: bool = False         # Base64 encoding flag
```

Response creation:

```python
# Automatic creation via decorator
@aws_lambda_handler()
def handler(event, context):
    return {
        "data": "success",                 # Will be automatically formatted
        "meta": {"count": 42}
    }

    # Manual creation
    response = LambdaResponse.create(
        body={"message": "success"},
        content_type='application/json',
        status_code=200,
        charset='UTF-8'
    )
```

### WebSocket Support

The library provides comprehensive support for WebSocket APIs through API Gateway, including connection management and event handling.

#### Connection Management

The `APIGatewayWSConnectionManager` class provides connection state management using DynamoDB:

```python
from chainsaws.aws.lambda_client.event_handler.websocket_connection import APIGatewayWSConnectionManager
from chainsaws.aws.lambda_client.event_handler.websocket import WebSocketResolver

# Initialize connection manager
connection_manager = APIGatewayWSConnectionManager(
    table_name='websocket-connections',  # DynamoDB table name
    partition='websocket_status',        # Partition for connection records
    connection_ttl=7200                  # Connection TTL in seconds (2 hours)
)

# Initialize resolver
resolver = WebSocketResolver()
```

##### Connection Lifecycle

1. **Table Initialization**:
```python
# Initialize DynamoDB table (run once during deployment)
async def init_resources():
    await connection_manager.init_table()
```

2. **Connection Handling**:
```python
@resolver.on_connect()
async def handle_connect(event, context, connection_id):
    # Store client information
    client_data = {
        "user_agent": event.get("headers", {}).get("User-Agent"),
        "source_ip": event["requestContext"]["identity"]["sourceIp"]
    }
    return await connection_manager.connect(connection_id, client_data)

@resolver.on_disconnect()
async def handle_disconnect(event, context, connection_id):
    return await connection_manager.disconnect(connection_id)
```

3. **Connection Tracking**:
```python
@resolver.middleware
class ConnectionTrackingMiddleware(Middleware):
    async def __call__(self, event, context, next_handler):
        connection_id = event["requestContext"]["connectionId"]
        route_key = event["requestContext"]["routeKey"]
        
        # Skip for $connect events
        if route_key != "$connect":
            await connection_manager.update_last_seen(connection_id)
        
        return await next_handler(event, context)
```

4. **Message Handling with Connection State**:
```python
@resolver.on_message("message")
async def handle_message(event, context, connection_id, body):
    # Verify connection exists
    connection = await connection_manager.get_connection(connection_id)
    if not connection:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid connection"})
        }
    
    # Access connection metadata
    client_info = connection.client_data
    print(f"Message from {client_info['source_ip']}")
    
    return {"message": "Processed"}
```

##### DynamoDB Schema

The connection manager uses the following DynamoDB structure:

- **Table Name**: (configurable)
- **Partition Key**: `connection_id` (String)
- **Sort Key**: `_crt` (Number, creation timestamp)
- **TTL Attribute**: `_ttl`

Additional attributes:
- `status`: Connection status
- `connected_at`: Connection timestamp
- `last_seen`: Last activity timestamp
- `client_data`: Client metadata (optional)

##### Error Handling

The connection manager provides comprehensive error handling:

```python
try:
    await connection_manager.connect(connection_id)
except DynamoDBError as e:
    logger.error(f"Connection failed: {e}")
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Internal error"})
    }
```

##### Configuration

Required IAM permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/websocket-connections"
        }
    ]
}
```

Environment variables:
```bash
DYNAMODB_TABLE=websocket-connections  # DynamoDB table name
```

##### Best Practices

1. **Connection Initialization**:
   - Initialize the table before first use
   - Use meaningful partition names
   - Set appropriate TTL values

2. **Error Handling**:
   - Always handle DynamoDBError exceptions
   - Log errors for debugging
   - Return appropriate error responses

3. **Performance**:
   - Use the connection tracking middleware
   - Implement connection cleanup
   - Monitor table capacity

4. **Security**:
   - Validate client data
   - Implement authentication
   - Use secure WebSocket protocols

##### Complete Example

```python
import os
from chainsaws.aws.lambda_client.event_handler.websocket import WebSocketResolver
from chainsaws.aws.lambda_client.event_handler.websocket_connection import APIGatewayWSConnectionManager

# Initialize managers
connection_manager = APIGatewayWSConnectionManager(
    table_name=os.environ['DYNAMODB_TABLE'],
    partition='websocket_status'
)
resolver = WebSocketResolver()

# Connection tracking
@resolver.middleware
class ConnectionTrackingMiddleware(Middleware):
    async def __call__(self, event, context, next_handler):
        if event["requestContext"]["routeKey"] != "$connect":
            await connection_manager.update_last_seen(
                event["requestContext"]["connectionId"]
            )
        return await next_handler(event, context)

# Connection handlers
@resolver.on_connect()
async def handle_connect(event, context, connection_id):
    return await connection_manager.connect(
        connection_id,
        client_data={"ip": event["requestContext"]["identity"]["sourceIp"]}
    )

@resolver.on_disconnect()
async def handle_disconnect(event, context, connection_id):
    return await connection_manager.disconnect(connection_id)

# Message handlers
@resolver.on_message("message")
async def handle_message(event, context, connection_id, body):
    connection = await connection_manager.get_connection(connection_id)
    if not connection:
        return {"statusCode": 400, "message": "Invalid connection"}
    
    return {
        "message": "Message received",
        "client": connection.client_data
    }

# Lambda handler
def handler(event, context):
    return resolver.resolve(event, context)
```

### Utility Functions

```python
from chainsaws.utils.handler_utils import get_body, get_headers, get_source_ip

# Get parsed JSON body
body = get_body(event)                     # Returns Dict[str, Any] or None

# Get request headers
headers = get_headers(event)               # Returns Dict[str, str]

# Get client IP
client_ip = get_source_ip(event)          # Returns str
```

## Response Format

### Successful Response

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": true,
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "rslt_cd": "S00000",
    "rslt_msg": "Call Success",
    "duration": 0.001,
    "data": {
      "your": "response data"
    }
  },
  "isBase64Encoded": false
}
```

### Error Response

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": true,
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "rslt_cd": "S99999",
    "rslt_msg": "Error message",
    "duration": 0.002,
    "traceback": "Error traceback..."
  },
  "isBase64Encoded": false
}
```

## Advanced Usage

### Custom Error Handling

```python
from chainsaws.utils.error_utils import AppError

def notify_slack(error_message: str):
    # Your error notification logic
    slack_client.post_message(error_message)

@aws_lambda_handler(error_receiver=notify_slack)
def handler(event, context):
    try:
        # Validate request
        body = get_body(event)
        if not body:
            raise AppError("B00001", "Missing request body")

        # Process request
        result = process_data(body)
        return {"data": result}

    except ValueError as e:
        raise AppError("B00002", str(e))
```

### Type Hints Support

```python
from typing import Dict, Any
from chainsaws.utils.handler_utils import LambdaEvent, LambdaResponse

def process_event(event_data: LambdaEvent) -> Dict[str, Any]:
    body = event_data.get_json_body()
    return {"processed": body}

def handler(event: Dict[str, Any], context: Any) -> LambdaResponse:
    event_data = LambdaEvent(**event)
    result = process_event(event_data)
    return {"data": result}
```

## Best Practices

1. **Use Type Validation**

   ```python
   from dataclasses import dataclass

   @dataclass
   class UserRequest:
       name: str
       age: int

   @aws_lambda_handler()
   def handler(event, context):
       body = get_body(event)
       user_data = UserRequest(**body)
       return {"user": user_data.to_dict()}
   ```

2. **Handle Different Content Types**

   ```python
   @aws_lambda_handler(content_type='application/xml')
   def handler(event, context):
       return {"data": "<root>XML response</root>"}
   ```

3. **Custom Error Handling**

   ```python
   @aws_lambda_handler(
       error_receiver=notify_slack,
       ignore_app_errors=[NOT_FOUND_ERROR]
   )
   def handler(event, context):
       try:
           return process_request(get_body(event))
       except ResourceNotFoundError:
           raise AppError("B00404", "Resource not found")
   ```

4. **Request Context Usage**
   ```python
   @aws_lambda_handler()
   def handler(event, context):
       event_data = LambdaEvent(**event)
       return {
           "client_ip": event_data.requestContext.get_source_ip(),
           "request_id": event_data.requestContext.request_id
       }
   ```
