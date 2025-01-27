import os
import uuid
import asyncio
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, TypeVar, Union, cast
from typing_extensions import ParamSpec, Awaitable
from .helper.krun_data import get_krun_data, is_krun_data
from .helper.serializer import serialize_with_redactor
from .helper.tag_extractor import get_tag_values
from .helper.json_formatter import jsonify_error
from .storage.context_vars import storage, KRunStorageData
from .client.sqs_client import KimtraceSQSClient
from .types.external import KRunData, KRunParams, KStatus

P = ParamSpec('P')
T = TypeVar('T')

async def handle_krun_success(
    response: Any,
    redactors: list,
    context: KRunData,
    start_time: datetime,
    end_time: datetime,
    emit_only_on_failure: bool = False
) -> Any:
    context.runStatus = KStatus.SUCCESS
    context.runOutput = serialize_with_redactor(redactors, response) if response else "{}"
    context.runStartTime = start_time
    context.runEndTime = end_time

    if not emit_only_on_failure:
        await handle_krun_completion(context)

    return response

async def handle_krun_error(
    error: Exception,
    context: KRunData,
    start_time: datetime,
    end_time: datetime
) -> Exception:
    if not context.tags:
        context.tags = []
    context.tags.append(error.__class__.__name__)

    serialized_result = jsonify_error(error)
    context.runStatus = KStatus.FAILED
    context.runOutput = serialized_result
    context.runStartTime = start_time
    context.runEndTime = end_time

    await handle_krun_completion(context)
    return error

async def handle_krun_completion(context: KRunData) -> None:
    await KimtraceSQSClient.send(context)

def kRun(params: KRunParams):
    def decorator(func: Callable[P, T]) -> Callable[P, Union[T, Awaitable[T]]]:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                init_context = get_krun_data()

                # If this is a nested kRun or disabled, bypass it
                if is_krun_data(init_context) or os.getenv("KIMTRACE_DISABLE", "false") == "true":
                    return await func(*args, **kwargs)

                request_id = params.run_id or str(uuid.uuid4())
                context = KRunData(
                    id=request_id,
                    clientId=os.getenv("KIMTRACE_CLIENT_ID", "ClientIdNotSet"),
                    runName=params.run_name,
                    redactors=params.redactors or []
                )

                token = storage.set(KRunStorageData(context=context, caller=request_id))
                try:
                    func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
                    all_args = {}

                    for i, arg in enumerate(args):
                        if i < len(func_params):
                            all_args[func_params[i]] = arg

                    all_args.update(kwargs)
                    
                    serialized_args = serialize_with_redactor(params.redactors or [], all_args) if all_args else "{}"
                    tag_values = get_tag_values(params.tags or [], all_args)

                    context.runInput = serialized_args
                    context.tags = tag_values
                    
                    start_time = datetime.now(timezone.utc)
                    try:
                        response = await func(*args, **kwargs)
                        return await handle_krun_success(
                            response=response,
                            redactors=params.redactors or [],
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            emit_only_on_failure=params.emit_only_on_failure or False
                        )
                    except Exception as error:
                        raise await handle_krun_error(
                            error=error,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc)
                        )
                finally:
                    storage.reset(token)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                init_context = get_krun_data()

                # If this is a nested kRun or disabled, bypass it
                if is_krun_data(init_context) or os.getenv("KIMTRACE_DISABLE", "false") == "true":
                    return func(*args, **kwargs)

                request_id = params.run_id or str(uuid.uuid4())
                context = KRunData(
                    id=request_id,
                    clientId=os.getenv("KIMTRACE_CLIENT_ID", "ClientIdNotSet"),
                    runName=params.run_name,
                    redactors=params.redactors or []
                )

                # Set the context
                token = storage.set(KRunStorageData(context=context, caller=request_id))
                try:
                    func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
                    all_args = {}

                    for i, arg in enumerate(args):
                        if i < len(func_params):
                            all_args[func_params[i]] = arg

                    all_args.update(kwargs)
                    
                    serialized_args = serialize_with_redactor(params.redactors or [], all_args) if all_args else "{}"
                    tag_values = get_tag_values(params.tags or [], all_args)

                    context.runInput = serialized_args
                    context.tags = tag_values

                    start_time = datetime.now(timezone.utc)
                    try:
                        response = func(*args, **kwargs)
                        # Use asyncio.run for the async operations in sync context
                        asyncio.run(handle_krun_success(
                            response=response,
                            redactors=params.redactors or [],
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            emit_only_on_failure=params.emit_only_on_failure or False
                        ))
                        return response
                    except Exception as error:
                        end_time = datetime.now(timezone.utc)
                        asyncio.run(handle_krun_error(
                            error=error,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc)
                        ))
                        raise
                finally:
                    storage.reset(token)

            return sync_wrapper

    return decorator

def krun_wrapper(params: KRunParams, fn: Callable[P, T]) -> Callable[P, Union[T, Awaitable[T]]]:
    return kRun(params)(fn)

def krun_wrapped_call(params: KRunParams, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    wrapped_fn = krun_wrapper(params, fn)
    return cast(T, wrapped_fn(*args, **kwargs))

async def async_krun_wrapped_call(params: KRunParams, fn: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    wrapped_fn = krun_wrapper(params, fn)
    result = wrapped_fn(*args, **kwargs)
    return cast(T, await result)