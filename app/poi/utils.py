# pylint: disable=not-callable
from collections import Counter
from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.poi import models


async def get_top_offenses(db: Session, top_n: int = 4):
    """
    Get the top offenses based on the number of matching POIOffense entries
    """
    return (
        db.query(
            models.Offense.name, func.count(models.POIOffense.offense_id).label("count")
        )
        .join(models.POIOffense, models.Offense.id == models.POIOffense.offense_id)
        .group_by(models.Offense.id)
        .order_by(func.count(models.POIOffense.offense_id).desc())
        .limit(top_n)
        .all()
    )


async def get_top_poi_age_ranges(dob_list: list[date]):
    """
    Get top poi age ranges
    """

    async def calculate_age(dob: date):
        """
        Calculate age based on dob
        """
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    async def get_age_range(age: int):
        """
        Get age range using age
        """
        if 18 <= age <= 27:
            return "18-27"
        elif 28 <= age <= 37:
            return "28-37"
        elif 38 <= age <= 47:
            return "38-47"
        elif 48 <= age <= 57:
            return "48-57"
        elif age >= 58:
            return "58+"
        else:
            return "Unknown"

    # Calculate ages and map them to age ranges
    age_ranges = [await get_age_range(await calculate_age(dob)) for dob in dob_list]

    # Count occurrences of each age range
    age_range_count = Counter(age_ranges)

    # Get the top 4 age ranges
    top_4_age_ranges = age_range_count.most_common(4)

    return top_4_age_ranges
