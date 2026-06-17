"""Resolve workspace GitHub App credentials for session launch."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from swarmer.models.github_app import GitHubApp


async def get_workspace_github_app(
    workspace_id: int,
    db: AsyncSession,
    user_id: str = "",
) -> GitHubApp | None:
    """Return the configured GitHub App for a workspace, or None."""
    result = await db.execute(
        select(GitHubApp).where(
            GitHubApp.workspace_id == workspace_id,
            or_(
                GitHubApp.user_id == user_id,
                GitHubApp.shared == True,  # noqa: E712
                GitHubApp.user_id == "",
            ),
        )
    )
    apps = result.scalars().all()
    app = None
    if user_id:
        for candidate in apps:
            if candidate.user_id == user_id:
                app = candidate
                break
    if app is None and apps:
        app = apps[0]
    if app is None or not app.is_configured:
        return None
    return app
