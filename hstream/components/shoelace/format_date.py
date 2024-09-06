from hstream.components.components import component_wrapper
from typing import Optional


@component_wrapper
def sl_format_date(
    self,
    date: str,
    locale: Optional[str] = None,
    weekday: Optional[str] = None,
    era: Optional[str] = None,
    year: Optional[str] = None,
    month: Optional[str] = None,
    day: Optional[str] = None,
    hour: Optional[str] = None,
    minute: Optional[str] = None,
    second: Optional[str] = None,
    time_zone_name: Optional[str] = None,
    time_zone: Optional[str] = None,
    hour_format: Optional[str] = None,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Render a Shoelace format-date component.

    Args:
        date (str): The date to format.
        locale (str, optional): The locale to use when formatting the date.
        weekday (str, optional): How to display the weekday.
        era (str, optional): How to display the era.
        year (str, optional): How to display the year.
        month (str, optional): How to display the month.
        day (str, optional): How to display the day.
        hour (str, optional): How to display the hour.
        minute (str, optional): How to display the minute.
        second (str, optional): How to display the second.
        time_zone_name (str, optional): How to display the time zone name.
        time_zone (str, optional): The time zone to express the time in.
        hour_format (str, optional): The hour format to use.
        key (str, optional): A unique identifier for the component.
        **kwargs: Additional attributes to pass to the format-date element.
    """
    attributes = [
        ("date", date),
        ("locale", locale),
        ("weekday", weekday),
        ("era", era),
        ("year", year),
        ("month", month),
        ("day", day),
        ("hour", hour),
        ("minute", minute),
        ("second", second),
        ("time-zone-name", time_zone_name),
        ("time-zone", time_zone),
        ("hour-format", hour_format),
    ]

    # Filter out None values
    filtered_attributes = [(k, v) for k, v in attributes if v is not None]

    with self.tag("sl-format-date", *filtered_attributes, *kwargs.items()):
        pass
