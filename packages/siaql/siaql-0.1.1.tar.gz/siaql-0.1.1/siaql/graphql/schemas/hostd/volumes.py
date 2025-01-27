import strawberry
from typing import List
from strawberry.types import Info

from siaql.graphql.schemas.types import AddVolumeRequest, ResizeVolumeRequest, UpdateVolumeRequest, Volume, VolumeMeta
from siaql.graphql.resolvers.hostd import HostdBaseResolver
from siaql.graphql.resolvers.filter import FilterInput, SortInput, PaginationInput
from typing import Optional


@strawberry.type
class VolumeQueries:
    @strawberry.field
    async def hostd_volumes(
        self,
        info: Info,
        filter: Optional[FilterInput] = None,
        sort: Optional[SortInput] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> List[VolumeMeta]:
        """Get list of volumes"""
        return await HostdBaseResolver.handle_api_call(
            info, "get_volumes", filter_input=filter, sort_input=sort, pagination_input=pagination
        )

    @strawberry.field
    async def hostd_volume(
        self,
        info: Info,
        id: int,
        filter: Optional[FilterInput] = None,
        sort: Optional[SortInput] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> VolumeMeta:
        """Get specific volume"""
        return await HostdBaseResolver.handle_api_call(
            info, "get_volume", id=id, filter_input=filter, sort_input=sort, pagination_input=pagination
        )


@strawberry.type
class VolumeMutations:
    @strawberry.mutation
    async def hostd_add_volume(self, info: Info, req: AddVolumeRequest.Input) -> Volume:
        """Add a new volume"""
        return await HostdBaseResolver.handle_api_call(info, "post_volume", req=req)

    @strawberry.mutation
    async def hostd_update_volume(self, info: Info, id: int, req: UpdateVolumeRequest.Input) -> bool:
        """Update volume settings"""
        await HostdBaseResolver.handle_api_call(info, "put_volume", id=id, req=req)
        return True

    @strawberry.mutation
    async def hostd_delete_volume(self, info: Info, id: int, force: bool = False) -> bool:
        """Delete a volume"""
        await HostdBaseResolver.handle_api_call(info, "delete_volume", id=id, force=force)
        return True

    @strawberry.mutation
    async def hostd_resize_volume(self, info: Info, id: int, req: ResizeVolumeRequest.Input) -> bool:
        """Resize a volume"""
        await HostdBaseResolver.handle_api_call(info, "put_volume_resize", id=id, req=req)
        return True

    @strawberry.mutation
    async def hostd_cancel_volume_operation(self, info: Info, id: int) -> bool:
        """Cancel ongoing volume operation"""
        await HostdBaseResolver.handle_api_call(info, "delete_volume_cancel_op", id=id)
        return True
