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


def test_save_stat_on_pause() -> None:
    start_date = datetime.now()
    with freeze_time(start_date) as frozen_datetime:
        pomodoro.start()
        delta = timedelta(seconds=24 * 60)
        frozen_datetime.tick(delta=delta)
        pomodoro.pause()

        with pomodoro.get_log() as log:
            log = list(log)
            assert len(log) == 1
            assert log[0].start == start_date
            assert log[0].end == start_date + delta
            assert log[0].duration == delta
            assert log[0].type == pomodoro.Status.POMODORO


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
