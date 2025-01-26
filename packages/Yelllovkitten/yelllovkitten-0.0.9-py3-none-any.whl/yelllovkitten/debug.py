import inspect
import yelllovkitten
import yelllovkitten.ofter
from warnings import warn as warning_python


def debug(func):
    """
    Checks the function for errors
    :param func: A function that takes as argument(s): Str, Int, Float, Bool or any.
    :return: True - if no errors are found. False - if errors are found.
    """
    errors = []
    type_any = 0
    try:
        every = len(inspect.getfullargspec(func).args)
        see = len(func.__annotations__)
    except:
        warning_python('Please specify the function as an argument.',stacklevel=2)
        return
    if every > see:
        errors.append([1,1])
        type_any = every - see
    try:
        for i in range(1,20000):
            new_list = []
            exitt = []
            for i in range(0, type_any):
                new_list.append(yelllovkitten.ofter.debug4())
            try: exitt = yelllovkitten.ofter.debug3(func)
            except: pass
            if not exitt:
                exitt = new_list
            elif not new_list:
                pass
            else:
                exitt = new_list + exitt
            eval(f'func({eval(f'str({exitt})[:-1][1:]')})')
    except:
        errors.append([2, 3])
    else:
        errors.append([0,1])
    if len(errors) > 0:
        yelllovkitten.text.out('\n\n\n\n\n\n\n\n\n\n',out_time=False)
        for i in errors:
            yelllovkitten.ofter.errors(i[0],i[1])