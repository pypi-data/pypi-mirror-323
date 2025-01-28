from functools import wraps

def action(name:str, description:str, parameters:dict, required:list):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    wrapper.__kl__name__ = name
    wrapper.__kl__doc__ = description
    wrapper.__kl__parameters__ = parameters
    wrapper.__kl__required__ = required
    return wrapper
  return decorator

def tool(name:str, description:str, parameters:dict, required:list, category:str):
  def decorator(cls):  
    class decoratorCls(cls):
      def __init__(self, *args, **kwargs):
        self.__kl__name__ = name
        self.__kl__doc__ = description
        self.__kl__parameters__ = parameters
        self.__kl__required__ = required
        self.__kl__category__ = category
        super().__init__(*args, **kwargs)
    decoratorCls.__kl__name__ = name
    decoratorCls.__kl__doc__ = description
    decoratorCls.__kl__parameters__ = parameters
    decoratorCls.__kl__required__ = required
    decoratorCls.__kl__category__ = category
    return decoratorCls
  return decorator