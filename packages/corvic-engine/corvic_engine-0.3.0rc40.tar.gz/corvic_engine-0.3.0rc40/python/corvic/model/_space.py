"""Spaces."""

from __future__ import annotations

import abc
import copy
import dataclasses
import datetime
import uuid
from collections.abc import Iterable, Mapping, Sequence
from typing import Final, Literal, TypeAlias

import pyarrow as pa
from more_itertools import first
from sqlalchemy import orm as sa_orm
from typing_extensions import Self

from corvic import op_graph, orm, system
from corvic.model._base_model import BaseModel
from corvic.model._defaults import Defaults
from corvic.model._feature_view import FeatureView, FeatureViewEdgeTableMetadata
from corvic.model._proto_orm_convert import (
    space_delete_orms,
    space_orm_to_proto,
    space_proto_to_orm,
)
from corvic.model._source import Source
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic.table import Table
from corvic_generated.algorithm.graph.v1 import graph_pb2
from corvic_generated.embedding.v1 import models_pb2 as embedding_models_pb2
from corvic_generated.feature.v2 import space_pb2 as feature_space_pb2
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import space_pb2

FeatureViewID: TypeAlias = orm.FeatureViewID
RoomID: TypeAlias = orm.RoomID
SpaceID: TypeAlias = orm.SpaceID

_DEFAULT_CONCAT_SEPARATOR = " "


model_proto_to_name: Final[dict[embedding_models_pb2.Model, str]] = {
    embedding_models_pb2.MODEL_CUSTOM: "random",
    embedding_models_pb2.MODEL_SENTENCE_TRANSFORMER: "text-embedding-004",
    embedding_models_pb2.MODEL_GCP_TEXT_EMBEDDING_004: "text-embedding-004",
    embedding_models_pb2.MODEL_OPENAI_TEXT_EMBEDDING_3_SMALL: "text-embedding-3-small",
    embedding_models_pb2.MODEL_OPENAI_TEXT_EMBEDDING_3_LARGE: "text-embedding-3-large",
    embedding_models_pb2.MODEL_IDENTITY: "identity",
    embedding_models_pb2.MODEL_UNSPECIFIED: "",
}
name_to_proto_model = {name: model for model, name in model_proto_to_name.items()}


image_model_proto_to_name: Final[dict[embedding_models_pb2.ImageModel, str]] = {
    embedding_models_pb2.IMAGE_MODEL_CUSTOM: "random",
    embedding_models_pb2.IMAGE_MODEL_CLIP: "openai/clip-vit-base-patch32",
    embedding_models_pb2.IMAGE_MODEL_IDENTITY: "identity",
    embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED: "",
}
name_to_proto_image_model = {
    name: model for model, name in image_model_proto_to_name.items()
}


class Space(BaseModel[SpaceID, models_pb2.Space, orm.Space]):
    """Spaces apply embedding methods to FeatureViews.

    Example:
    >>> space = Space.node2vec(feature_view, dim=10, walk_length=10, window=10)
    """

    _feature_view: FeatureView | None

    def __init__(
        self,
        client: system.Client,
        proto_self: models_pb2.Space,
        feature_view: FeatureView | None = None,
    ):
        super().__init__(client, proto_self)
        self._feature_view = feature_view

    @classmethod
    def orm_class(cls):
        return orm.Space

    @classmethod
    def id_class(cls):
        return SpaceID

    @classmethod
    def orm_to_proto(cls, orm_obj: orm.Space) -> models_pb2.Space:
        return space_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.Space, session: orm.Session
    ) -> Ok[orm.Space] | InvalidArgumentError:
        return space_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[SpaceID], session: orm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return space_delete_orms(ids, session)

    @property
    def column_embedding_parameters(
        self,
    ) -> embedding_models_pb2.ColumnEmbeddingParameters | None:
        if self.proto_self.space_parameters.HasField("column_embedding_parameters"):
            return self.proto_self.space_parameters.column_embedding_parameters
        return None

    @property
    def node2vec_parameters(self) -> graph_pb2.Node2VecParameters | None:
        if self.proto_self.space_parameters.HasField("node2vec_parameters"):
            return self.proto_self.space_parameters.node2vec_parameters
        return None

    @property
    def concat_and_embed_parameters(
        self,
    ) -> embedding_models_pb2.ConcatAndEmbedParameters | None:
        if self.proto_self.space_parameters.HasField("concat_and_embed_parameters"):
            return self.proto_self.space_parameters.concat_and_embed_parameters
        return None

    @property
    def embed_and_concat_parameters(
        self,
    ) -> embedding_models_pb2.EmbedAndConcatParameters | None:
        if self.proto_self.space_parameters.HasField("embed_and_concat_parameters"):
            return self.proto_self.space_parameters.embed_and_concat_parameters
        return None

    @property
    def embed_image_parameters(
        self,
    ) -> embedding_models_pb2.EmbedImageParameters | None:
        if self.proto_self.space_parameters.HasField("embed_image_parameters"):
            return self.proto_self.space_parameters.embed_image_parameters
        return None

    @property
    def name(self):
        return self.proto_self.name

    @property
    def room_id(self):
        return RoomID(self.proto_self.room_id)

    @property
    def description(self):
        return self.proto_self.description

    @property
    def parameters(self):
        return self.proto_self.space_parameters

    @property
    def feature_view_id(self):
        return FeatureViewID(self.proto_self.feature_view_id)

    @property
    def auto_sync(self):
        return self.proto_self.auto_sync

    @property
    def space_type(self):
        if self.node2vec_parameters:
            return feature_space_pb2.SPACE_TYPE_RELATIONAL
        if self.concat_and_embed_parameters:
            return feature_space_pb2.SPACE_TYPE_SEMANTIC
        if self.embed_and_concat_parameters:
            return feature_space_pb2.SPACE_TYPE_TABULAR
        if self.embed_image_parameters:
            return feature_space_pb2.SPACE_TYPE_IMAGE
        return feature_space_pb2.SPACE_TYPE_UNSPECIFIED

    def with_auto_sync(self, *, auto_sync: bool):
        self.proto_self.auto_sync = auto_sync
        return self

    def feature_view(self):
        if self._feature_view:
            return Ok(self._feature_view)
        match FeatureView.load_proto_for(self.feature_view_id, self.client):
            case Ok(feature_view):
                return Ok(FeatureView.from_proto(feature_view, self.client))
            case NotFoundError() as err:
                return err

    @abc.abstractmethod
    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        """Generate per-output-source embeddings tables for this space."""

    @classmethod
    def from_id(
        cls,
        space_id: SpaceID,
        client: system.Client | None = None,
        session: sa_orm.Session | None = None,
    ) -> Ok[SpecificSpace] | NotFoundError:
        client = client or Defaults.get_default_client()
        return cls.load_proto_for(space_id, client, session).map(
            lambda proto_self: cls.from_proto(
                proto_self,
                client,
            )
        )

    @classmethod
    def list(
        cls,
        *,
        limit: int | None = None,
        room_id: orm.RoomID | None = None,
        created_before: datetime.datetime | None = None,
        client: system.Client | None = None,
        ids: Iterable[orm.SpaceID] | None = None,
        existing_session: sa_orm.Session | None = None,
    ) -> Ok[list[SpecificSpace]] | InvalidArgumentError | NotFoundError:
        client = client or Defaults.get_default_client()

        match cls.list_as_proto(
            client,
            limit=limit,
            room_id=room_id,
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
        cls, proto: models_pb2.Space, client: system.Client | None = None
    ) -> SpecificSpace:
        client = client or Defaults.get_default_client()
        if proto.space_parameters.HasField("node2vec_parameters"):
            return RelationalSpace(client, proto)
        if proto.space_parameters.HasField("concat_and_embed_parameters"):
            return SemanticSpace(client, proto)
        if proto.space_parameters.HasField("embed_and_concat_parameters"):
            return TabularSpace(client, proto)
        if proto.space_parameters.HasField("embed_image_parameters"):
            return ImageSpace(client, proto)
        return UnknownSpace(client, proto)


class UnknownSpace(Space):
    """A space that this version of the code doesn't know what to do with."""

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        """Generate per-ouput-source embeddings tables for this space."""
        return Ok({})


@dataclasses.dataclass(frozen=True)
class Node2VecParameters:
    dim: int = 10
    walk_length: int = 10
    window: int = 10
    p: float = 1.0
    q: float = 1.0
    alpha: float = 0.025
    min_alpha: float = 0.0001
    negative: int = 5
    epochs: int = 10

    def to_proto(self) -> graph_pb2.Node2VecParameters:
        return graph_pb2.Node2VecParameters(
            ndim=self.dim,
            walk_length=self.walk_length,
            window=self.window,
            p=self.p,
            q=self.q,
            alpha=self.alpha,
            min_alpha=self.min_alpha,
            negative=self.negative,
            epochs=self.epochs,
        )


class RelationalSpace(Space):
    """Spaces for embeddings that encode relationships."""

    @classmethod
    def create(
        cls,
        feature_view: FeatureView,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Ok[RelationalSpace] | InvalidArgumentError:
        if not feature_view.relationships:
            return InvalidArgumentError(
                "space will not be useful without at least one relationship"
            )
        if not feature_view.output_sources:
            return InvalidArgumentError(
                "space will not be useful without at least one output source"
            )
        client = client or feature_view.client
        room_id = room_id or Defaults.get_default_room_id(client)
        proto_self = models_pb2.Space(
            feature_view_id=str(feature_view.id), room_id=str(room_id)
        )

        return Ok(
            RelationalSpace(
                client,
                proto_self,
                feature_view,
            )
        )

    def with_node2vec(self, params: Node2VecParameters):
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.space_parameters.CopyFrom(
            space_pb2.SpaceParameters(node2vec_parameters=params.to_proto())
        )
        return RelationalSpace(
            self.client, proto_self, self.feature_view().unwrap_or_raise()
        )

    def legacy_embeddings_table(self) -> Ok[Table] | InvalidArgumentError:
        if not self.node2vec_parameters:
            return InvalidArgumentError("space was not configured")
        match self.feature_view():
            case Ok(feature_view):
                pass
            case NotFoundError() as err:
                return InvalidArgumentError.from_(err)

        def gen_edge_list_tables():
            for edge_table in feature_view.output_edge_tables():
                endpoint_metadata = edge_table.get_typed_metadata(
                    FeatureViewEdgeTableMetadata
                )
                yield op_graph.EdgeListTable(
                    table=edge_table.set_metadata({}).op_graph,
                    start_column_name=endpoint_metadata.start_source_column_name,
                    start_entity_name=endpoint_metadata.start_source_name,
                    end_column_name=endpoint_metadata.end_source_column_name,
                    end_entity_name=endpoint_metadata.end_source_name,
                )

        edge_list_tables = list(gen_edge_list_tables())
        if not edge_list_tables:
            return InvalidArgumentError(
                "no relationships given, or those given did not result in edges between"
                + "output sources"
            )

        return op_graph.op.embed_node2vec_from_edge_lists(
            edge_list_tables=edge_list_tables,
            params=self.node2vec_parameters,
        ).map(
            lambda t: Table(
                self.client,
                t,
            )
        )

    def _split_embedding_table_by_source(
        self, embeddings_table: op_graph.Op
    ) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        match embeddings_table.unnest_struct("id"):
            case InvalidArgumentError() as err:
                return err
            case Ok(embeddings_table):
                pass
        match self.feature_view():
            case Ok(feature_view):
                pass
            case NotFoundError() as err:
                return InvalidArgumentError.from_(err)
        id_fields = [
            field
            for field in embeddings_table.schema
            if field.name.startswith("column_")
        ]
        id_fields.sort(key=lambda field: int(field.name.removeprefix("column_")))
        source_name_column = id_fields[-1].name
        dtype_to_id_field = {field.dtype: field.name for field in id_fields[:-1]}

        tables: Mapping[str, Table] = {}
        for source_id in feature_view.output_sources:
            source = feature_view.source_id_to_feature_view_source[source_id].source
            primary_key_field = source.table.schema.get_primary_key()
            if primary_key_field is None:
                return InvalidArgumentError(
                    "source is required to have a primary key to be an output"
                )
            source_id_column = dtype_to_id_field[primary_key_field.dtype]

            match (
                embeddings_table.filter_rows(
                    op_graph.row_filter.eq(source_name_column, source.name, pa.string())
                )
                .and_then(
                    lambda t, source_id_column=source_id_column: t.select_columns(
                        [source_id_column, "embedding"]
                    )
                )
                .and_then(
                    lambda t, source_id_column=source_id_column: t.rename_columns(
                        {source_id_column: "entity_id"}
                    )
                )
                .and_then(
                    lambda t, source_id=source_id: t.add_literal_column(
                        "source_id",
                        str(source_id),
                        pa.string(),
                    )
                )
            ):
                case Ok(op):
                    pass
                case InvalidArgumentError() as err:
                    return err

            table = Table(
                self.client,
                op,
            )
            tables[source.name] = table

        return Ok(tables)

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        return self.legacy_embeddings_table().and_then(
            lambda t: self._split_embedding_table_by_source(t.op_graph)
        )


@dataclasses.dataclass
class ConcatAndEmbedParameters:
    column_names: list[str]
    model_name: str
    tokenizer_name: str
    expected_vector_length: int


class SemanticSpace(Space):
    """Spaces for embedding source properties."""

    _output_sources: list[Source] | None

    def __init__(
        self,
        client: system.Client,
        proto_self: models_pb2.Space,
        feature_view: FeatureView | None = None,
        output_sources: list[Source] | None = None,
    ):
        super().__init__(client, proto_self, feature_view)
        self._output_sources = output_sources

    def output_sources(self):
        if self._output_sources is not None:
            return Ok(self._output_sources)
        match self.feature_view():
            case Ok(feature_view):
                return Ok(
                    [
                        feature_view.source_id_to_feature_view_source[
                            output_source
                        ].source
                        for output_source in feature_view.output_sources
                    ]
                )
            case NotFoundError() as err:
                return err

    @property
    def expected_coordinate_bitwidth(self) -> Literal[32]:
        return 32

    @property
    def tokenizer_name(self) -> Literal[""]:
        return ""

    @property
    def model_name(self) -> str | None:
        if self.concat_and_embed_parameters:
            return model_proto_to_name[
                self.concat_and_embed_parameters.model_parameters.model
            ]
        return None

    @classmethod
    def create(
        cls,
        feature_view: FeatureView,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Ok[SemanticSpace] | InvalidArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) == 0:
            return InvalidArgumentError(
                "feature view must have at least one output source"
            )
        sources = [
            feature_view.source_id_to_feature_view_source[output_source].source
            for output_source in feature_view.output_sources
        ]

        room_id = room_id or Defaults.get_default_room_id(client)
        proto_self = models_pb2.Space(
            feature_view_id=str(feature_view.id), room_id=str(room_id)
        )
        return Ok(
            SemanticSpace(
                client,
                proto_self,
                feature_view,
                sources,
            )
        )

    def with_concat_and_embed(self, params: ConcatAndEmbedParameters) -> SemanticSpace:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.space_parameters.CopyFrom(
            space_pb2.SpaceParameters(
                concat_and_embed_parameters=embedding_models_pb2.ConcatAndEmbedParameters(
                    column_names=params.column_names,
                    model_parameters=embedding_models_pb2.Parameters(
                        model=name_to_proto_model.get(
                            params.model_name, embedding_models_pb2.MODEL_UNSPECIFIED
                        ),
                        ndim=params.expected_vector_length,
                    ),
                )
            )
        )
        return SemanticSpace(
            self.client,
            proto_self,
            self.feature_view().unwrap_or_raise(),
            output_sources=self.output_sources().unwrap_or_raise(),
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        model_name = self.model_name
        if not self.concat_and_embed_parameters or model_name is None:
            return InvalidArgumentError(
                "space was not configured to produce embeddings"
            )
        match self.output_sources():
            case Ok(output_sources):
                pass
            case NotFoundError() as err:
                return InvalidArgumentError.from_(err)

        params = self.concat_and_embed_parameters
        combined_column_tmp_name = f"__concat-{uuid.uuid4()}"
        embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

        tables: Mapping[str, Table] = {}

        first_schema = output_sources[0].table.schema

        for output_source in output_sources:
            pk_field = output_source.table.schema.get_primary_key()
            if pk_field is None:
                return InvalidArgumentError("output source must have a primary key")

            if first_schema != output_source.table.schema:
                return InvalidArgumentError(
                    "schema for all output sources must be the same"
                )

            op = (
                output_source.table.op_graph.concat_string(
                    list(params.column_names),
                    combined_column_tmp_name,
                    _DEFAULT_CONCAT_SEPARATOR,
                )
                .and_then(
                    lambda t: t.embed_column(
                        combined_column_tmp_name,
                        embedding_column_tmp_name,
                        model_name,
                        self.tokenizer_name,
                        params.model_parameters.ndim,
                        self.expected_coordinate_bitwidth,
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.select_columns(  # noqa: E501
                        [pk_field.name, embedding_column_tmp_name]
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.rename_columns(  # noqa: E501
                        {
                            pk_field.name: "entity_id",
                            embedding_column_tmp_name: "embedding",
                        }
                    )
                )
                .and_then(
                    lambda t, output_source=output_source: t.add_literal_column(
                        "source_id",
                        str(output_source.id),
                        pa.string(),
                    )
                )
            )

            match op:
                case Ok(table):
                    pass
                case InvalidArgumentError() as err:
                    return err

            tables[output_source.name] = Table(self.client, table)

        return Ok(tables)


@dataclasses.dataclass
class EmbedAndConcatParameters:
    expected_vector_length: int


class TabularSpace(Space):
    """Spaces for embedding source properties."""

    _output_sources: list[Source] | None

    def __init__(
        self,
        client: system.Client,
        proto_self: models_pb2.Space,
        feature_view: FeatureView | None = None,
        output_sources: list[Source] | None = None,
    ):
        super().__init__(client, proto_self, feature_view)
        self._output_sources = output_sources

    def output_sources(self):
        if self._output_sources is not None:
            return Ok(self._output_sources)
        match self.feature_view():
            case Ok(feature_view):
                return Ok(
                    [
                        feature_view.source_id_to_feature_view_source[
                            output_source
                        ].source
                        for output_source in feature_view.output_sources
                    ]
                )
            case NotFoundError() as err:
                return err

    @classmethod
    def create(
        cls,
        feature_view: FeatureView,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Ok[Self] | InvalidArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) == 0:
            return InvalidArgumentError(
                "feature view must have at least one output source"
            )
        sources = [
            feature_view.source_id_to_feature_view_source[output_source].source
            for output_source in feature_view.output_sources
        ]

        room_id = room_id or Defaults.get_default_room_id(client)
        proto_self = models_pb2.Space(
            feature_view_id=str(feature_view.id), room_id=str(room_id)
        )
        return Ok(
            cls(
                client,
                proto_self,
                feature_view,
                sources,
            )
        )

    def with_embed_and_concat(self, params: EmbedAndConcatParameters) -> TabularSpace:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.space_parameters.CopyFrom(
            space_pb2.SpaceParameters(
                embed_and_concat_parameters=embedding_models_pb2.EmbedAndConcatParameters(
                    ndim=params.expected_vector_length,
                )
            )
        )
        return TabularSpace(
            self.client,
            proto_self,
            self.feature_view().unwrap_or_raise(),
            output_sources=self.output_sources().unwrap_or_raise(),
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:  # noqa: C901
        if not self.embed_and_concat_parameters:
            return InvalidArgumentError(
                "space was not configured to produce embeddings"
            )
        match self.output_sources():
            case Ok(output_sources):
                pass
            case NotFoundError() as err:
                return InvalidArgumentError.from_(err)
        parameters = self.embed_and_concat_parameters

        tables: Mapping[str, Table] = {}
        first_schema = output_sources[0].table.schema

        for output_source in output_sources:
            pk_field = output_source.table.schema.get_primary_key()
            if not pk_field:
                return InvalidArgumentError("output source must have a primary key")

            if first_schema != output_source.table.schema:
                return InvalidArgumentError(
                    "schema for all output sources must be the same"
                )

            schema = output_source.table.op_graph.schema
            op = output_source.table.op_graph
            embedding_column_tmp_names: list[str] = []
            for column in schema:
                match column.ftype:
                    case op_graph.feature_type.Numerical():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            encoded_columns=[
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.max_abs_scaler(),
                                )
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err
                    case op_graph.feature_type.Categorical():
                        encoded_column_name = f"__encoded-{uuid.uuid4()}"
                        embedding_column_tmp_names.append(encoded_column_name)
                        match op.encode_columns(
                            [
                                op_graph.encoder.EncodedColumn(
                                    column_name=column.name,
                                    encoded_column_name=encoded_column_name,
                                    encoder=op_graph.encoder.label_encoder(),
                                ),
                            ]
                        ):
                            case Ok(op):
                                pass
                            case InvalidArgumentError() as err:
                                return err

                    case _:
                        continue

            embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

            op = (
                op.concat_list(
                    column_names=embedding_column_tmp_names,
                    concat_list_column_name=embedding_column_tmp_name,
                )
                .and_then(
                    lambda t,
                    embedding_column_name=embedding_column_tmp_name: op_graph.op.coordinates_from_embedding(  # noqa: E501
                        table=t,
                        embedding_column_name=embedding_column_name,
                        output_dims=parameters.ndim,
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name,
                    output_source=output_source: t.select_columns(
                        [pk_field.name, embedding_column_tmp_name]
                    )
                )
                .and_then(
                    lambda t,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.update_feature_types(  # noqa: E501
                        {embedding_column_tmp_name: op_graph.feature_type.embedding()}
                    )
                )
                .and_then(
                    lambda t,
                    pk_field=pk_field,
                    embedding_column_tmp_name=embedding_column_tmp_name: t.rename_columns(  # noqa: E501
                        {
                            pk_field.name: "entity_id",
                            embedding_column_tmp_name: "embedding",
                        }
                    )
                )
                .and_then(
                    lambda t, output_source=output_source: t.add_literal_column(
                        "source_id",
                        str(output_source.id),
                        pa.string(),
                    )
                )
            )

            match op:
                case Ok(table):
                    pass
                case InvalidArgumentError() as err:
                    return err

            tables[output_source.name] = Table(self.client, table)

        return Ok(tables)


@dataclasses.dataclass
class EmbedImageParameters:
    column_name: str
    model_name: str
    expected_vector_length: int


class ImageSpace(Space):
    """Spaces for embedding images."""

    _output_source: Source | None = None

    def __init__(
        self,
        client: system.Client,
        proto_self: models_pb2.Space,
        feature_view: FeatureView | None = None,
        output_source: Source | None = None,
    ):
        super().__init__(client, proto_self, feature_view)
        self._output_source = output_source

    def output_source(self):
        if self._output_source is not None:
            return Ok(self._output_source)
        match self.feature_view():
            case Ok(feature_view):
                return Ok(
                    feature_view.source_id_to_feature_view_source[
                        first(iter(feature_view.output_sources))
                    ].source
                )
            case NotFoundError() as err:
                return err

    def _sub_orm_objects(self, orm_object: orm.Space) -> Iterable[orm.Base]:
        return []

    @property
    def expected_coordinate_bitwidth(self) -> Literal[32]:
        return 32

    @property
    def model_name(self) -> str | None:
        if self.embed_image_parameters:
            return image_model_proto_to_name[
                self.embed_image_parameters.model_parameters.model
            ]
        return None

    @classmethod
    def create(
        cls,
        feature_view: FeatureView,
        client: system.Client | None = None,
        room_id: orm.RoomID | None = None,
    ) -> Ok[Self] | InvalidArgumentError:
        client = client or feature_view.client
        if len(feature_view.output_sources) != 1:
            return InvalidArgumentError(
                "feature view must have exactly one output source"
            )
        source = feature_view.source_id_to_feature_view_source[
            first(iter(feature_view.output_sources))
        ].source

        room_id = room_id or Defaults.get_default_room_id(client)
        proto_self = models_pb2.Space(
            feature_view_id=str(feature_view.id), room_id=str(room_id)
        )
        return Ok(
            cls(
                client,
                proto_self,
                feature_view,
                source,
            )
        )

    def with_embed_and_image(self, params: EmbedImageParameters) -> ImageSpace:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.space_parameters.CopyFrom(
            space_pb2.SpaceParameters(
                embed_image_parameters=embedding_models_pb2.EmbedImageParameters(
                    column_name=params.column_name,
                    model_parameters=embedding_models_pb2.ImageModelParameters(
                        model=name_to_proto_image_model.get(
                            params.model_name,
                            embedding_models_pb2.IMAGE_MODEL_UNSPECIFIED,
                        ),
                        ndim=params.expected_vector_length,
                    ),
                )
            )
        )
        return ImageSpace(
            self.client,
            proto_self,
            self.feature_view().unwrap_or_raise(),
            output_source=self.output_source().unwrap_or_raise(),
        )

    def embeddings_tables(self) -> Ok[Mapping[str, Table]] | InvalidArgumentError:
        model_name = self.model_name
        if not self.embed_image_parameters or model_name is None:
            return InvalidArgumentError(
                "space was not configured to produce embeddings"
            )
        match self.output_source():
            case Ok(output_source):
                pass
            case NotFoundError() as err:
                return InvalidArgumentError.from_(err)
        params = self.embed_image_parameters
        pk_field = output_source.table.schema.get_primary_key()
        if not pk_field:
            return InvalidArgumentError("output source must have a primary key")

        embedding_column_tmp_name = f"__embed-{uuid.uuid4()}"

        return (
            output_source.table.op_graph.embed_image_column(
                column_name=params.column_name,
                embedding_column_name=embedding_column_tmp_name,
                model_name=model_name,
                expected_vector_length=params.model_parameters.ndim,
                expected_coordinate_bitwidth=self.expected_coordinate_bitwidth,
            )
            .and_then(
                lambda t: t.select_columns([pk_field.name, embedding_column_tmp_name])
            )
            .and_then(
                lambda t: t.rename_columns(
                    {pk_field.name: "entity_id", embedding_column_tmp_name: "embedding"}
                )
            )
            .and_then(
                lambda t: t.add_literal_column(
                    "source_id",
                    str(output_source.id),
                    pa.string(),
                )
            )
            .map(lambda t: {output_source.name: Table(self.client, t)})
        )


SpecificSpace: TypeAlias = (
    RelationalSpace | SemanticSpace | TabularSpace | ImageSpace | UnknownSpace
)
