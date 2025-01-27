import asyncio
from pprint import pprint

import aiohttp

from gitlab_async_client.client import GitlabHTTPClient


async def main():
    async with aiohttp.ClientSession() as session:
        client = GitlabHTTPClient(
            base_url='https://gitlab.mychili.id',
            access_token='oCUyQzYm4CEy-ydngy-6',
            session=session,
        )
        noteable_id = 22795
        noteable_iid = 597
        note_id = 118794
        a = await client.get_single_mr_note(project_id=87, mr_iid=597, note_id=118794)
        pprint(a)


if __name__ == '__main__':
    asyncio.run(main())
