from hstream.components.components import component_wrapper
from typing import Optional


@component_wrapper
def sl_format_date(self, date: str, key: Optional[str] = None, **kwargs) -> None:
    """
    Render a Shoelace format-date component.

    Args:
        date (str): The date to format.
        key (str, optional): A unique identifier for the component.
        **kwargs: Additional attributes to pass to the format-date element.
            Possible attributes include:
            - locale: The locale to use when formatting the date.
            - weekday: How to display the weekday.
            - era: How to display the era.
            - year: How to display the year.
            - month: How to display the month.
            - day: How to display the day.
            - hour: How to display the hour.
            - minute: How to display the minute.
            - second: How to display the second.
            - time_zone_name: How to display the time zone name.
            - time_zone: The time zone to express the time in.
            - hour_format: The hour format to use.
    """
    attributes = [("date", date)]
    attributes.extend([(k.replace("_", "-"), v) for k, v in kwargs.items() if v is not None])

    with self.tag("sl-format-date", *attributes):
        pass
