from .user import User
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Dict,
    Optional,
    TYPE_CHECKING
)
if TYPE_CHECKING:
    from .client import Client

@dataclass
class Post:
    announcement:bool
    attachments: list #後で制作
    author: User
    content: str
    created_at: datetime
    id: int
    like_count: int
    liked_by_me: bool
    lock: bool
    mask: bool
    private: bool
    reply_count: int
    reply_id: Optional[int]
    reply_to_post: Optional["Post"]
    repost_count: int
    repost_to: Optional[int]
    reposted_post: Optional["Post"]
    star_count: int
    starred_by_me: bool
    user: User
    user_id: int
    client: "Client"

    @classmethod
    def from_json(cls, data: Dict[str, Any], client: "Client") -> "Post":
        p: Dict[str, Any] = data.get("post", data)

        reply_to_post = (
            Post.from_json(p["reply_to_post"])
            if isinstance(p.get("reply_to_post"), dict)
            else None
        )
        reposted_post = (
            Post.from_json(p["reposted_post"])
            if isinstance(p.get("reposted_post"), dict)
            else None
        )
        return cls(
            announcement=p["announcement"],
            attachments=p["attachments"],
            author=User.from_json(p["author"], client),
            content=p["content"],
            created_at=datetime.fromisoformat(p["created_at"]),
            id=p["id"],
            like_count=p["like_count"],
            liked_by_me=p["liked_by_me"],
            lock=p["lock"],
            mask=p["mask"],
            private=p["private"],
            reply_count=p["reply_count"],
            reply_id=p.get("reply_id"),
            reply_to_post=reply_to_post,
            repost_count=p["repost_count"],
            repost_to=p.get("repost_to"),
            reposted_post=reposted_post,
            star_count=p["star_count"],
            starred_by_me=p["starred_by_me"],
            user=User.from_json(p["user"], client),
            user_id=p["userid"],
            client=client
        )
