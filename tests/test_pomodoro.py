from datetime import datetime, timedelta

from freezegun import freeze_time

from jtravail import pomodoro


def test_start() -> None:
    status = pomodoro.status()

    assert status.stopped
    assert status.remaining is None

    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.start()
        status = pomodoro.status()

        assert status.pomodoro
        assert status.remaining is not None
        assert status.remaining.total_seconds() == 25 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))
        status = pomodoro.status()

        assert status.pomodoro
        assert status.remaining is not None
        assert status.remaining.total_seconds() == 24 * 60

        frozen_datetime.tick(delta=timedelta(seconds=25 * 60))
        status = pomodoro.status()

        assert status.pomodoro
        assert status.remaining is not None
        assert status.remaining.total_seconds() == -1 * 60


def test_pause() -> None:
    status = pomodoro.status()

    assert status.stopped
    assert status.remaining is None

    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.pause()
        status = pomodoro.status()

        assert status.paused
        assert status.remaining is not None
        assert status.remaining.total_seconds() == 5 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))
        status = pomodoro.status()

        assert status.paused
        assert status.remaining is not None
        assert status.remaining.total_seconds() == 4 * 60


def test_stop() -> None:
    pomodoro.start()
    pomodoro.stop()
    status = pomodoro.status()

    assert status.stopped
    assert status.remaining is None

    pomodoro.stop()
    status = pomodoro.status()

    assert status.stopped
    assert status.remaining is None
