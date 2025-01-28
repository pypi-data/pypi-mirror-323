"""Completion Models."""

from __future__ import annotations

import copy
import datetime
from collections.abc import Iterable, Sequence
from typing import TypeAlias

from sqlalchemy import orm as sa_orm

from corvic import orm, system
from corvic.model._base_model import BaseModel
from corvic.model._defaults import Defaults
from corvic.model._proto_orm_convert import (
    completion_model_delete_orms,
    completion_model_orm_to_proto,
    completion_model_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2

CompletionModelID: TypeAlias = orm.CompletionModelID
OrgID: TypeAlias = orm.OrgID


class CompletionModel(
    BaseModel[CompletionModelID, models_pb2.CompletionModel, orm.CompletionModel]
):
    """Completion Models."""

    @classmethod
    def orm_class(cls):
        return orm.CompletionModel

    @classmethod
    def id_class(cls):
        return CompletionModelID

    @classmethod
    def orm_to_proto(cls, orm_obj: orm.CompletionModel) -> models_pb2.CompletionModel:
        return completion_model_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.CompletionModel, session: orm.Session
    ) -> Ok[orm.CompletionModel] | InvalidArgumentError:
        return completion_model_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[CompletionModelID], session: orm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return completion_model_delete_orms(ids, session)

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def org_id(self) -> OrgID:
        return OrgID(self.proto_self.org_id)

    @property
    def model_name(self) -> str:
        return self.proto_self.model_name

    @property
    def endpoint(self) -> str:
        return self.proto_self.endpoint

    @property
    def secret_api_key(self) -> str:
        return self.proto_self.secret_api_key

    @property
    def description(self) -> str:
        return self.proto_self.description

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        model_name: str,
        endpoint: str,
        secret_api_key: str,
        client: system.Client | None = None,
    ):
        client = client or Defaults.get_default_client()
        return cls(
            client,
            models_pb2.CompletionModel(
                name=name,
                description=description,
                model_name=model_name,
                endpoint=endpoint,
                secret_api_key=secret_api_key,
            ),
        )

    @classmethod
    def list(
        cls,
        *,
        limit: int | None = None,
        created_before: datetime.datetime | None = None,
        client: system.Client | None = None,
        ids: Iterable[CompletionModelID] | None = None,
        existing_session: sa_orm.Session | None = None,
    ) -> Ok[list[CompletionModel]] | NotFoundError | InvalidArgumentError:
        """List completion models."""
        client = client or Defaults.get_default_client()
        match cls.list_as_proto(
            client,
            limit=limit,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok([cls.from_proto(proto, client) for proto in protos])

    @classmethod
    def from_proto(
        cls, proto: models_pb2.CompletionModel, client: system.Client | None = None
    ) -> CompletionModel:
        client = client or Defaults.get_default_client()
        return cls(client, proto)

    @classmethod
    def from_id(
        cls,
        completion_model_id: CompletionModelID,
        client: system.Client | None = None,
        session: sa_orm.Session | None = None,
    ) -> Ok[CompletionModel] | NotFoundError:
        client = client or Defaults.get_default_client()
        return cls.load_proto_for(completion_model_id, client, session).map(
            lambda proto_self: cls.from_proto(proto_self, client)
        )

    def with_name(self, name: str) -> CompletionModel:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return CompletionModel(self.client, proto_self)

    def with_description(self, description: str) -> CompletionModel:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.description = description
        return CompletionModel(self.client, proto_self)

    def with_model_name(self, model_name: str) -> CompletionModel:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.model_name = model_name
        return CompletionModel(self.client, proto_self)

    def with_endpoint(self, endpoint: str) -> CompletionModel:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.endpoint = endpoint
        return CompletionModel(self.client, proto_self)

    def with_secret_api_key(self, secret_api_key: str) -> CompletionModel:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.secret_api_key = secret_api_key
        return CompletionModel(self.client, proto_self)
