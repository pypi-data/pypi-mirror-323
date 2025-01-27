import inspect

from typing import Any, List, Dict, Callable

from graphql import (
    graphql,
    graphql_sync,
    ExecutionContext,
    GraphQLError,
    GraphQLOutputType,
)

from graphql.execution import ExecutionResult
from graphql.type.schema import GraphQLSchema

from graphql_api.context import GraphQLContext
from graphql_api.middleware import (
    middleware_field_context,
    middleware_request_context,
    middleware_local_proxy,
    middleware_adapt_enum,
    middleware_catch_exception,
    middleware_call_coroutine,
)


class GraphQLBaseExecutor:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def validate(self):
        pass

    def execute(self, query, variables=None, operation_name=None) -> ExecutionResult:
        pass

    async def execute_async(
        self, query, variables=None, operation_name=None
    ) -> ExecutionResult:
        pass


class ErrorProtectionExecutionContext(ExecutionContext):
    default_error_protection = True

    error_protection = "ERROR_PROTECTION"

    def handle_field_error(
        self,
        error: GraphQLError,
        return_type: GraphQLOutputType,
    ) -> None:
        error_protection = self.default_error_protection
        original_error = error.original_error
        if hasattr(error, self.error_protection):
            error_protection = getattr(error, self.error_protection)

        elif hasattr(original_error, self.error_protection):
            error_protection = getattr(original_error, self.error_protection)

        if not error_protection:
            raise error.original_error

        return super().handle_field_error(error=error, return_type=return_type)


class NoErrorProtectionExecutionContext(ErrorProtectionExecutionContext):
    default_error_protection = False


class GraphQLExecutor(GraphQLBaseExecutor):
    def __init__(
        self,
        schema: GraphQLSchema,
        meta: Dict = None,
        root_value: Any = None,
        middleware: List[Callable[[Callable, GraphQLContext], Any]] = None,
        middleware_on_introspection: bool = False,
        error_protection: bool = True,
    ):
        super().__init__()

        if meta is None:
            meta = {}

        if middleware is None:
            middleware = []

        middleware.insert(0, middleware_catch_exception)
        middleware.insert(0, middleware_field_context)
        middleware.insert(0, middleware_request_context)
        middleware.insert(0, middleware_local_proxy)
        middleware.insert(0, middleware_adapt_enum)
        middleware.insert(0, middleware_call_coroutine)

        self.meta = meta
        self.schema = schema
        self.middleware = middleware
        self.root_value = root_value
        self.middleware_on_introspection = middleware_on_introspection
        self.execution_context_class = (
            ErrorProtectionExecutionContext
            if error_protection
            else NoErrorProtectionExecutionContext
        )

    def execute(
        self, query, variables=None, operation_name=None, root_value=None, context=None
    ) -> ExecutionResult:
        context = GraphQLContext(schema=self.schema, meta=self.meta, executor=self)

        if root_value is None:
            root_value = self.root_value

        value = graphql_sync(
            self.schema,
            query,
            context_value=context,
            variable_values=variables,
            operation_name=operation_name,
            middleware=self.adapt_middleware(self.middleware),
            root_value=root_value,
            execution_context_class=self.execution_context_class,
        )
        return value

    async def execute_async(
        self, query, variables=None, operation_name=None, root_value=None, context=None
    ) -> ExecutionResult:
        context = GraphQLContext(schema=self.schema, meta=self.meta, executor=self)

        if root_value is None:
            root_value = self.root_value

        value = await graphql(
            self.schema,
            query,
            context_value=context,
            variable_values=variables,
            operation_name=operation_name,
            middleware=self.adapt_middleware(self.middleware),
            root_value=root_value,
            execution_context_class=self.execution_context_class,
        )
        return value

    @staticmethod
    def adapt_middleware(middleware, middleware_on_introspection: bool = False):
        def simplify(_middleware: Callable[[Callable, GraphQLContext], Any]):
            def graphql_middleware(next, root, info, **args):
                kwargs = {}
                if "context" in inspect.signature(_middleware).parameters:
                    context: GraphQLContext = info.context
                    kwargs["context"] = context
                    context.resolve_args["root"] = root
                    context.resolve_args["info"] = info
                    context.resolve_args["args"] = args

                return _middleware(lambda: next(root, info, **args), **kwargs)

            return graphql_middleware

        def skip_if_introspection(_middleware):
            def middleware_with_skip(next, root, info, **args):
                skip = (
                    info.operation.name
                    and info.operation.name.value == "IntrospectionQuery"
                )
                if skip:
                    return next(root, info, **args)
                return _middleware(next, root, info, **args)

            return middleware_with_skip

        adapters = [simplify]

        if middleware_on_introspection is False:
            adapters.append(skip_if_introspection)

        adapted_middleware = []

        for middleware in reversed(middleware):
            for adapter in adapters:
                middleware = adapter(middleware)
            adapted_middleware.append(middleware)

        return adapted_middleware
