
from typing import Any, Callable, List, Union
from .http.request import Request
from .http.response import NexioResponse
from .types import HTTPMethod
from .decorators import allowed_methods
from .routing import Router, Routes,WSRouter
import logging,traceback
from .structs import RouteParam
from .websockets import get_websocket_session
import traceback
allowed_methods_default = ['get','post','delete','put','patch','options']

from typing import Dict, Any
import json

def validate_params(params: Dict[str, Any], param_types: Dict[str, type]) -> bool:
    errors = []
    for param, expected_type in param_types.items():
        try:
            _param = expected_type(params[param])
        except Exception:
            _param = params[param]
        if param not in params:
            errors.append(f"Missing parameter: {param}")
        
       
        elif not isinstance(_param, expected_type):
            errors.append(f"Parameter '{param}' should be of type {expected_type.__name__}. Got {type(params[param]).__name__}.")
    
    if errors:
        return False, errors
    return True, []


class NexioApp:
    def __init__(self, 
                 config = None,
                 middlewares: list = None):
        self.config = config
        self.routes: List[Routes] = []
        self.ws_routes :List[Routes] = []
        self.http_middlewares: List = middlewares or []
        self.ws_middlewares: List =  []
        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.logger = logging.getLogger("nexio")

    def on_startup(self, handler: Callable) -> Callable:
        """Decorator to register startup handlers"""
        self.startup_handlers.append(handler)
        return handler

    def on_shutdown(self, handler: Callable) -> Callable:
        """Decorator to register shutdown handlers"""
        self.shutdown_handlers.append(handler)
        return handler

    async def startup(self) -> None:
        """Execute all startup handlers sequentially"""
        for handler in self.startup_handlers:
            await handler()

    async def shutdown(self) -> None:
        """Execute all shutdown handlers sequentially with error handling"""
        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                self.logger.error(f"Shutdown handler error: {str(e)}")

    async def handle_lifespan(self, receive: Callable, send: Callable) -> None:
        """Handle ASGI lifespan protocol events"""
        try:
            while True:
                message = await receive()
                
                if message["type"] == "lifespan.startup":
                    try:
                        await self.startup()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        self.logger.error(f"Startup error: {str(e)}")
                        await send({"type": "lifespan.startup.failed", "message": str(e)})
                        return
                
                elif message["type"] == "lifespan.shutdown":
                    try:
                        await self.shutdown()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
                    except Exception as e:
                        self.logger.error(f"Shutdown error: {str(e)}")
                        await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                        return

        except Exception as e:
            self.logger.error(f"Lifespan error: {str(e)}")
            if message["type"].startswith("lifespan.startup"):
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})
    def normalize_path(self,path: str) -> str:
        return path.rstrip("/").lower().replace("//", "/")
   
    
    async def execute_middleware_stack(self, 
                                     request: Request,
                                     response: NexioResponse, 
                                     handler: Callable = None) -> Any:
        """Execute middleware stack including the handler as the last 'middleware'."""
        async def default_handler(req,res :NexioResponse):
            return res.json({"error":"Not Found"},status_code=404)
        handler = handler or default_handler
        stack = self.http_middlewares.copy()

        # If we have a handler, add it to the stack
        if handler:
            stack.append(handler)

        index = -1 
        async def next_middleware():
            nonlocal index
            index += 1
            
            if index < len(stack):
                middleware = stack[index]
                if not response._body:
                    if index == len(stack) - 1:  # This is the handler
                        await middleware(request, response)
                    else:
                        await middleware(request, response, next_middleware)
                return

        await next_middleware()

    async def handle_http_request(self, scope: dict, receive: Callable, send: Callable) -> None:
        request = Request(scope, receive, send)
        response = NexioResponse()
        request.scope['config'] = self.config
       
        
        handler = None
        try:
            for route in self.routes:
                url = self.normalize_path(request.url.path)
                match = route.pattern.match(url)
                if match:
                    route.handler = allowed_methods(route.methods)(route.handler)
                    route_kwargs = match.groupdict()
                    handler_validator = getattr(route,"validator",None)
                    if handler_validator:
                        is_valid,errors = validate_params(route_kwargs,handler_validator)
                        if not is_valid:
                            response.json({"error":errors},status_code=422)
                            break
                    scope['route_params'] = RouteParam(route_kwargs)
                    
                    
                    if route.router_middleware and len(route.router_middleware) > 0:
                        self.http_middlewares.extend(route.router_middleware)
                    handler = lambda req, res: route.handler(req, res)
                   
                   
                    break
            await self.execute_middleware_stack(request, response, handler)
            
            if handler:
                [self.http_middlewares.remove(x) for x in route.router_middleware or []]

            
        except Exception as e:
            error = traceback.format_exc()
            self.logger.error(f"Request handler error: {str(error)}")
            response.json("Server Error", 500)
        
        await response(scope, receive, send)
        return 
    def route(self, path: str, methods: List[Union[str, HTTPMethod]] = allowed_methods_default,validator = None) -> Callable:
        
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            handler = allowed_methods(methods)(handler)
            self.add_route(Routes(path, handler,methods=methods,validator=validator))
            return handler
        return decorator
    def ws_route(self, path: str) -> Callable:
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            self.add_route(Routes(path, handler))
            return handler
        return decorator
    
    def add_ws_route(self, route: Routes) -> None:
        """Add a route to the application"""
        
        self.ws_routes.append(route)

    def add_route(self, route: Routes) -> None:
        """Add a route to the application"""
        
       
        self.routes.append(route)

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the application"""
        if callable(middleware):
            self.http_middlewares.append(middleware)
        

    def mount_router(self, router: Router) -> None:
        """Mount a router and all its routes to the application"""
        for route in router.get_routes():
            self.add_route(route)

    def mount_ws_router(self, router:WSRouter ) -> None:
        """Mount a router and all its routes to the application"""
        for route in router.get_routes():
            
            self.add_ws_route(route)
    
    async def execute_ws_middleware_stack(self, ws, **kwargs):
        """
        Executes WebSocket middleware stack after route matching.
        """
        stack = self.ws_middlewares.copy()
        index = -1

        async def next_middleware():
            nonlocal index
            index += 1
            if index < len(stack):
                middleware = stack[index]
                return await middleware(ws, next_middleware, **kwargs)
            else:
                # No more middleware to process
                return None

        return await next_middleware()

    
    async def handler_websocket(self, scope, receive, send):
        ws = await get_websocket_session(scope, receive, send)
        await self.execute_ws_middleware_stack(ws)
        for route in self.ws_routes:
            url = self.normalize_path(ws.url.path)
            match = route.pattern.match(url)
            
            if match:
                route_kwargs = match.groupdict()
                scope['route_params'] = RouteParam(route_kwargs)
                
                try:
                    await route.execute_middleware_stack(ws)
                    await route.handler(ws, **route_kwargs)
                    return

                except Exception as e:
                    error = traceback.format_exc()
                    self.logger.error(f"WebSocket handler error: {error}")
                    await ws.close(code=1011, reason=f"Internal Server Error: {str(e)}")
                    return

        await ws.close(reason="Not found")
    def add_ws_middleware(self, middleware: Callable) -> None:
        """
        Add a WebSocket middleware to the application.
        """
        if callable(middleware):
            self.ws_middlewares.append(middleware)
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI application callable"""
        if scope["type"] == "lifespan":
            await self.handle_lifespan(receive, send)
        elif scope["type"] == "http":    
            await self.handle_http_request(scope, receive, send)

        else:
            await self.handler_websocket(scope, receive, send)

    def get(self, path: str,validator = None) -> Callable:
        """Decorator to register a GET route."""
        return self.route(path, methods=["GET"],validator = validator)

    def post(self, path: str,validator = None) -> Callable:
        """Decorator to register a POST route."""
        return self.route(path, methods=["POST"],validator= validator)

    def delete(self, path: str,validator = None) -> Callable:
        """Decorator to register a DELETE route."""
        return self.route(path, methods=["DELETE"],validator = validator)

    def put(self, path: str,validator = None) -> Callable:
        """Decorator to register a PUT route."""
        return self.route(path, methods=["PUT"],validator = validator)

    def patch(self, path: str,validator = None) -> Callable:
        """Decorator to register a PATCH route."""
        return self.route(path, methods=["PATCH"],validator = validator)

    def options(self, path: str,validator = None) -> Callable:
        """Decorator to register an OPTIONS route."""
        return self.route(path, methods=["OPTIONS"],validator = validator)
