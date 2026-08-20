from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

@dataclass
class Visibility:
    scid: Optional[str]
    likes: Optional[str]
    stars: Optional[str]
    following: Optional[str]
    followers: Optional[str]
    posts: Optional[str]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Visibility:
        return cls(
            scid=data.get("scid"),
            likes=data.get("likes"),
            stars=data.get("stars"),
            following=data.get("following"),
            followers=data.get("followers"),
            posts=data.get("posts"),
        )


@dataclass
class Relationship:
    viewer_blocks_profile: Optional[bool]
    profile_blocks_viewer: Optional[bool]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Relationship:
        return cls(
            viewer_blocks_profile=data.get("viewer_blocks_profile"),
            profile_blocks_viewer=data.get("profile_blocks_viewer"),
        )


@dataclass
class User:
    id: int
    name: Optional[str]
    nyaitter_id: Optional[str]
    me: Optional[str]
    header_image: Optional[str]
    icon_data: Optional[str]
    icon_available: Optional[bool]
    account_state: Optional[str]
    admin: Optional[bool]
    verify: Optional[bool]
    is_imposter: Optional[bool]
    visibility: Optional[Visibility]
    relationship: Optional[Relationship]
    following_count: Optional[int]
    follower_count: Optional[int]
    post_count: Optional[int]
    media_count: Optional[int]
    pinned_post_id: Optional[int]
    created_at: Optional[datetime]
    client: "Client"

    @classmethod
    def from_json(cls, data: Dict[str, Any], client: "Client") -> User:
        u: Dict[str, Any] = data.get("user", data)

        visibility = (
            Visibility.from_json(u["visibility"])
            if isinstance(u.get("visibility"), dict)
            else None
        )

        relationship = (
            Relationship.from_json(u["relationship"])
            if isinstance(u.get("relationship"), dict)
            else None
        )

        created_at = (
            datetime.fromisoformat(u["created_at"])
            if isinstance(u.get("created_at"), str)
            else None
        )

        return cls(
            id=u["id"],
            name=u.get("name"),
            nyaitter_id=u.get("nyaitter_id"),
            me=u.get("me"),
            header_image=u.get("header_image"),
            icon_data=u.get("icon_data"),
            icon_available=u.get("icon_available"),
            account_state=u.get("account_state"),
            admin=u.get("admin"),
            verify=u.get("verify"),
            is_imposter=u.get("is_imposter"),
            visibility=visibility,
            relationship=relationship,
            following_count=u.get("following_count"),
            follower_count=u.get("follower_count"),
            post_count=u.get("post_count"),
            media_count=u.get("media_count"),
            pinned_post_id=u.get("pinned_post_id"),
            created_at=created_at,
            client=client
        )

    async def re_fetch(self) -> User:
        new = await self.client.fetch_user(self.id)
        self.__dict__.update(new.__dict__)
        return self
