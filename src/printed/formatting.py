from whenever import Instant, OffsetDateTime, TimeDelta


def relative_datetime(dt: OffsetDateTime | None) -> str:
    if dt is None:
        return "N/A"

    now = Instant.now()
    diff = now - dt

    hours, minutes, *_ = diff.in_hrs_mins_secs_nanos()
    days = hours // 24
    hours = hours % 24

    segments = []
    if days:
        segments.append(f"{days} days")

    if hours:
        segments.append(f"{hours} hours")

    if minutes:
        segments.append(f"{minutes} minutes")

    return " ".join(segments) + " ago"


def format_datetime(dt: OffsetDateTime | None, timezone: str) -> str:
    if dt is None:
        return "N/A"

    return dt.to_tz(timezone).format_common_iso()


def format_duration(duration: TimeDelta) -> str:
    if not duration:
        return ""
    return duration.format_common_iso()[2:]


def format_cost(val: float, *, cost_symbol: str = "$") -> str:
    return f"{cost_symbol}{val:0.2f}"


def format_weight(val: float) -> str:
    return f"{val:0.1f}"


def parse_duration(d: str | TimeDelta) -> TimeDelta:
    if isinstance(d, TimeDelta):
        return d

    return TimeDelta.parse_common_iso(f"PT{d.upper()}")


def format_title(title: str) -> str:
    return title.replace("_", " ").title()
