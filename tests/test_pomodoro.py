from datetime import datetime, timedelta

from freezegun import freeze_time

from jtravail import pomodoro


def test_start() -> None:
    (status, remaining) = pomodoro.status()

    assert status == pomodoro.Status.STOPPED
    assert remaining is None

    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.start()
        (status, remaining) = pomodoro.status()

        assert status == pomodoro.Status.POMODORO
        assert remaining is not None
        assert remaining.total_seconds() == 25 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))
        (status, remaining) = pomodoro.status()

        assert status == pomodoro.Status.POMODORO
        assert remaining is not None
        assert remaining.total_seconds() == 24 * 60

        frozen_datetime.tick(delta=timedelta(seconds=25 * 60))
        (status, remaining) = pomodoro.status()

        assert status == pomodoro.Status.POMODORO
        assert remaining is not None
        assert remaining.total_seconds() == -1 * 60


def test_pause() -> None:
    (status, remaining) = pomodoro.status()

    assert status == pomodoro.Status.STOPPED
    assert remaining is None

    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.pause()
        (status, remaining) = pomodoro.status()

        assert status == pomodoro.Status.PAUSED
        assert remaining is not None
        assert remaining.total_seconds() == 5 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))
        (status, remaining) = pomodoro.status()

        assert status == pomodoro.Status.PAUSED
        assert remaining is not None
        assert remaining.total_seconds() == 4 * 60


def test_stop() -> None:
    pomodoro.start()
    pomodoro.stop()
    (status, remaining) = pomodoro.status()

    assert status == pomodoro.Status.STOPPED
    assert remaining is None

    pomodoro.stop()
    (status, remaining) = pomodoro.status()
