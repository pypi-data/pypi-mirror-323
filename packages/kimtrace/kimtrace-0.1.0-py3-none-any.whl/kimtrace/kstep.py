import uuid
import os
import asyncio
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, TypeVar, Union, cast, Optional
from typing_extensions import ParamSpec, Awaitable
from .types.external import KStepData
from .helper.krun_data import get_krun_data, is_krun_data
from .helper.serializer import serialize_with_redactor
from .helper.json_formatter import jsonify_error
from .storage.context_vars import storage, KRunStorageData
from .types.external import KStepParams, KStatus

P = ParamSpec('P')
T = TypeVar('T')

def handle_kstep_success(
    response: Any,
    step_name: str,
    args: str,
    redactors: list,
    context: Any,
    start_time: datetime,
    end_time: datetime,
    called_from: str,
    id: str
) -> Any:
    if not hasattr(context, 'steps'):
        context.steps = []
    
    context.steps.append(KStepData(
        id=id,
        stepName=step_name,
        stepStatus=KStatus.SUCCESS,
        stepInput=args or "{}",
        stepOutput=serialize_with_redactor(redactors, response) if response else "{}",
        stepStartTime=start_time,
        stepEndTime=end_time,
        calledFromId=called_from
    ))

    return response

def handle_kstep_error(
    error: Exception,
    step_name: str,
    args: str,
    context: Any,
    start_time: datetime,
    end_time: datetime,
    called_from: str,
    id: str
) -> Exception:
    if not hasattr(context, 'steps'):
        context.steps = []
        
    context.steps.append(KStepData(
        id=id,
        stepName=step_name,
        stepStatus=KStatus.FAILED,
        stepInput=args or "",
        stepOutput=jsonify_error(error),
        stepStartTime=start_time,
        stepEndTime=end_time,
        calledFromId=called_from
    ))

    return error

def kStep(params: Optional[KStepParams] = None):
    def decorator(func: Callable[P, T]) -> Callable[P, Union[T, Awaitable[T]]]:
        class_name = func.__qualname__.split('.')[-2] if '.' in func.__qualname__ else None
        method_name = func.__name__
        stack_name = f"{class_name}.{method_name}" if class_name else method_name
        
        if isinstance(func, (classmethod, staticmethod)):
            # Handle class/static methods
            method = func.__func__
            class_name = method.__qualname__.split('.')[-2]
            method_name = method.__name__
            stack_name = f"{class_name}.{method_name}"

        step_name = stack_name
        if (params and params.step_name):
            step_name = params.step_name

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                krun_data = get_krun_data()
                id = str(uuid.uuid4())

                if not is_krun_data(krun_data) or os.getenv("KIMTRACE_DISABLE", "false") == "true":
                    return await func(*args, **kwargs)

                context = krun_data.context
                called_from = krun_data.caller
                token = storage.set(KRunStorageData(context=context, caller=id))

                try:
                    func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
                    all_args = {}

                    for i, arg in enumerate(args):
                        if i < len(func_params):
                            all_args[func_params[i]] = arg
                    # Add keyword arguments
                    all_args.update(kwargs)
                    
                    serialized_args = serialize_with_redactor(context.redactors, all_args) if all_args else "{}"
                    
                    start_time = datetime.now(timezone.utc)
                    try:
                        response = await func(*args, **kwargs)
                        return handle_kstep_success(
                            response=response,
                            step_name=step_name,
                            args=serialized_args,
                            redactors=context.redactors,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            called_from=called_from,
                            id=id
                        )
                    except Exception as error:
                        raise handle_kstep_error(
                            error=error,
                            step_name=step_name,
                            args=serialized_args,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            called_from=called_from,
                            id=id
                        )
                finally:
                    storage.reset(token)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                krun_data = get_krun_data()
                id = str(uuid.uuid4())

                if not is_krun_data(krun_data) or os.getenv("KIMTRACE_DISABLE", "false") == "true":
                    return func(*args, **kwargs)

                context = krun_data.context
                called_from = krun_data.caller
                token = storage.set(KRunStorageData(context=context, caller=id))

                try:
                    func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
                    all_args = {}
                    # Add positional arguments with their parameter names
                    for i, arg in enumerate(args):
                        if i < len(func_params):
                            all_args[func_params[i]] = arg
                    # Add keyword arguments
                    all_args.update(kwargs)
                    
                    serialized_args = serialize_with_redactor(context.redactors, all_args) if all_args else "{}"

                    start_time = datetime.now(timezone.utc)
                    try:
                        response = func(*args, **kwargs)
                        return handle_kstep_success(
                            response=response,
                            step_name=step_name,
                            args=serialized_args,
                            redactors=context.redactors,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            called_from=called_from,
                            id=id
                        )
                    except Exception as error:
                        raise handle_kstep_error(
                            error=error,
                            step_name=step_name,
                            args=serialized_args,
                            context=context,
                            start_time=start_time,
                            end_time=datetime.now(timezone.utc),
                            called_from=called_from,
                            id=id
                        )
                finally:
                    storage.reset(token)

            return sync_wrapper

    return decorator

def kstep_wrapper(params: Optional[KStepParams], fn: Callable[P, T]) -> Callable[P, Union[T, Awaitable[T]]]:
    return kStep(params)(fn)

def kstep_wrapped_call(params: Optional[KStepParams], fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    wrapped_fn = kstep_wrapper(params, fn)
    return cast(T, wrapped_fn(*args, **kwargs))

async def async_kstep_wrapped_call(params: Optional[KStepParams], fn: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    wrapped_fn = kstep_wrapper(params, fn)
    result = wrapped_fn(*args, **kwargs)
    return cast(T, await result)