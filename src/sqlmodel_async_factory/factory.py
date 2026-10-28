import asyncio
import inspect
from typing import Any

from factory import Factory, FactoryError
from factory.alchemy import SQLAlchemyOptions
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar


def _lookup_statement(
    model_class: type[SQLModel], key_fields: dict[str, Any]
) -> "SelectOfScalar[Any]":
    # select().filter_by() drops SQLModel's scalar typing, so exec() would yield Rows
    statement = select(model_class)
    for field, value in key_fields.items():
        statement = statement.where(getattr(model_class, field) == value)
    return statement


class AsyncSQLModelOptions(SQLAlchemyOptions):
    # factory_boy declares these through OptionDefault, out of reach of a type checker
    sqlalchemy_session: AsyncSession
    sqlalchemy_get_or_create: tuple[str, ...]


class AsyncSQLModelFactory(Factory):
    _options_class = AsyncSQLModelOptions
    _meta: AsyncSQLModelOptions
    _original_params: dict[str, Any]

    @classmethod
    def _generate(cls, strategy: str, params: dict[str, Any]) -> Any:
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        cls._original_params = params
        return super()._generate(strategy, params)

    @classmethod
    async def create(cls, **kwargs: Any) -> Any:
        session = cls._meta.sqlalchemy_session

        instance = await super().create(**kwargs)
        # one commit per build to avoid sharing the same connection
        await session.commit()
        return instance

    @classmethod
    def _create(cls, model_class: type[SQLModel], *args: Any, **kwargs: Any) -> Any:
        async def maker_coroutine() -> Any:
            for key, value in kwargs.items():
                # when using SubFactory, you'll have a Task in the corresponding kwarg
                # await tasks to pass model instances instead
                if inspect.isawaitable(value):
                    kwargs[key] = await value

            if cls._meta.sqlalchemy_get_or_create:
                return await cls._get_or_create(model_class, *args, **kwargs)
            return await cls._save(model_class, *args, **kwargs)

        # A Task can be awaited multiple times, unlike a coroutine.
        # useful when a factory and a subfactory must share a same object
        return asyncio.create_task(maker_coroutine())

    @classmethod
    async def create_batch(  # type: ignore[override]
        cls, size: int, **kwargs: Any
    ) -> list[Any]:
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _get_or_create(
        cls, model_class: type[SQLModel], *args: Any, **kwargs: Any
    ) -> Any:
        session = cls._meta.sqlalchemy_session

        key_fields = {}
        for field in cls._meta.sqlalchemy_get_or_create:
            if field not in kwargs:
                raise FactoryError(
                    "sqlalchemy_get_or_create - "
                    f"Unable to find initialization value for '{field}' "
                    f"in factory {cls.__name__}"
                )
            key_fields[field] = kwargs.pop(field)

        obj = (await session.exec(_lookup_statement(model_class, key_fields))).first()
        if obj is not None:
            return obj

        try:
            return await cls._save(model_class, *args, **key_fields, **kwargs)
        except IntegrityError as error:
            await session.rollback()
            get_or_create_params = {
                lookup: value
                for lookup, value in cls._original_params.items()
                if lookup in cls._meta.sqlalchemy_get_or_create
            }
            if not get_or_create_params:
                raise
            try:
                return (
                    await session.exec(
                        _lookup_statement(model_class, get_or_create_params)
                    )
                ).one()
            except NoResultFound:
                # Original params are not a valid lookup and triggered a create(),
                # that resulted in an IntegrityError.
                raise error from None

    @classmethod
    async def _save(cls, model_class: type[SQLModel], *args: Any, **kwargs: Any) -> Any:
        session = cls._meta.sqlalchemy_session

        obj = model_class(*args, **kwargs)
        session.add(obj)
        await session.commit()
        return obj

    class Meta:
        abstract = True
