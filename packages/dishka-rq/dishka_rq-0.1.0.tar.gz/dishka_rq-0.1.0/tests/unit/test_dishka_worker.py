from typing import cast
from unittest.mock import Mock

import pytest
from dishka import Container, FromDishka
from fakeredis import FakeStrictRedis
from rq import Queue
from rq.job import Job

from dishka_rq import DishkaWorker

from .common import (
    APP_DEP_VALUE,
    REQUEST_DEP_VALUE,
    AppDep,
    AppMock,
    AppProvider,
    RequestDep,
)

# Supress CLIENT SETNAME warning from Worker. FakeRedis does not support it.
pytestmark = pytest.mark.filterwarnings("ignore:CLIENT SETNAME")


def app_job(a: FromDishka[AppDep], app_mock: FromDishka[AppMock]):
    app_mock(a)


def request_job(
    a: FromDishka[AppDep],
    r: FromDishka[RequestDep],
    mock: FromDishka[Mock],
):
    mock(r)


def job_without_deps(b: str) -> str:
    return b


def job_with_missing_dep(str: FromDishka[str]):
    pass  # pragma: no coverage


@pytest.fixture
def fake_redis_conn():
    return FakeStrictRedis()


@pytest.fixture
def worker(
    container: Container,
    fake_redis_conn: FakeStrictRedis,
):
    return DishkaWorker(
        ["test_queue"],
        container=container,
        connection=fake_redis_conn,
    )


@pytest.fixture
def queue(fake_redis_conn: FakeStrictRedis):
    return Queue(name="test_queue", connection=fake_redis_conn)


def test_worker_initialization(
    container: Container,
    fake_redis_conn: FakeStrictRedis,
):
    worker = DishkaWorker(
        ["test_queue"],
        container=container,
        connection=fake_redis_conn,
    )
    assert worker.dishka_container == container


def test_inject_app_deps(
    worker: DishkaWorker,
    container: Container,
    fake_redis_conn: FakeStrictRedis,
    app_provider: AppProvider,
):
    job = Job.create(
        func=app_job,
        kwargs={},
        connection=fake_redis_conn,
    )

    request_container = container().__enter__()
    worker.inject_deps(job, request_container)

    assert job.kwargs["a"] == APP_DEP_VALUE
    assert job.kwargs["app_mock"] == app_provider.app_mock


def test_inject_request_deps(
    worker: DishkaWorker,
    container: Container,
    fake_redis_conn: FakeStrictRedis,
    app_provider: AppProvider,
):
    job = Job.create(func=request_job, kwargs={}, connection=fake_redis_conn)

    request_container = container().__enter__()
    worker.inject_deps(job, request_container)

    assert job.kwargs["a"] == APP_DEP_VALUE
    assert job.kwargs["r"] == REQUEST_DEP_VALUE
    assert job.kwargs["mock"] == app_provider.mock


def test_inject_deps_with_existing_kwargs(
    container: Container,
    worker: DishkaWorker,
    fake_redis_conn: FakeStrictRedis,
):
    existing_kwargs = {"extra_param": "value"}
    job = Job.create(
        func=app_job,
        kwargs=existing_kwargs.copy(),
        connection=fake_redis_conn,
    )

    request_container = container().__enter__()
    worker.inject_deps(job, request_container)

    assert job.kwargs["extra_param"] == "value"
    assert job.kwargs["a"] == APP_DEP_VALUE


def test_inject_deps_without_dependencies(
    container: Container,
    worker: DishkaWorker,
    fake_redis_conn: FakeStrictRedis,
):
    job = Job.create(
        func=job_without_deps,
        kwargs={"b": "just string"},
        connection=fake_redis_conn,
    )

    request_container = container().__enter__()
    worker.inject_deps(job, request_container)

    assert job.kwargs == {"b": "just string"}


def test_perform_app_job(
    worker: DishkaWorker,
    fake_redis_conn: FakeStrictRedis,
    app_provider: AppProvider,
):
    queue = Queue(connection=fake_redis_conn)
    job = queue.enqueue(app_job)

    worker.perform_job(job, queue)

    cast(Mock, app_provider.app_mock).assert_called_once()
    app_provider.app_released.assert_not_called()

    worker.teardown()
    app_provider.app_released.assert_called()


def test_perform_request_job(
    worker: DishkaWorker,
    fake_redis_conn: FakeStrictRedis,
    app_provider: AppProvider,
):
    queue = Queue(connection=fake_redis_conn)
    job = queue.enqueue(request_job)

    worker.perform_job(job, queue)

    cast(Mock, app_provider.mock).assert_called_once()
    app_provider.app_released.assert_not_called()
    app_provider.request_released.assert_called()

    worker.teardown()
    app_provider.app_released.assert_called()


# def test_dependency_missing(
#     worker: DishkaWorker,
#     fake_redis_conn: FakeStrictRedis,
# ):
#     """Should not add missing dependency to function."""
#     queue = Queue(connection=fake_redis_conn)
#     job = queue.enqueue(job_with_missing_dep)

#     worker.perform_job(job, queue)
