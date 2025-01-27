import asyncio
import logging
from collections import defaultdict
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from inspect import BoundArguments, Signature
from typing import Any, Generic, TypeVar, cast

from engin._dependency import Dependency, Provide, Supply
from engin._exceptions import AssemblyError
from engin._type_utils import TypeId, type_id_of

LOG = logging.getLogger("engin")

T = TypeVar("T")


@dataclass(slots=True, kw_only=True, frozen=True)
class AssembledDependency(Generic[T]):
    dependency: Dependency[Any, T]
    bound_args: BoundArguments

    async def __call__(self) -> T:
        return await self.dependency(*self.bound_args.args, **self.bound_args.kwargs)


class Assembler:
    def __init__(self, providers: Iterable[Provide]) -> None:
        self._providers: dict[TypeId, Provide[Any]] = {}
        self._multiproviders: dict[TypeId, list[Provide[list[Any]]]] = defaultdict(list)
        self._dependencies: dict[TypeId, Any] = {}
        self._consumed_providers: set[Provide[Any]] = set()
        self._lock = asyncio.Lock()

        for provider in providers:
            type_id = provider.return_type_id
            if not provider.is_multiprovider:
                if type_id in self._providers:
                    raise RuntimeError(f"A Provider already exists for '{type_id}'")
                self._providers[type_id] = provider
            else:
                self._multiproviders[type_id].append(provider)

    def _resolve_providers(self, type_id: TypeId) -> Collection[Provide]:
        if type_id.multi:
            providers = self._multiproviders.get(type_id)
        else:
            providers = [provider] if (provider := self._providers.get(type_id)) else None
        if not providers:
            if type_id.multi:
                LOG.warning(f"no provider for '{type_id}' defaulting to empty list")
                providers = [(Supply([], type_hint=list[type_id.type]))]  # type: ignore[name-defined]
            else:
                raise LookupError(f"No Provider registered for dependency '{type_id}'")

        required_providers: list[Provide[Any]] = []
        for provider in providers:
            required_providers.extend(
                provider
                for provider_param in provider.parameter_types
                for provider in self._resolve_providers(provider_param)
            )

        return {*required_providers, *providers}

    async def _satisfy(self, target: TypeId) -> None:
        for provider in self._resolve_providers(target):
            if provider in self._consumed_providers:
                continue
            self._consumed_providers.add(provider)
            type_id = provider.return_type_id
            bound_args = await self._bind_arguments(provider.signature)
            try:
                value = await provider(*bound_args.args, **bound_args.kwargs)
            except Exception as err:
                raise AssemblyError(
                    provider=provider, error_type=type(err), error_message=str(err)
                ) from err
            if provider.is_multiprovider:
                if type_id in self._dependencies:
                    self._dependencies[type_id].extend(value)
                else:
                    self._dependencies[type_id] = value
            else:
                self._dependencies[type_id] = value

    async def _bind_arguments(self, signature: Signature) -> BoundArguments:
        args = []
        kwargs = {}
        for param_name, param in signature.parameters.items():
            if param_name == "self":
                args.append(object())
                continue
            param_key = type_id_of(param.annotation)
            has_dependency = param_key in self._dependencies
            if not has_dependency:
                await self._satisfy(param_key)
            val = self._dependencies[param_key]
            if param.kind == param.POSITIONAL_ONLY:
                args.append(val)
            else:
                kwargs[param.name] = val

        return signature.bind(*args, **kwargs)

    async def assemble(self, dependency: Dependency[Any, T]) -> AssembledDependency[T]:
        async with self._lock:
            return AssembledDependency(
                dependency=dependency,
                bound_args=await self._bind_arguments(dependency.signature),
            )

    async def get(self, type_: type[T]) -> T:
        type_id = type_id_of(type_)
        if type_id in self._dependencies:
            return cast(T, self._dependencies[type_id])
        if type_id.multi:
            out = []
            for provider in self._multiproviders[type_id]:
                assembled_dependency = await self.assemble(provider)
                out.extend(await assembled_dependency())
            self._dependencies[type_id] = out
            return out  # type: ignore[return-value]
        else:
            assembled_dependency = await self.assemble(self._providers[type_id])
            value = await assembled_dependency()
            self._dependencies[type_id] = value
            return value  # type: ignore[return-value]

    def has(self, type_: type[T]) -> bool:
        return type_id_of(type_) in self._providers
