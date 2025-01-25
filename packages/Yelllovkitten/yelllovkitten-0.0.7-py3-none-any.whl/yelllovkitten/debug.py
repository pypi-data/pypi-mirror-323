import inspect
import yelllovkitten
import yelllovkitten.ofter


def debug(func):
    errors = []
    every = len(inspect.getfullargspec(func).args)
    see = len(func.__annotations__)
    if every > see:
        errors.append([1,1])
    try:
        for i in range(1,20000):
            try: exitt = yelllovkitten.ofter.debug3(func)
            except: errors.append([-1, 2])
            eval(f'func({eval(f'str({exitt})[:-1][1:]')})')
    except:
        errors.append([2, 3])
    else:
        errors.append([0,1])
    if len(errors) > 0:
        yelllovkitten.text.out('\n\n\n\n\n\n\n\n\n\n')
        for i in errors:
            yelllovkitten.ofter.errors(i[0],i[1])