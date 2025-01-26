"""Simple async controller to intermittently re-send `file_progress` to refresh the 30-second client side timeout."""

__all__ = ['FakeFileProgress']

from simplyprint_ws_client.core.client import Client
from simplyprint_ws_client.core.state import FileProgressStateEnum
from simplyprint_ws_client.shared.utils.backoff import Backoff, ConstantBackoff
from simplyprint_ws_client.shared.utils.stoppable import AsyncStoppable


class FakeFileProgress(AsyncStoppable):
    client: Client
    backoff: Backoff

    def __init__(self, client: Client, **kwargs) -> None:
        super().__init__(**kwargs)
        self.client = client
        self.backoff = ConstantBackoff(5)

    async def run(self):
        is_downloading = False

        while not self.is_stopped():
            if not is_downloading:
                await self.client.wait_for_changes()

            is_downloading = self.client.printer.file_progress.state == FileProgressStateEnum.DOWNLOADING

            if not is_downloading:
                continue

            self.client.printer.file_progress.model_set_changed("state", "progress")

            await self.wait(self.backoff.delay())
