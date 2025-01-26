import datetime
import zoneinfo
from pathlib import Path

from icalendar import (
    Alarm,
    Calendar,
    Event,
    vCalAddress,
    vDatetime,
    vText,
)

from lunar_birthday_ical.lunar import get_future_lunar_equivalent_date
from lunar_birthday_ical.pastebin import pastebin_helper
from lunar_birthday_ical.utils import get_logger

logger = get_logger(__name__)


def get_local_datetime(
    local_date: datetime.date | str,
    local_time: datetime.time | str,
    timezone: zoneinfo.ZoneInfo,
) -> datetime.datetime:
    if not isinstance(local_date, datetime.date):
        local_date = datetime.datetime.strptime(local_date, "%Y-%m-%d").date()
    if not isinstance(local_time, datetime.time):
        local_time = datetime.datetime.strptime(local_time, "%H:%M:%S").time()

    local_datetime = datetime.datetime.combine(local_date, local_time, timezone)

    return local_datetime


def local_datetime_to_utc_datetime(
    local_datetime: datetime.datetime,
) -> datetime.datetime:
    # 将 local_datetime "强制"转换为 UTC 时间, 注意 local_datetime 需要携带 tzinfo 信息
    utc = zoneinfo.ZoneInfo("UTC")
    # 这里宁可让它抛出错误信息, 也不要设置 默认值
    utc_datetime = local_datetime.replace(tzinfo=utc) - local_datetime.utcoffset()

    return utc_datetime


def add_reminders_to_event(event: Event, reminders: list, summary: str) -> None:
    # 添加提醒
    for reminder_days in reminders:
        alarm = Alarm()
        trigger_time = datetime.timedelta(days=-reminder_days)
        alarm.add("action", "DISPLAY")
        alarm.add("description", f"Reminder: {summary}")
        alarm.add("trigger", trigger_time)
        event.add_component(alarm)


def add_attendees_to_event(event: Event, attendees: list) -> None:
    # 添加与会者
    for attendee_email in attendees:
        attendee = vCalAddress(f"mailto:{attendee_email}")
        attendee.params["cn"] = vText(attendee_email.split("@")[0])
        attendee.params["role"] = vText("REQ-PARTICIPANT")
        event.add("attendee", attendee)


def add_event_to_calendar(
    calendar: Calendar,
    dtstart: datetime.datetime,
    dtend: datetime.datetime,
    summary: str,
    reminders: list[int],
    attendees: list[str],
) -> None:
    event = Event()
    event.add("dtstart", vDatetime(dtstart))
    event.add("dtend", vDatetime(dtend))
    event.add("summary", summary)

    add_reminders_to_event(event, reminders, summary)
    add_attendees_to_event(event, attendees)

    calendar.add_component(event)


def create_calendar(config: dict, output: Path) -> None:
    calendar_name = config.get("global").get("calendar_name")
    timezone_name = config.get("global").get("timezone")
    try:
        timezone = zoneinfo.ZoneInfo(timezone_name)
    except Exception:
        logger.error("Invalid timezone: %s", timezone_name)

    calendar = Calendar()
    calendar.add("PRODID", "-//Google Inc//Google Calendar//EN")
    calendar.add("VERSION", "2.0")
    calendar.add("CALSCALE", "GREGORIAN")
    calendar.add("X-WR-CALNAME", calendar_name)
    calendar.add("X-WR-TIMEZONE", timezone)

    # 跳过开始时间在 skip_days 之前的事件
    skip_days = config.get("global").get("skip_days")
    now = datetime.datetime.now().replace(tzinfo=timezone)
    skip_days_datetime = now - datetime.timedelta(days=skip_days)

    for item in config.get("startdate_list"):
        username = item.get("username")
        # YAML 似乎会自动将 YYYY-mm-dd 格式字符串转换成 datetime.date 类型
        startdate = item.get("startdate")
        event_time = item.get("event_time") or config.get("global").get("event_time")
        # 开始时间, 类型为 datetime.datetime
        start_datetime = get_local_datetime(startdate, event_time, timezone)

        # 事件持续时长
        event_duration = datetime.timedelta(
            hours=item.get("event_duration")
            or config.get("global").get("event_duration")
        )
        reminders = item.get("reminders") or config.get("global").get("reminders")
        attendees = item.get("attendees") or config.get("global").get("attendees")

        # 最多创建 max_events 个事件
        max_events = item.get("max_events") or config.get("global").get("max_events")

        event_count = 0
        max_days = item.get("max_days") or config.get("global").get("max_days")
        interval = item.get("interval") or config.get("global").get("interval")
        # 添加 cycle days 事件
        for days in range(interval, max_days + 1, interval):
            # 整数日事件 将 start_datetime 加上间隔 days 即可
            event_datetime = start_datetime + datetime.timedelta(days=days)
            # 跳过开始时间在 skip_days 之前的事件
            if event_datetime < skip_days_datetime:
                continue
            # 最多创建 max_events 个事件
            if event_count >= max_events:
                continue
            # iCal 中的时间都以 UTC 保存
            dtstart = local_datetime_to_utc_datetime(event_datetime)
            dtend = dtstart + event_duration
            age = round(days / 365.25, 2)
            summary = f"{username} 降临地球🌏已经 {days} 天啦! (age: {age})"
            add_event_to_calendar(
                calendar=calendar,
                dtstart=dtstart,
                dtend=dtend,
                summary=summary,
                reminders=reminders,
                attendees=attendees,
            )
            event_count += 1
            logger.debug("username %s cycle_days event_count %d", username, event_count)

        event_count_birthday, event_count_lunar_birthday = 0, 0
        max_ages = item.get("max_ages") or config.get("global").get("max_ages")
        for age in range(0, max_ages + 1):
            # 是否添加公历生日事件
            # bool 选项不能使用 or 来确定优先级
            if item.get("birthday", config.get("global").get("birthday", False)):
                # 公历生日直接替换 start_datetime 的 年份 即可
                event_datetime = start_datetime.replace(year=start_datetime.year + age)
                # 跳过开始时间在 skip_days 之前的事件
                if event_datetime < skip_days_datetime:
                    continue
                # 最多创建 max_events 个事件
                if event_count_birthday >= max_events:
                    continue
                dtstart = local_datetime_to_utc_datetime(event_datetime)
                dtend = dtstart + event_duration
                summary = f"{username} {dtstart.year} 年生日🎂快乐! (age: {age})"
                add_event_to_calendar(
                    calendar=calendar,
                    dtstart=dtstart,
                    dtend=dtend,
                    summary=summary,
                    reminders=reminders,
                    attendees=attendees,
                )
                event_count_birthday += 1
                logger.debug(
                    "username %s birthday event_count %d",
                    username,
                    event_count_birthday,
                )

            # 是否添加农历生日事件
            # bool 选项不能使用 or 来确定优先级
            if item.get(
                "lunar_birthday", config.get("global").get("lunar_birthday", True)
            ):
                # 将给定 公历日期 转换为农历后计算对应农历月日在当前 age 的 公历日期
                event_datetime = get_future_lunar_equivalent_date(start_datetime, age)
                # 跳过开始时间在 skip_days 之前的事件
                if event_datetime < skip_days_datetime:
                    continue
                # 最多创建 max_events 个事件
                if event_count_lunar_birthday >= max_events:
                    continue
                dtstart = local_datetime_to_utc_datetime(event_datetime)
                dtend = dtstart + event_duration
                summary = f"{username} {dtstart.year} 年农历生日🎂快乐! (age: {age})"
                add_event_to_calendar(
                    calendar=calendar,
                    dtstart=dtstart,
                    dtend=dtend,
                    summary=summary,
                    reminders=reminders,
                    attendees=attendees,
                )
                event_count_lunar_birthday += 1
                logger.debug(
                    "username %s lunar_birthday event_count %d",
                    username,
                    event_count_lunar_birthday,
                )

    calendar_data = calendar.to_ical()
    with output.open("wb") as f:
        f.write(calendar_data)
    logger.info("iCal file saved to %s", output)

    if config.get("global").get("pastebin"):
        pastebin_helper(config, output)
