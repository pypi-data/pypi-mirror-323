import datetime
from .system import CurrentSystemTime
def CalculateTimeDifferencetoTargetTime24HourFrame(targettime):
    currenttime = CurrentSystemTime()
    try:
        targettime = datetime.datetime.combine(currenttime.date(), datetime.datetime.strptime(targettime, "%H:%M").time())
    except (ValueError, TypeError):
        return "Error try Format: str(%H:%M)"
    timedifference = targettime - currenttime
    return timedifference