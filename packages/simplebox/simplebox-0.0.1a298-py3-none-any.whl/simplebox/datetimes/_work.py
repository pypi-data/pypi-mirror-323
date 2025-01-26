#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
from collections import defaultdict
from collections.abc import Iterable, Callable
from datetime import datetime, date, time, timedelta
from typing import Optional, Union

from dateutil.rrule import rrule, DAILY

from ._datetype import DateType, DateTimeType, TimeType, _handle_time_type, _handle_date_type, _handle_datetime_type, \
    _handle_diff_type

__all__ = []

DayCategory = Union[Iterable[DateType], dict[DateType, Iterable[Iterable[TimeType, TimeType], ...]]]


class WorkCalculator:
    """
    Calculate working times
    """

    def __init__(self, holiday: Optional[DayCategory] = None, works: Optional[DayCategory] = None,
                 time_start: Optional[TimeType] = None, time_end: Optional[TimeType] = None):
        """
        :param holiday: holiday configuration, if it is a list or tuple, only date will be used. If it is a dictionary,
                        with date as the key, a date can be configured with multiple time ranges,
                        each time range being a list or tuple, containing two elements: start and end times.

                        ex1: [date(1971, 1, 1), date(1971, 1, 2)]
                        ex2: [datetime(1971, 1, 1, 9, 0, 0), datetime(1971, 1, 2, 9, 0, 0)]
                        ex3: {"1971-01-01": [
                                    [time(*[9, 0, 0]), time(*[11, 59, 59])],  # start and end, valid time range.
                                    [time(*[13, 0, 0]), time(*[17, 59, 59])]  # start and end, valid time range.
                            ]}
                        If the date spans days, you need to split it into two days。

        :param works: Work configuration, refer to holiday
        """
        if not isinstance(holiday, (Iterable, dict, type(None))):
            raise TypeError(f"expected type iterable or dict, got '{type(holiday).__name__}'")
        self.__time_start_ = _handle_time_type(time_start or time(9, 0, 0))
        self.__time_end_ = _handle_time_type(time_end or time(18, 0, 0))
        self.__holidays: dict[date, list[list[time, time], ...]] = defaultdict(list)
        self.__workdays: dict[date, list[list[time, time], ...]] = defaultdict(list)
        self.__parser_day_category(holiday, self.__holidays)
        self.__parser_day_category(works, self.__workdays)

    @staticmethod
    def __parser_day_category(categories, container: dict[date, list[list[time, time], ...]]):
        if categories is not None:
            if isinstance(categories, Iterable):
                for category in categories:
                    dt = _handle_date_type(category)
                    container[dt] = []
            elif isinstance(categories, dict):
                for ket_of_date, value_of_times in container.items():
                    key = _handle_date_type(ket_of_date)
                    if not value_of_times:
                        for value_of_time in value_of_times:
                            if length := len(value_of_time) != 2:
                                raise ValueError(
                                    f"'{ket_of_date}' expected time range list length is 2, but got {length}")
                            range_time = [_handle_time_type(value_of_time[0]), _handle_time_type(value_of_time[1])]
                            range_time.sort()
                            container.get(key).append(range_time)

    @staticmethod
    def __check_time_in_range(t: time, range_t: list[list[time, time], ...]) -> bool:
        return any(rt[0] <= t <= rt[1] for rt in range_t)

    @staticmethod
    def __parser_start_time(start: time, holidays: list[list[time, time]]):
        new = []
        found = False
        for holiday in holidays:
            if not found and holiday[0] <= start <= holiday[1]:
                new.append([start, holiday[1]])
                found = True
            else:
                new.append(holiday)
        return new

    @staticmethod
    def __parser_end_time(end: time, holidays: list[list[time, time]]):
        new = []
        found = False
        for holiday in holidays:
            if not found and holiday[0] <= end <= holiday[1]:
                new.append([holiday[0], end])
                found = True
            else:
                new.append(holiday)
        return new

    @staticmethod
    def __cal_use_time(start: time, end: time, holidays: list[list[time, time]]):
        total = timedelta()
        today = datetime.now().date()
        for h_start, h_end in holidays:
            total += (datetime.combine(today, h_end) - datetime.combine(today, h_start))

        total = (datetime.combine(today, end) - datetime.combine(today, start)) - total
        return total

    def is_weekend(self, day: DateType or DateTimeType) -> bool:
        """check date is weekend"""
        # noinspection PyBroadException
        try:
            dt = _handle_datetime_type(day)
            return dt.date().weekday() >= 5
        except BaseException:
            try:
                dt = _handle_date_type(day)
                return dt.weekday() >= 5
            except BaseException:
                raise TypeError(f'excepted date or datetime, got {type(day).__name__}.')

    def is_holiday(self, day: DateType or DateTimeType) -> bool:
        """check date is holiday, not working is holiday"""
        return not self.is_workday(day)

    def is_workday(self, day: DateType or DateTimeType) -> bool:
        """check date is working day"""
        # noinspection PyBroadException
        try:
            dt = _handle_datetime_type(day)
            workday_list = self.__workdays.get(dt.date())
            holiday_list = self.__holidays.get(dt.date())
            in_workday_list = self.__check_time_in_range(dt.time(), workday_list)
            in_holiday_list = self.__check_time_in_range(dt.time(), holiday_list)

            # compensatory leave work
            if dt not in self.__holidays and self.is_weekend(day) and dt in self.__workdays:
                return in_workday_list and not in_holiday_list
            else:
                return dt not in self.__holidays and not self.is_weekend(day) \
                    and in_workday_list and not in_holiday_list
        except BaseException:
            try:
                dt = _handle_date_type(day)
                # compensatory leave work
                if dt not in self.__holidays and self.is_weekend(day) and dt in self.__workdays:
                    return True
                else:
                    return dt not in self.__holidays and not self.is_weekend(day)
            except BaseException:
                raise TypeError(f'excepted date or datetime, got {type(day).__name__}.')

    def workday_interval(self, start: DateTimeType, end: DateTimeType, date_start: Optional[TimeType] = None,
                         date_end: Optional[TimeType] = None) -> timedelta:
        """
        calculate work datetime.
        """
        return self.datetime_interval(self.is_workday, start, end, date_start, date_end)

    def datetime_interval(self, condition: Callable[..., [bool]], start: DateTimeType, end: DateTimeType,
                          time_start: Optional[TimeType] = None,
                          time_end: Optional[TimeType] = None) -> timedelta:
        """
        calculate datetime diff.
        :param condition: The condition of the hit time.
        :param start: The start time of a period of consecutive date time.
        :param end: The end time of a period of consecutive date time.
        :param time_start: The start time of the day
        :param time_end: The end time of the day
        :return:
        """
        start_ = _handle_datetime_type(start)
        end_ = _handle_datetime_type(end)
        if start_ > end_:
            start_, end_ = end_, start_

        time_start_ = _handle_time_type(time_start or self.__time_start_)
        time_end_ = _handle_time_type(time_end or self.__time_end_)

        if datetime.combine(datetime.today(), time_start_) > datetime.combine(datetime.today(), time_end_):
            time_end_, time_start_ = time_start_, time_end_

        total_seconds = timedelta()
        if start_.date() == end_.date():
            holidays = self.__parser_start_time(start_.time(), self.__holidays.get(start_.date(), []))
            holidays = self.__parser_end_time(time_end_, holidays)
            total_seconds += self.__cal_use_time(start_.time(), end_.time(), holidays)
        else:
            for dt in rrule(DAILY, dtstart=start_, count=(end_.date() - start_.date()).days + 1):
                dt_date = dt.date()
                if condition(dt):
                    if dt_date == start_.date():
                        holidays = self.__parser_start_time(start_.time(), self.__holidays.get(dt_date, []))
                        holidays = self.__parser_end_time(time_end_, holidays)
                        total_seconds += self.__cal_use_time(start_.time(), time_end_, holidays)
                    elif dt_date == end_.date():
                        holidays = self.__parser_end_time(time_start_, self.__holidays.get(dt_date, []))
                        holidays = self.__parser_end_time(end_.time(), holidays)
                        total_seconds += self.__cal_use_time(time_start_, end_.time(), holidays)
                    else:
                        holidays = self.__parser_start_time(time_start_, self.__holidays.get(dt_date, []))
                        holidays = self.__parser_end_time(time_end_, holidays)
                        total_seconds += self.__cal_use_time(time_start_, time_end_, holidays)
        return total_seconds

    def __postponed_workday(self, d: date, condition: Callable[..., [bool]] = None, is_before: bool = True):
        if condition is None:
            condition = self.is_workday
        if condition(d):
            return d
        tmp = d + timedelta(days=1 if is_before else -1)
        return self.__postponed_workday(tmp, condition, is_before=is_before)

    def cal_workday_datetime(self, src_dt: DateTimeType, diff: Union[timedelta, int, float],
                             time_start: Optional[TimeType] = None,
                             time_end: Optional[TimeType] = None) -> DateTimeType:
        return self.cal_datetime(self.is_workday, src_dt, diff, time_start, time_end)

    def cal_datetime(self, condition: Callable[..., [bool]], src_dt: DateTimeType, diff: Union[timedelta, int, float],
                     time_start: Optional[TimeType] = None,
                     time_end: Optional[TimeType] = None) -> DateTimeType:
        """
        Calculate the date after src_dt increase or decrease the diff.
        :param condition:
        :param src_dt:
        :param diff:
        :param time_start:
        :param time_end:
        """
        def future(dt):
            ref_datetime = datetime.combine(dt.date(), dt.time())
            d = self.__postponed_workday(ref_datetime.date(), condition=condition)
            if diff_int == 0:
                if d == src_ref_datetime_.date():
                    ref_datetime = datetime.combine(d, src_ref_datetime_.time())
                else:
                    ref_datetime = datetime.combine(d, time_start_)
            else:
                if d == src_ref_datetime_.date():
                    ref_datetime = datetime.combine(d, src_ref_datetime_.time())
                    for _ in range(diff_int):
                        ref_datetime = datetime.combine(
                            self.__postponed_workday(ref_datetime.date() + timedelta(days=1), condition=condition),
                            ref_datetime.time())
                else:
                    ref_datetime = datetime.combine(d, time_start_)
                    for _ in range(diff_int):
                        ref_datetime = datetime.combine(
                            self.__postponed_workday(ref_datetime.date() + timedelta(days=1), condition=condition),
                            time_start_)
            day_time = datetime.combine(datetime.today(), ref_datetime.time())
            if day_time < start_datetime:
                day_time = datetime.combine(datetime.today(), time_start_)
                ref_datetime = datetime.combine(ref_datetime.date(), time_start_)
            if day_time <= end_datetime:
                today_rem_diff = end_datetime - day_time
                if diff_dec_to_sec <= today_rem_diff.seconds:
                    return ref_datetime + timedelta(seconds=diff_dec_to_sec)
                else:
                    rem_sec = diff_dec_to_sec - today_rem_diff.seconds
                    ref_datetime = self.__postponed_workday(ref_datetime + timedelta(days=1), condition=condition)
                    return datetime.combine(ref_datetime.date(), time_start_) + timedelta(seconds=rem_sec)
            else:
                ref_datetime = datetime.combine(
                    self.__postponed_workday(ref_datetime + timedelta(days=1), condition=condition), time_start_)
                return datetime.combine(ref_datetime.date(), time_start_) + timedelta(seconds=diff_dec_to_sec)

        def ago(dt: datetime):
            ref_datetime = datetime.combine(dt.date(), dt.time())
            d = self.__postponed_workday(ref_datetime.date(), condition=condition, is_before=False)
            if diff_int == 0:
                if d == src_ref_datetime_.date():
                    ref_datetime = datetime.combine(d, src_ref_datetime_.time())
                else:
                    ref_datetime = datetime.combine(d, time_end_)
            else:
                if d == src_ref_datetime_.date():
                    ref_datetime = datetime.combine(d, src_ref_datetime_.time())
                    for _ in range(int(abs(diff_int))):
                        # s
                        ref_datetime = datetime.combine(
                            self.__postponed_workday(ref_datetime.date() + timedelta(days=-1), condition=condition,
                                                     is_before=False),
                            ref_datetime.time())
                else:
                    ref_datetime = datetime.combine(d, time_end_)
                    for _ in range(int(abs(diff_int))):
                        ref_datetime = datetime.combine(
                            self.__postponed_workday(ref_datetime.date() + timedelta(days=-1), condition=condition,
                                                     is_before=False),
                            time_end_)
            day_time = datetime.combine(datetime.today(), ref_datetime.time())
            if day_time < start_datetime:
                day_time = datetime.combine(
                    self.__postponed_workday(datetime.today() + timedelta(days=-1), condition=condition,
                                             is_before=False), time_end_)
                ref_datetime = datetime.combine(
                    self.__postponed_workday(ref_datetime.date() + timedelta(days=-1), condition=condition,
                                             is_before=False), time_end_)
                today_rem_diff = day_time - start_datetime
                if diff_dec_to_sec <= today_rem_diff.seconds:
                    return ref_datetime + timedelta(seconds=-diff_dec_to_sec)
                else:
                    rem_sec = diff_dec_to_sec - today_rem_diff.seconds
                    ref_datetime = self.__postponed_workday(ref_datetime + timedelta(days=-1), condition=condition,
                                                            is_before=False)
                    return datetime.combine(ref_datetime.date(), time_start_) + timedelta(seconds=-rem_sec)
            else:
                if day_time < end_datetime:
                    ref_datetime = datetime.combine(
                        self.__postponed_workday(ref_datetime, condition=condition, is_before=False),
                        ref_datetime.time())
                else:
                    ref_datetime = datetime.combine(
                        self.__postponed_workday(ref_datetime, condition=condition, is_before=False),
                        time_end_)
                return datetime.combine(ref_datetime.date(), ref_datetime.time()) + timedelta(seconds=-diff_dec_to_sec)

        diff_ = _handle_diff_type(diff)
        time_start_ = _handle_time_type(time_start or self.__time_start_)
        time_end_ = _handle_time_type(time_end or self.__time_end_)

        start_datetime = datetime.combine(datetime.today(), time_start_)
        end_datetime = datetime.combine(datetime.today(), time_end_)
        if start_datetime > end_datetime:
            time_end_, time_start_ = time_start_, time_end_

        src_ref_datetime_ = _handle_datetime_type(src_dt)

        # Reference datetime
        if condition(src_ref_datetime_):
            ref_datetime_ = datetime.combine(src_ref_datetime_.date(), src_ref_datetime_.time())
        else:
            ref_datetime_ = datetime.combine(src_ref_datetime_.date(), time_start_)
        diff_dec, diff_int = math.modf(diff_)
        diff_int = int(diff_int)
        diff_dec_to_sec = abs(diff_dec) * (end_datetime - start_datetime).seconds

        if diff_ >= 0:
            # go to the future
            return future(ref_datetime_)

        else:
            # turn the clock back
            return ago(ref_datetime_)
