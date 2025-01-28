"""API Gateway event resolvers for Lambda functions.

Provides REST and HTTP API Gateway event handling with routing capabilities.
"""

from typing import Any, Callable, Optional, TypeVar, Union, Generic
from enum import Enum
import re
from http import HTTPStatus


from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse, LambdaEvent
from chainsaws.aws.lambda_client.types.events.api_gateway_proxy import (
    APIGatewayProxyV1Event,
    APIGatewayProxyV2Event,
)
from chainsaws.aws.lambda_client.event_handler.middleware import MiddlewareManager, Middleware

T = TypeVar("T", APIGatewayProxyV1Event, APIGatewayProxyV2Event)
RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Any])


class HttpMethod(str, Enum):
    """HTTP methods supported by API Gateway."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class Route:
    """API Gateway route definition."""

    __slots__ = ('path', 'method', 'handler', 'cors', '_pattern')

    def __init__(
        self,
        path: str,
        method: HttpMethod,
        handler: Callable[..., Any],
        cors: bool = True
    ):
        """Initialize route with lazy pattern compilation."""
        self.path = path
        self.method = method
        self.handler = handler
        self.cors = cors
        self._pattern = None

    @property
    def pattern(self) -> re.Pattern:
        """Lazy compile and cache the route pattern."""
        if self._pattern is None:
            pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                             r'(?P<\1>[^/]+)', self.path)
            self._pattern = re.compile(f'^{pattern}$')
        return self._pattern

    def match(self, path: str) -> Optional[re.Match]:
        """Match a path against this route's pattern."""
        return self.pattern.match(path)


class BaseResolver(Generic[T]):
    """Base resolver for API Gateway events."""

    def __init__(self, base_path: str = ""):
        """Initialize resolver."""
        self.routes: list[Route] = []
        self.middleware_manager: MiddlewareManager[T] = MiddlewareManager()
        self.base_path = self._normalize_base_path(base_path)
        self.routers: list["Router"] = []

    def _normalize_base_path(self, path: str) -> str:
        """Normalize base path to always start with / and never end with /.

        Args:
            path: Base path to normalize

        Returns:
            Normalized base path
        """
        if not path:
            return ""
        return "/" + path.strip("/")

    def _normalize_path(self, path: str) -> str:
        """Normalize path with base path.

        Args:
            path: Route path to normalize

        Returns:
            Full normalized path including base path
        """
        # 항상 /로 시작하고 /로 끝나지 않도록 정규화
        path = "/" + path.strip("/")

        if not self.base_path:
            return path

        # base_path가 있는 경우 결합
        return self.base_path + path

    def include_router(
        self,
        router: "Router",
        prefix: str = "",
        tags: list[str] | None = None
    ) -> None:
        """Include a router with optional prefix and tags."""
        if prefix:
            router.base_path = self._normalize_base_path(prefix)
        if tags:
            router.tags.extend(tags)

        router.parent = self
        self.routers.append(router)

        # Add router's routes to resolver
        for route in router.routes:
            full_path = router._get_full_path(route.path)
            new_route = Route(
                path=full_path,
                method=route.method,
                handler=route.handler,
                cors=route.cors
            )
            self.routes.append(new_route)

        # Add router's middleware
        for middleware in router.middleware_manager.middleware:
            self.add_middleware(middleware)

    def add_middleware(self, middleware: Middleware) -> None:
        """Add a middleware to the resolver."""
        self.middleware_manager.add_middleware(middleware)

    def middleware(self, middleware_func: Middleware) -> Middleware:
        """Decorator to add a middleware."""
        self.add_middleware(middleware_func)
        return middleware_func

    def add_route(
        self,
        path: str,
        method: Union[str, HttpMethod],
        cors: bool = True,
        status_code: Union[int, HTTPStatus] = HTTPStatus.OK
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator to add a route handler."""
        if isinstance(method, str):
            method = HttpMethod(method.upper())

        # HTTPStatus를 int로 변환
        status_code_value = status_code.value if isinstance(status_code, HTTPStatus) else status_code

        normalized_path = self._normalize_path(path)

        def decorator(handler: RouteHandler) -> RouteHandler:
            async def wrapped_handler(*args, **kwargs):
                result = await handler(*args, **kwargs) if hasattr(handler, '__await__') else handler(*args, **kwargs)
                if not isinstance(result, dict) or "statusCode" not in result:
                    return LambdaResponse.create(result, status_code=status_code_value)
                return result
            
            route = Route(
                path=normalized_path,
                method=method,
                handler=wrapped_handler,
                cors=cors
            )
            self.routes.append(route)
            return handler
        return decorator

    def get(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.OK) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for GET method routes."""
        return self.add_route(path, HttpMethod.GET, cors, status_code)

    def post(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.CREATED) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for POST method routes."""
        return self.add_route(path, HttpMethod.POST, cors, status_code)

    def put(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.OK) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PUT method routes."""
        return self.add_route(path, HttpMethod.PUT, cors, status_code)

    def delete(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.NO_CONTENT) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for DELETE method routes."""
        return self.add_route(path, HttpMethod.DELETE, cors, status_code)

    def patch(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.OK) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PATCH method routes."""
        return self.add_route(path, HttpMethod.PATCH, cors, status_code)

    def head(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for HEAD method routes."""
        return self.add_route(path, HttpMethod.HEAD, cors)

    def options(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for OPTIONS method routes."""
        return self.add_route(path, HttpMethod.OPTIONS, cors)

    def _find_route(self, path: str, method: str) -> Optional[Route]:
        """Find matching route for path and method."""
        for route in self.routes:
            if route.method.value == method.upper():
                match = route.match(path)
                if match:
                    return route
        return None

    def resolve(self, event: T, context: Any = None) -> dict[str, Any]:
        """Resolve API Gateway event to handler response."""
        raise NotImplementedError


class Router(BaseResolver[T]):
    """Router for modular route handling."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None):
        """Initialize router."""
        super().__init__(base_path=prefix)
        self.tags = tags or []
        self.parent: Optional[BaseResolver] = None

    def _get_full_path(self, path: str) -> str:
        """Get full path including all parent base paths."""
        # 현재 라우터의 base_path와 결합
        full_path = self._normalize_path(path)

        # 부모 라우터가 있다면 부모의 base_path도 포함
        if self.parent and self.parent.base_path:
            full_path = self.parent.base_path + full_path

        return full_path


class APIGatewayRestResolver(BaseResolver[APIGatewayProxyV1Event]):
    """Resolver for REST API Gateway events."""

    def resolve(self, event: APIGatewayProxyV1Event, context: Any = None) -> dict[str, Any]:
        """Resolve REST API Gateway event to handler response."""
        # Validate event structure
        if event.get('version', '1.0') != '1.0':
            return LambdaResponse.create(
                {"message":
                    "Invalid API Gateway version. Expected REST API (v1)"},
                status_code=400
            )

        lambda_event = LambdaEvent.from_dict(event)

        path = event.get('path', '')
        method = event.get('httpMethod', '')

        route = self._find_route(path, method)
        if not route:
            return LambdaResponse.create(
                {"message": "Not Found"},
                status_code=404
            )

        try:
            # Extract path parameters
            pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                             r'(?P<\1>[^/]+)', route.path)
            match = re.match(f'^{pattern}$', path)
            path_params = match.groupdict() if match else {}

            # Prepare kwargs for handler
            kwargs = {
                "event": lambda_event,
                "context": context,
                "path_parameters": path_params,
                "query_parameters": event.get('queryStringParameters', {}),
                "headers": event.get('headers', {}),
                "body": lambda_event.get_json_body()
            }

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    **{**kwargs, "event": e, "context": c})
            )
            result = handler(event, context)

            # If result is already a dict with statusCode, assume it's properly formatted
            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )


class APIGatewayHttpResolver(BaseResolver[APIGatewayProxyV2Event]):
    """Resolver for HTTP API Gateway events."""

    def resolve(self, event: APIGatewayProxyV2Event, context: Any = None) -> dict[str, Any]:
        """Resolve HTTP API Gateway event to handler response."""
        # Validate event structure
        if event.get('version', '2.0') != '2.0':
            return LambdaResponse.create(
                {"message":
                    "Invalid API Gateway version. Expected HTTP API (v2)"},
                status_code=400
            )

        lambda_event = LambdaEvent.from_dict(event)

        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get(
            'http', {}).get('method', '')

        route = self._find_route(path, method)
        if not route:
            return LambdaResponse.create(
                {"message": "Not Found"},
                status_code=404
            )

        try:
            # Extract path parameters
            pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                             r'(?P<\1>[^/]+)', route.path)
            match = re.match(f'^{pattern}$', path)
            path_params = match.groupdict() if match else {}

            # Prepare kwargs for handler
            kwargs = {
                "event": lambda_event,
                "context": context,
                "path_parameters": path_params,
                "query_parameters": event.get('queryStringParameters', {}),
                "headers": event.get('headers', {}),
                "body": lambda_event.get_json_body()
            }

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    **{**kwargs, "event": e, "context": c})
            )
            result = handler(event, context)

            # If result is already a dict with statusCode, assume it's properly formatted
            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )
