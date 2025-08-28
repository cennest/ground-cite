"""
Core dependency injection container for the GroundCite library.

This module implements a thread-safe dependency injection container that provides
service registration, resolution, and lifecycle management. It supports singleton
and transient scopes, named bindings, and automatic dependency resolution.
"""

import threading
from inspect import signature
from functools import wraps
from punq import Container, Scope
from typing import Type, Optional, Dict, Any, Callable


class CoreDi:
    """
    Thread-safe dependency injection container.
    
    Provides service registration, dependency resolution, and lifecycle management
    for the GroundCite library. Supports singleton and transient scopes with
    automatic constructor injection and named service bindings.
    
    Attributes:
        _global_instance (CoreDi): Global singleton instance
        _lock (threading.Lock): Thread synchronization lock
        _container (Container): Underlying punq container
        _named_bindings (Dict): Named service binding registry
    """
    _global_instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._container = Container()
        self._named_bindings: Dict[tuple[Type, str], Any] = {}

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._global_instance = None

    @classmethod
    def global_instance(cls):
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = CoreDi()
        return cls._global_instance

    def add_transient(self, implementation: Type, interface: Optional[Type] = None, name: Optional[str] = None):
        self._register(implementation, interface, Scope.transient, name)

    def add_singleton(self, implementation: Type, interface: Optional[Type] = None, name: Optional[str] = None):
        self._register(implementation, interface, Scope.singleton, name)

    def add_factory(self, factory: Callable, interface: Type, name: Optional[str] = None, scope: Scope = Scope.transient):
        self._container.register(interface, factory, scope=scope)
        if name:
            self._named_bindings[(interface, name)] = factory


    def _register(self, implementation: Type, interface: Optional[Type], scope: Scope, name: Optional[str]):

        if not callable(implementation):
            raise TypeError(f"Implementation must be callable, got {type(implementation)}")

        if interface:
            if name:
                self._container.register(implementation, implementation, scope=scope)
                self._named_bindings[(interface, name)] = implementation
            else:
                self._container.register(interface, implementation, scope=scope)
        else:
            self._container.register(implementation, implementation, scope=scope)


    def resolve(self, key: Type, name: Optional[str] = None) -> Any:
        if name:
            impl = self._named_bindings.get((key, name))
            if not impl:
                raise ValueError(f"No implementation registered for interface {key} with name '{name}'")
            return self._container.resolve(impl)
        return self._container.resolve(key)



    def inject(self, func: Callable):
        sig = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for name, param in sig.parameters.items():
                if name not in kwargs and param.annotation != param.empty:
                    try:
                        override_name = kwargs.pop(f"__di_name__{name}", None)
                        kwargs[name] = self.resolve(param.annotation, name=override_name)
                    except Exception as e:
                        raise RuntimeError(f"Dependency injection failed for parameter '{name}': {e}") from e
            return func(*args, **kwargs)

        return wrapper

def coredi_injectable(
    interface: Optional[Type] = None,
    scope: Scope = Scope.singleton,
    name: Optional[str] = None,
    container: Optional[CoreDi] = None,
):
    def decorator(cls):
        target_container = container or CoreDi.global_instance()
        target_container._register(cls, interface=interface, scope=scope, name=name)
        return cls

    return decorator


def inject(_func=None, **named_bindings):
    """
    Decorator that supports:
    - @inject
    - @inject(logger="file", db="mysql")
    """
    def decorator(func: Callable):
        base_wrapper = CoreDi.global_instance().inject(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for param, name in named_bindings.items():
                kwargs[f"__di_name__{param}"] = name
            return base_wrapper(*args, **kwargs)

        return wrapper

    if callable(_func):
        # Used as @inject without params
        return decorator(_func)

    # Used as @inject(...)
    return decorator

def inject_privately(*service_params):
    """
    Custom decorator that injects services but doesn't expose them in the public signature.
    
    Args:
        service_params: Names of parameters that should be injected but hidden from callers
    """
    def decorator(func):
        # Apply the original inject decorator
        injected_func = inject(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Remove any service parameters that callers might try to pass
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in service_params}
            return await injected_func(*args, **filtered_kwargs)
        
        # Modify the wrapper's signature to hide service parameters
        import inspect
        sig = inspect.signature(func)
        new_params = [
            param for name, param in sig.parameters.items() 
            if name not in service_params
        ]
        wrapper.__signature__ = sig.replace(parameters=new_params)
        
        return wrapper
    return decorator