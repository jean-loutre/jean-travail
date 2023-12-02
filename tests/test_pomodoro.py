from datetime import datetime, timedelta

from freezegun import freeze_time

from jtravail.pomodoro import Pomodoro


def test_start(pomodoro: Pomodoro) -> None:
    assert pomodoro.stopped
    assert pomodoro.remaining == timedelta(0)

    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.start()

        assert pomodoro.working
        assert pomodoro.remaining.total_seconds() == 25 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))

        assert pomodoro.working
        assert pomodoro.remaining.total_seconds() == 24 * 60

        frozen_datetime.tick(delta=timedelta(seconds=25 * 60))

        assert pomodoro.remaining.total_seconds() == -1 * 60


def test_pause(pomodoro: Pomodoro) -> None:
    with freeze_time(datetime.now()) as frozen_datetime:
        pomodoro.pause()
        assert pomodoro.paused
        assert pomodoro.remaining.total_seconds() == 5 * 60

        frozen_datetime.tick(delta=timedelta(seconds=60))

        assert pomodoro.paused
        assert pomodoro.remaining.total_seconds() == 4 * 60

        pomodoro.pause()

        # Calling pause during pause doesn't reset the counter
        assert pomodoro.paused
        assert pomodoro.remaining.total_seconds() == 4 * 60

        pomodoro.start()
        pomodoro.pause()

        assert pomodoro.paused
        assert pomodoro.remaining.total_seconds() == 5 * 60


def test_save_stat_on_pause(pomodoro: Pomodoro) -> None:
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
            assert log[0].type == pomodoro.WORKING


def test_stop(pomodoro: Pomodoro) -> None:
    pomodoro.start()
    pomodoro.stop()

    assert pomodoro.stopped
    assert pomodoro.remaining == timedelta(0)

    pomodoro.stop()

    assert pomodoro.stopped
    assert pomodoro.remaining == timedelta(0)
