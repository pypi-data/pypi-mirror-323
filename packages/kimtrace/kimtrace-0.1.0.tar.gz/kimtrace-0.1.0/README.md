# kimtrace-py

## Dependencies Required
1. Recommended Python version 3.8+ 
2. Ensure that you are loading dotenv in your application somewhere before KimTrace is called.

ex: 
```python
from dotenv import load_dotenv
load_dotenv()
```

## How to Use
You have access to two different decorators/wrappers called `@kRun` and `@kStep`.

### .env Secrets
```
KIMTRACE_ACCESS_KEY_ID = '<Will be provided when you onboard with Kimtrace>'
KIMTRACE_SECRET_ACCESS_KEY = '<Will be provided when you onboard with Kimtrace>'
KIMTRACE_REGION = '<Will be provided when you onboard with Kimtrace - but currently only supports us-east-1>'
KIMTRACE_SQS_URL = '<Will be provided when you onboard with Kimtrace>'
KIMTRACE_CLIENT_ID = '<Will be provided when you onboard with Kimtrace>'
## [OPTIONAL] emergency configuration, "true" will disable Kimtrace, and "false" or null will enable it. Useful when a Kimtrace regression is causing an outage on your service. 
#KIMTRACE_DISABLE = true
```

### @kRun 
This decorator is used to initialize Kimtrace, record the initial input and final output of the run, and start the process of recording the subsequent call stacks. 

All `@kStep` invocations are expected to have been preceeded by a `@kRun` invocation.

The decorator variant is`@kRun`, with some functional variants:
 - `krun_wrapper` is used when you want to wrap a function and call it later
 - `krun_wrapped_call` is used when you want to wrap a function and call it immediately

Here are some additional properties you can configure using `@kRun`:
- *run_id*: Sets the run id of the execution, used to identify in the Kimtrace webapp
- *run_name*: Sets the name of the overall run, used to identify in the Kimtrace webapp
- *tags*: An array of property names (string) that will be used to tag the run based on the non-object output from the run's input. If the value is an object, it will be ignored.

Example 1:
```
if the input is {a: 1, b: 2} and you specify `tags: ["a"]`, it will tag the run with "1"
```

Example 2:
```
if the input is {a: {num: 1}, b: 2} and you specify `tags: ["a", "b"]`, it will tag the run with "2"
```

- *redactors*: An array of strings that will be used to redact the input and output of the run in the Kimtrace webapp

Example 1: Redacting the input of a nested step based on `redactors: ["firstNum"]`:
```
    {
      "stepName": "StepWrapper.asyncAdd",
      "stepStatus": "success",
      "stepInput": "[{\"firstNum\":\"[REDACTED]\",\"secondNum\":88}]",
      "stepOutput": "122",
      "stepStartTime": "2025-01-03T03:03:10.113Z",
      "stepEndTime": "2025-01-03T03:03:10.113Z",
      "calledFromId": "4359adfa-fd8a-408f-a376-e6814fee078c",
      "id": "75143726-2671-4818-8d82-0b36da012c19"
    },
```

### @kStep
This decorator is used to represent each step in the kRun call stack. If you decorate a class method with this decorator, it record the input and output of that method. 

The decorator variant is`@kStep`, with some functional variants:
 - `kstep_wrapper` is used when you want to wrap a function and call it later
 - `kstep_wrapped_call` is used when you want to wrap a function and call it immediately

This only has an additional property of `step_name` which has the same functionality as explained previously.

### Examples

#### Setting up a @kRun 

```python
from kimtrace import KRunParams

class TransactionProcessor:
    
    @staticmethod
    @kRun(KRunParams(run_name="Transaction.process", tags=["type_", "account_id"], redactors=["amount"]))
    async def process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        # ... code here
```

#### Setting up a krun_wrapper

```python
    @staticmethod
    async def process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        wrapped_fn = krun_wrapper(
            KRunParams(run_name="Transaction.process", tags=["type_", "account_id"], redactors=["amount"]),
            TransactionProcessor._process_transaction
        )
        return await wrapped_fn(amount=amount, type_=type_, account_id=account_id)

    @staticmethod
    async def _process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        # ... code here
```

#### Setting up a krun_wrapped_call

```python
    @staticmethod
    async def process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        return await async_krun_wrapped_call(
            KRunParams(run_name="Transaction.process", tags=["type_", "account_id"], redactors=["amount"]),
            TransactionProcessor._process_transaction,
            amount=amount, 
            type_=type_, 
            account_id=account_id
        )

    @staticmethod
    async def _process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        # ... code here
```

#### Setting up a @kStep

```python
    @staticmethod
    @kRun(KRunParams(run_name="Transaction.process", tags=["type_", "account_id"]))
    async def process_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        TransactionProcessor.transaction_count += 1
        validated = await TransactionProcessor.validate_transaction(amount=amount, type_=type_, account_id=account_id)
        # ... code here
    
    @staticmethod
    @kStep(KStepParams(step_name="Transaction.validate"))
    async def validate_transaction(amount: float, type_: str, account_id: str) -> Dict[str, Any]:
        # ... code here
```
