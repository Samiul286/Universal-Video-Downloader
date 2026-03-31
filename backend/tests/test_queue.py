"""BE-U3: Queue enqueue/dequeue/max size. BE-U4: Queue state (size, list of job ids)."""
import pytest

from app.downloader.queue import DownloadQueue


@pytest.mark.asyncio
async def test_queue_enqueue_dequeue_max_size():
    q = DownloadQueue(max_size=2)
    assert await q.enqueue("job1") is True
    assert await q.enqueue("job2") is True
    assert await q.enqueue("job3") is False  # at max
    assert q.size == 2
    j = await q.dequeue()
    assert j == "job1"
    assert q.size == 1
    j2 = await q.dequeue()
    assert j2 == "job2"
    j3 = await q.dequeue()
    assert j3 is None


@pytest.mark.asyncio
async def test_queue_list_ids_consistent():
    q = DownloadQueue(max_size=10)
    await q.enqueue("a")
    await q.enqueue("b")
    ids = await q.list_ids()
    assert ids == ["a", "b"]
    await q.dequeue()
    ids2 = await q.list_ids()
    assert ids2 == ["b"]
    q.remove("b")
    ids3 = await q.list_ids()
    assert ids3 == []
