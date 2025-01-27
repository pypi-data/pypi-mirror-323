"""
Provides parameter and input validation, integer parsing, and concurrency handling utilities.
"""
import multiprocessing
from collections.abc import Sized
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Type, Union

@dataclass
class MessageContext:
    value: Any = None
    valueType: Optional[str] = None
    containerType: Optional[str] = None
    isElement: bool = False

def _constructErrorMessage(context: MessageContext, parameterName: str, parameterType: Optional[Type[Any]] = None) -> str:
    """Constructs error message from available context using template:
    I received ["value" | a value | None] [of type `type` | None] [as an element in | None] [a `containerType` type | None] but `parameterName` must have integers [in type(s) `parameterType` | None].
    """
    messageParts = ["I received "]

    # Value part
    if context.value is not None and not isinstance(context.value, (bytes, bytearray, memoryview)):
        messageParts.append(f'"{context.value}"')
    else:
        messageParts.append("a value")

    # Type part
    if context.valueType:
        messageParts.append(f" of type `{context.valueType}`")

    # Element part
    if context.isElement:
        messageParts.append(" as an element in")

    # Container part
    if context.containerType:
        messageParts.append(f" a `{context.containerType}` type")

    # Required part
    messageParts.append(f" but {parameterName} must have integers")

    # Parameter type part
    if parameterType:
        messageParts.append(f" in type(s) `{parameterType}`")

    return "".join(messageParts)

def defineConcurrencyLimit(limit: Optional[Union[int, float, bool]]) -> int:
    """
    Determines the concurrency limit based on the provided parameter. This package has Pytest tests you can import and run on this function. `from Z0Z_tools.pytest_parseParameters import makeTestSuiteConcurrencyLimit`

    Parameters:
        limit: Whether and how to limit CPU usage. Accepts True/False, an integer count, or a fraction of total CPUs.
               Positive and negative values have different behaviors, see code for details.

    Returns:
        concurrencyLimit: The calculated concurrency limit, ensuring it is at least 1.

    Notes:
        If you want to be extra nice to your users, consider using `Z0Z_tools.oopsieKwargsie()` to handle
    malformed inputs. For example:

    ```
    if not (CPUlimit is None or isinstance(CPUlimit, (bool, int, float))):
        CPUlimit = oopsieKwargsie(CPUlimit)
    ```

    Example parameter:
        from typing import Optional, Union
        CPUlimit: Optional[Union[int, float, bool]] = None

    Example parameter:
        from typing import Union
        CPUlimit: Union[bool, float, int, None]

    Example docstring:

    Parameters:
        CPUlimit: whether and how to limit the CPU usage. See notes for details.

    Limits on CPU usage `CPUlimit`:
        - `False`, `None`, or `0`: No limits on CPU usage; uses all available CPUs. All other values will potentially limit CPU usage.
        - `True`: Yes, limit the CPU usage; limits to 1 CPU.
        - Integer `>= 1`: Limits usage to the specified number of CPUs.
        - Decimal value (`float`) between 0 and 1: Fraction of total CPUs to use.
        - Decimal value (`float`) between -1 and 0: Fraction of CPUs to *not* use.
        - Integer `<= -1`: Subtract the absolute value from total CPUs.
    """
    cpuTotal = multiprocessing.cpu_count()
    concurrencyLimit = cpuTotal

    if isinstance(limit, str):
        limitFromString = oopsieKwargsie(limit) # type: ignore
        if isinstance(limitFromString, str):
            try:
                limit = float(limitFromString)
            except ValueError:
                raise ValueError(f"I received '{limitFromString}', but it must be a number, True, False, or None.")
        else:
            limit = limitFromString

    match limit:
        case None | False | 0:
            pass
        case True:
            concurrencyLimit = 1
        case _ if limit >= 1:
            concurrencyLimit = int(limit)
        case _ if 0 < limit < 1:
            concurrencyLimit = int(limit * cpuTotal)
        case _ if -1 < limit < 0:
            concurrencyLimit = cpuTotal - abs(int(limit * cpuTotal))
        case _ if limit <= 1:
            concurrencyLimit = cpuTotal - abs(int(limit))

    return max(int(concurrencyLimit), 1)

def intInnit(listInt_Allegedly: Iterable[int], parameterName: str = 'the parameter', parameterType: Optional[Type[Any]] = None) -> List[int]:
    """
    Validates and converts input to a list of integers. This package has Pytest tests you can import and run on this function. `from Z0Z_tools.pytest_parseParameters import makeTestSuiteIntInnit`


    Parameters:
        listInt_Allegedly: Input that should be a list of integers.
        parameterName: Name of parameter for error messages.

    Returns:
        listValidated: The validated integers.

    Raises:
        Various built-in exceptions with enhanced error messages.
    """
    if not listInt_Allegedly:
        raise ValueError(f"I did not receive a value for {parameterName}, but it is required.")

    try:
        iter(listInt_Allegedly)
        lengthInitial = None
        if isinstance(listInt_Allegedly, Sized):
            lengthInitial = len(listInt_Allegedly)

        listValidated = []

        for allegedInt in listInt_Allegedly:
            messageContext = MessageContext(
                value=allegedInt,
                valueType=type(allegedInt).__name__,
                isElement=True
            )

            if isinstance(allegedInt, bool):
                raise TypeError(messageContext)

            if isinstance(allegedInt, (bytes, bytearray, memoryview)):
                if (isinstance(allegedInt, memoryview) and allegedInt.nbytes != 1) or \
                    (not isinstance(allegedInt, memoryview) and len(allegedInt) != 1):
                    messageContext.value = None  # Don't include binary data in message
                    raise ValueError(messageContext)
                allegedInt = int.from_bytes(
                    allegedInt if isinstance(allegedInt, (bytes, bytearray))
                    else allegedInt.tobytes(),
                    byteorder='big'
                )

            if isinstance(allegedInt, complex):
                if allegedInt.imag != 0:
                    raise ValueError(messageContext)
                allegedInt = float(allegedInt.real)
            elif isinstance(allegedInt, str):
                allegedInt = float(allegedInt.strip())

            if isinstance(allegedInt, float):
                if not float(allegedInt).is_integer():
                    raise ValueError(messageContext)
                allegedInt = int(allegedInt)
            else:
                allegedInt = int(allegedInt)

            listValidated.append(allegedInt)

            if lengthInitial is not None and isinstance(listInt_Allegedly, Sized):
                if len(listInt_Allegedly) != lengthInitial:
                    raise RuntimeError((lengthInitial, len(listInt_Allegedly)))

        return listValidated

    except (TypeError, ValueError) as ERRORmessage:
        if isinstance(ERRORmessage.args[0], MessageContext):
            context = ERRORmessage.args[0]
            if not context.containerType:
                context.containerType = type(listInt_Allegedly).__name__
            message = _constructErrorMessage(context, parameterName, parameterType)
            raise type(ERRORmessage)(message) from None
        # If it's not our MessageContext, let it propagate
        raise

    except RuntimeError as ERRORruntime:
        lengthInitial, lengthCurrent = ERRORruntime.args[0]
        raise RuntimeError(
            f"The input sequence {parameterName} was modified during iteration. "
            f"Initial length {lengthInitial}, current length {lengthCurrent}."
        ) from None

def oopsieKwargsie(huh: str) -> None | str | bool:
    """
    If a calling function passes a `str` to a parameter that shouldn't receive a `str`, `oopsieKwargsie()` might help you avoid an Exception. It tries to interpret the string as `True`, `False`, or `None`. This package has Pytest tests you can import and run on this function. `from Z0Z_tools.pytest_parseParameters import makeTestSuiteOopsieKwargsie`

    Parameters:
        huh: The input string to be parsed.

    Returns:
        (bool | None | str): The reserved keywords `True`, `False`, or `None` or the original string, `huh`.
    """
    if not isinstance(huh, str):
        try:
            huh = str(huh)
        except Exception:
            return huh
    formatted = huh.strip().title()
    if formatted == str(True):
        return True
    elif formatted == str(False):
        return False
    elif formatted == str(None):
        return None
    else:
        return huh

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
