import dataclasses
import datetime
from collections.abc import Sequence
from typing import Generic, TypeVar, cast

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from google.protobuf import timestamp_pb2
from more_itertools import flatten

from corvic import orm
from corvic.result import InvalidArgumentError, Ok
from corvic_generated.model.v1alpha import models_pb2

UNCOMMITTED_ID_PREFIX = "__uncommitted_object-"

_Proto = (
    models_pb2.Resource
    | models_pb2.Source
    | models_pb2.FeatureView
    | models_pb2.Space
    | models_pb2.FeatureViewSource
    | models_pb2.Agent
    | models_pb2.Pipeline
    | models_pb2.Room
    | models_pb2.CompletionModel
)
_ID = TypeVar(
    "_ID",
    orm.ResourceID,
    orm.SourceID,
    orm.FeatureViewID,
    orm.SpaceID,
    orm.FeatureViewSourceID,
    orm.AgentID,
    orm.PipelineID,
    orm.RoomID,
    orm.CompletionModelID,
)


@dataclasses.dataclass
class _OrmIDs(Generic[_ID]):
    obj_id: _ID | None
    room_id: orm.RoomID | None


def _translate_orm_ids(
    proto_obj: _Proto, obj_id_class: type[_ID]
) -> Ok[_OrmIDs[_ID]] | orm.InvalidORMIdentifierError:
    if proto_obj.id.startswith(UNCOMMITTED_ID_PREFIX):
        obj_id = None
    else:
        obj_id = obj_id_class(proto_obj.id)
        match obj_id.to_db():
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok():
                pass

    match proto_obj:
        case (
            models_pb2.Resource()
            | models_pb2.Source()
            | models_pb2.FeatureView()
            | models_pb2.Space()
            | models_pb2.Agent()
            | models_pb2.Pipeline()
        ):
            room_id = orm.RoomID(proto_obj.room_id)
            match room_id.to_db():
                case orm.InvalidORMIdentifierError() as err:
                    return err
                case Ok():
                    pass
        case models_pb2.FeatureViewSource() | models_pb2.CompletionModel():
            room_id = None
        case models_pb2.Room():
            room_id = cast(orm.RoomID, obj_id)

    return Ok(_OrmIDs(obj_id, room_id))


def timestamp_orm_to_proto(
    timestamp_orm: datetime.datetime | None,
) -> timestamp_pb2.Timestamp | None:
    if timestamp_orm is not None:
        timestamp_proto = timestamp_pb2.Timestamp()
        timestamp_proto.FromDatetime(timestamp_orm)
    else:
        timestamp_proto = None
    return timestamp_proto


def resource_orm_to_proto(resource_orm: orm.Resource) -> models_pb2.Resource:
    return models_pb2.Resource(
        id=str(resource_orm.id),
        name=resource_orm.name,
        description=resource_orm.description,
        mime_type=resource_orm.mime_type,
        url=resource_orm.url,
        md5=resource_orm.md5,
        size=resource_orm.size,
        original_path=resource_orm.original_path,
        room_id=str(resource_orm.room_id),
        source_ids=[str(val.source_id) for val in resource_orm.source_associations],
        org_id=str(resource_orm.org_id),
        pipeline_id=str(resource_orm.pipeline_input_refs[-1].pipeline.id)
        if resource_orm.pipeline_input_refs
        else None,
        created_at=timestamp_orm_to_proto(resource_orm.created_at),
    )


def source_orm_to_proto(source_orm: orm.Source) -> models_pb2.Source:
    return models_pb2.Source(
        id=str(source_orm.id),
        name=source_orm.name,
        table_op_graph=source_orm.table_op_graph,
        room_id=str(source_orm.room_id),
        resource_id=str(source_orm.resource_associations[0].resource_id)
        if source_orm.resource_associations
        else "",
        org_id=str(source_orm.org_id),
        pipeline_id=str(source_orm.pipeline_output_refs[-1].pipeline.id)
        if source_orm.pipeline_output_refs
        else None,
        created_at=timestamp_orm_to_proto(source_orm.created_at),
    )


def agent_orm_to_proto(agent_orm: orm.Agent) -> models_pb2.Agent:
    return models_pb2.Agent(
        id=str(agent_orm.id),
        name=agent_orm.name,
        room_id=str(agent_orm.room_id),
        agent_parameters=agent_orm.parameters,
        org_id=str(agent_orm.org_id),
        created_at=timestamp_orm_to_proto(agent_orm.created_at),
    )


def feature_view_source_orm_to_proto(
    feature_view_source_orm: orm.FeatureViewSource,
) -> models_pb2.FeatureViewSource:
    return models_pb2.FeatureViewSource(
        id=str(feature_view_source_orm.id),
        source=source_orm_to_proto(feature_view_source_orm.source),
        table_op_graph=feature_view_source_orm.table_op_graph,
        drop_disconnected=feature_view_source_orm.drop_disconnected,
        org_id=str(feature_view_source_orm.org_id),
        created_at=timestamp_orm_to_proto(feature_view_source_orm.created_at),
    )


def feature_view_orm_to_proto(
    feature_view_orm: orm.FeatureView,
) -> models_pb2.FeatureView:
    return models_pb2.FeatureView(
        id=str(feature_view_orm.id),
        name=feature_view_orm.name,
        description=feature_view_orm.description,
        room_id=str(feature_view_orm.room_id),
        feature_view_output=feature_view_orm.feature_view_output,
        feature_view_sources=[
            feature_view_source_orm_to_proto(fvs)
            for fvs in feature_view_orm.feature_view_sources
        ],
        org_id=str(feature_view_orm.org_id),
        created_at=timestamp_orm_to_proto(feature_view_orm.created_at),
    )


def pipeline_orm_to_proto(
    pipeline_orm: orm.Pipeline,
) -> models_pb2.Pipeline:
    return models_pb2.Pipeline(
        id=str(pipeline_orm.id),
        name=pipeline_orm.name,
        room_id=str(pipeline_orm.room_id),
        resource_inputs={
            input_obj.name: resource_orm_to_proto(input_obj.resource)
            for input_obj in pipeline_orm.inputs
        },
        source_outputs={
            output_obj.name: source_orm_to_proto(output_obj.source)
            for output_obj in pipeline_orm.outputs
        },
        pipeline_transformation=pipeline_orm.transformation,
        org_id=str(pipeline_orm.org_id),
        description=pipeline_orm.description,
        created_at=timestamp_orm_to_proto(pipeline_orm.created_at),
    )


def space_orm_to_proto(space_orm: orm.Space) -> models_pb2.Space:
    return models_pb2.Space(
        id=str(space_orm.id),
        name=space_orm.name,
        description=space_orm.description,
        room_id=str(space_orm.room_id),
        space_parameters=space_orm.parameters,
        feature_view_id=str(space_orm.feature_view_id),
        auto_sync=space_orm.auto_sync if space_orm.auto_sync is not None else False,
        org_id=str(space_orm.org_id),
        created_at=timestamp_orm_to_proto(space_orm.created_at),
    )


def room_orm_to_proto(room_orm: orm.Room) -> models_pb2.Room:
    return models_pb2.Room(
        id=str(room_orm.id),
        name=room_orm.name,
        org_id=str(room_orm.org_id),
        created_at=timestamp_orm_to_proto(room_orm.created_at),
    )


def completion_model_orm_to_proto(
    completion_model_orm: orm.CompletionModel,
) -> models_pb2.CompletionModel:
    return models_pb2.CompletionModel(
        id=str(completion_model_orm.id),
        name=completion_model_orm.name,
        description=completion_model_orm.description,
        org_id=str(completion_model_orm.org_id),
        model_name=completion_model_orm.model_name,
        endpoint=completion_model_orm.endpoint,
        secret_api_key=completion_model_orm.secret_api_key,
        created_at=timestamp_orm_to_proto(completion_model_orm.created_at),
    )


def resource_proto_to_orm(
    proto_obj: models_pb2.Resource, session: sa_orm.Session
) -> Ok[orm.Resource] | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.ResourceID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    source_ids = list[orm.SourceID]()
    for source_id in proto_obj.source_ids:
        orm_id = orm.SourceID(source_id)
        match orm_id.to_db():
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok():
                source_ids.append(orm_id)
    orm_obj = orm.Resource(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        mime_type=proto_obj.mime_type,
        md5=proto_obj.md5,
        url=proto_obj.url,
        size=proto_obj.size,
        original_path=proto_obj.original_path,
        room_id=ids.room_id,
        source_associations=[
            orm.SourceResourceAssociation(source_id=src_id, resource_id=ids.obj_id)
            for src_id in source_ids
        ],
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
        for assn in orm_obj.source_associations:
            assn.org_id = orm_obj.org_id

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def pipeline_proto_to_orm(  # noqa: C901
    proto_obj: models_pb2.Pipeline, session: sa_orm.Session
) -> Ok[orm.Pipeline] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.PipelineID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit pipeline")

    orm_obj = orm.Pipeline(
        id=ids.obj_id,
        name=proto_obj.name,
        room_id=ids.room_id,
        transformation=proto_obj.pipeline_transformation,
        description=proto_obj.description,
    )

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    for name, val in proto_obj.resource_inputs.items():
        if any(input.name == name for input in orm_obj.inputs):
            continue
        match resource_proto_to_orm(val, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(resource_orm):
                if resource_orm.id:
                    resource_orm = session.merge(resource_orm)
                else:
                    session.add(resource_orm)
                session.merge(
                    orm.PipelineInput(
                        pipeline=orm_obj, resource=resource_orm, name=name
                    )
                )

    for name, val in proto_obj.source_outputs.items():
        if any(output.name == name for output in orm_obj.outputs):
            continue
        match source_proto_to_orm(val, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(source_orm):
                if source_orm.id:
                    source_orm = session.merge(source_orm)
                else:
                    session.add(source_orm)
                session.merge(
                    orm.PipelineOutput(pipeline=orm_obj, source=source_orm, name=name)
                )
    if proto_obj.org_id:
        org_id = orm.OrgID(proto_obj.org_id)
        orm_obj.org_id = org_id
        for obj in flatten((orm_obj.inputs, orm_obj.outputs)):
            obj.org_id = orm.OrgID(proto_obj.org_id)
    return Ok(orm_obj)


def source_proto_to_orm(
    proto_obj: models_pb2.Source, session: sa_orm.Session
) -> Ok[orm.Source] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.SourceID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")
    resource_id = orm.ResourceID(proto_obj.resource_id)
    if resource_id:
        associations = [
            orm.SourceResourceAssociation(source_id=ids.obj_id, resource_id=resource_id)
        ]
    else:
        associations = list[orm.SourceResourceAssociation]()

    orm_obj = orm.Source(
        id=ids.obj_id,
        name=proto_obj.name,
        table_op_graph=proto_obj.table_op_graph,
        room_id=ids.room_id,
        resource_associations=associations,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
        for assn in orm_obj.resource_associations:
            assn.org_id = orm.OrgID(proto_obj.org_id)
    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def agent_proto_to_orm(
    proto_obj: models_pb2.Agent, session: sa_orm.Session
) -> Ok[orm.Agent] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.AgentID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    orm_obj = orm.Agent(
        id=ids.obj_id,
        name=proto_obj.name,
        parameters=proto_obj.agent_parameters,
        room_id=ids.room_id,
    )

    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def space_proto_to_orm(
    proto_obj: models_pb2.Space, session: sa_orm.Session
) -> Ok[orm.Space] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.SpaceID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    feature_view_id = orm.FeatureViewID(proto_obj.feature_view_id)
    feature_view = session.get(orm.FeatureView, feature_view_id)
    if not feature_view:
        return InvalidArgumentError("feature view required to commit resource")

    orm_obj = orm.Space(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        room_id=ids.room_id,
        feature_view_id=feature_view_id,
        parameters=proto_obj.space_parameters,
        auto_sync=proto_obj.auto_sync,
        feature_view=feature_view,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)
    return Ok(orm_obj)


def feature_view_proto_to_orm(
    proto_obj: models_pb2.FeatureView, session: sa_orm.Session
) -> Ok[orm.FeatureView] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.FeatureViewID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass
    if not ids.room_id:
        return InvalidArgumentError("room id required to commit resource")

    feature_view_sources = list[orm.FeatureViewSource]()
    for fvs in proto_obj.feature_view_sources:
        match feature_view_source_proto_to_orm(fvs, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(orm_fvs):
                if orm_fvs.id:
                    orm_fvs = session.merge(orm_fvs)
                else:
                    session.add(orm_fvs)
                feature_view_sources.append(orm_fvs)

    orm_obj = orm.FeatureView(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        room_id=ids.room_id,
        feature_view_output=proto_obj.feature_view_output,
        feature_view_sources=feature_view_sources,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)
    return Ok(orm_obj)


def feature_view_source_proto_to_orm(
    proto_obj: models_pb2.FeatureViewSource, session: sa_orm.Session
) -> Ok[orm.FeatureViewSource] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match source_proto_to_orm(proto_obj.source, session):
        case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
            return err
        case Ok(source):
            pass

    if source.id:
        source = session.merge(source)
    else:
        session.add(source)
    orm_obj = orm.FeatureViewSource(
        table_op_graph=proto_obj.table_op_graph,
        drop_disconnected=proto_obj.drop_disconnected,
        source=source,
    )
    if proto_obj.org_id:
        orm_obj.org_id = orm.OrgID(proto_obj.org_id)
    return Ok(orm_obj)


def room_proto_to_orm(
    proto_obj: models_pb2.Room, session: sa_orm.Session
) -> Ok[orm.Room] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.RoomID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass

    orm_obj = orm.Room(
        id=ids.obj_id,
        name=proto_obj.name,
    )

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def completion_model_proto_to_orm(
    proto_obj: models_pb2.CompletionModel, session: sa_orm.Session
) -> Ok[orm.CompletionModel] | InvalidArgumentError:
    match _translate_orm_ids(proto_obj, orm.CompletionModelID):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(ids):
            pass

    orm_obj = orm.CompletionModel(
        id=ids.obj_id,
        name=proto_obj.name,
        description=proto_obj.description,
        model_name=proto_obj.model_name,
        endpoint=proto_obj.endpoint,
        secret_api_key=proto_obj.secret_api_key,
    )

    if ids.obj_id:
        orm_obj = session.merge(orm_obj)
    else:
        session.add(orm_obj)

    return Ok(orm_obj)


def source_delete_orms(
    orm_ids: Sequence[orm.SourceID],
    session: sa_orm.Session,
) -> Ok[None] | InvalidArgumentError:
    feat_view_refs = list(
        session.scalars(
            sa.select(orm.FeatureViewSource.id)
            .where(orm.FeatureViewSource.source_id.in_(orm_ids))
            .limit(1)
        )
    )

    if feat_view_refs:
        return InvalidArgumentError(
            "cannot delete a source that still has feature views"
        )
    session.execute(sa.delete(orm.Source).where(orm.Source.id.in_(orm_ids)))
    return Ok(None)


def pipeline_delete_orms(
    ids: Sequence[orm.PipelineID], session: sa_orm.Session
) -> Ok[None] | InvalidArgumentError:
    source_ids = [
        val[0]
        for val in session.execute(
            sa.select(orm.Source.id).where(
                orm.Source.id.in_(
                    sa.select(orm.PipelineOutput.source_id).where(
                        orm.PipelineOutput.pipeline_id.in_(ids)
                    )
                )
            )
        )
        if val[0] is not None
    ]
    match source_delete_orms(source_ids, session):
        case InvalidArgumentError() as err:
            return err
        case Ok():
            pass

    session.execute(
        sa.delete(orm.Resource).where(
            orm.Resource.id.in_(
                sa.select(orm.PipelineInput.resource_id)
                .join(orm.Pipeline)
                .where(orm.Pipeline.id.in_(ids))
            )
        )
    )
    session.execute(sa.delete(orm.Pipeline).where(orm.Pipeline.id.in_(ids)))
    return Ok(None)


def resource_delete_orms(
    ids: Sequence[orm.ResourceID],
    session: orm.Session,
) -> Ok[None] | InvalidArgumentError:
    pipeline_refs = list(
        session.execute(
            sa.select(orm.PipelineInput.pipeline_id)
            .where(orm.PipelineInput.resource_id.in_(ids))
            .limit(1)
        )
    )

    if pipeline_refs:
        return InvalidArgumentError(
            "sources exist that reference resources to be deleted"
        )
    session.execute(sa.delete(orm.Resource).where(orm.Resource.id.in_(ids)))
    return Ok(None)


def agent_delete_orms(
    ids: Sequence[orm.AgentID], session: orm.Session
) -> Ok[None] | InvalidArgumentError:
    session.execute(sa.delete(orm.Agent).where(orm.Agent.id.in_(ids)))
    return Ok(None)


def feature_view_source_delete_orms(
    ids: Sequence[orm.FeatureViewSourceID], session: orm.Session
) -> Ok[None] | InvalidArgumentError:
    feat_view_refs = list(
        session.execute(
            sa.select(orm.FeatureView.id)
            .where(
                orm.FeatureView.id.in_(
                    sa.select(orm.FeatureViewSource.feature_view_id).where(
                        orm.FeatureViewSource.id.in_(ids)
                    )
                )
            )
            .limit(1)
        )
    )
    if feat_view_refs:
        return InvalidArgumentError(
            "feature views exist that reference feature_view_sources to be deleted"
        )

    session.execute(
        sa.delete(orm.FeatureViewSource).where(orm.FeatureViewSource.id.in_(ids))
    )
    return Ok(None)


def feature_view_delete_orms(
    ids: Sequence[orm.FeatureViewID], session: orm.Session
) -> Ok[None] | InvalidArgumentError:
    space_refs = list(
        session.execute(
            sa.select(orm.Space.id).where(orm.Space.feature_view_id.in_(ids))
        )
    )
    if space_refs:
        return InvalidArgumentError(
            "spaces exist that reference feature_views to be deleted"
        )
    session.execute(sa.delete(orm.FeatureView).where(orm.FeatureView.id.in_(ids)))
    return Ok(None)


def space_delete_orms(
    ids: Sequence[orm.SpaceID], session: orm.Session
) -> Ok[None] | InvalidArgumentError:
    session.execute(sa.delete(orm.Space).where(orm.Space.id.in_(ids)))
    return Ok(None)


def room_delete_orms(
    ids: Sequence[orm.RoomID], session: orm.Session
) -> Ok[None] | InvalidArgumentError:
    source_refs = list(
        session.scalars(sa.select(orm.Source).where(orm.Source.room_id == ids).limit(1))
    )
    if source_refs:
        return InvalidArgumentError("cannot delete a room that still has sources")

    session.execute(sa.delete(orm.Room).where(orm.Room.id == ids))
    return Ok(None)


def completion_model_delete_orms(
    ids: Sequence[orm.CompletionModelID],
    session: orm.Session,
) -> Ok[None] | InvalidArgumentError:
    session.execute(
        sa.delete(orm.CompletionModel).where(orm.CompletionModel.id.in_(ids))
    )
    return Ok(None)
