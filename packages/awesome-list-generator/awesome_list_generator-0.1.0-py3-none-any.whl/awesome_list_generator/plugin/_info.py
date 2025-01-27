import asyncio
from collections.abc import Iterable
from typing import Self

import pydantic

import awesome_list_generator as alg

from . import GitHubInfo


class ProjectInfo(pydantic.BaseModel):
    category: str = "others"
    github: GitHubInfo | None = None

    @property
    def name(self) -> str:
        if self.github:
            return self.github.full_name
        msg: str = "ProjectInfo must have a GitHubInfo to get the name"
        raise ValueError(msg)

    @property
    def url(self) -> str:
        if self.github:
            return self.github.html_url
        msg: str = "ProjectInfo must have a GitHubInfo to get the URL"
        raise ValueError(msg)

    @property
    def description(self) -> str | None:
        if self.github and self.github.description:
            return self.github.description
        return None

    @classmethod
    async def fetch(cls, config: alg.ProjectConfig) -> Self:
        return cls(
            category=config.category or "others",
            github=await GitHubInfo.fetch(config.github) if config.github else None,
        )


async def fetch_projects(projects: Iterable[alg.ProjectConfig]) -> list[ProjectInfo]:
    return await asyncio.gather(*[ProjectInfo.fetch(project) for project in projects])
