# flake8: noqa: WPS110, WPS114

from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, field_validator


class Competition(BaseModel):
    """Represents the data about competition which provide the judobase api"""

    id_competition: str
    date_from: str
    date_to: str
    name: str
    has_results: int
    city: str
    street: str
    street_no: str
    comp_year: int
    prime_event: bool
    continent_short: str
    has_logo: bool
    competition_code: Optional[str]
    updated_at_ts: datetime
    updated_at: datetime
    timezone: Optional[str]
    id_live_theme: int
    code_live_theme: str
    country_short: str
    country: str
    id_country: int
    is_teams: int
    status: Optional[str]
    external_id: Optional[str]
    id_draw_type: int
    ages: List[str]
    rank_name: Optional[str]

    @field_validator("updated_at", mode="after")
    @classmethod
    def parse_updated_at(cls, value):
        return value.replace(tzinfo=timezone.utc)

    @field_validator("date_from", mode="after")
    @classmethod
    def parse_date_from(cls, value):
        return datetime.strptime(value, "%Y/%m/%d")

    @field_validator("date_to", mode="after")
    @classmethod
    def parse_date_to(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y/%m/%d")


class Contest(BaseModel):
    """Represents the data about contest which provide the judobase api"""

    # general contest data
    id_competition: str
    id_fight: str
    id_person_blue: str
    id_person_white: str
    id_winner: Optional[str]
    is_finished: bool
    round: int
    duration: Optional[str]
    gs: bool
    bye: str
    fight_duration: Optional[str]
    weight: Optional[str]
    id_weight: Optional[str]
    type: int
    round_code: Optional[str]
    round_name: str
    mat: int
    date_start_ts: datetime
    updated_at: datetime
    first_hajime_at_ts: datetime

    # white person details
    ippon_w: Optional[int]
    waza_w: Optional[int]
    yuko_w: Optional[int]
    penalty_w: Optional[int]
    hsk_w: Optional[int]
    person_white: str
    id_ijf_white: str
    family_name_white: str
    given_name_white: str
    timestamp_version_white: str
    country_white: Optional[str]
    country_short_white: Optional[str]
    id_country_white: Optional[str]
    picture_folder_1: Optional[str]
    picture_filename_1: Optional[str]
    personal_picture_white: Optional[str]

    # blue person details
    ippon_b: Optional[int]
    waza_b: Optional[int]
    yuko_b: Optional[int]
    penalty_b: Optional[int]
    hsk_b: Optional[int]
    person_blue: str
    id_ijf_blue: str
    family_name_blue: str
    given_name_blue: str
    timestamp_version_blue: str
    country_blue: Optional[str]
    country_short_blue: Optional[str]
    id_country_blue: Optional[str]
    picture_folder_2: Optional[str]
    picture_filename_2: Optional[str]
    personal_picture_blue: Optional[str]

    # competitions details
    competition_name: str
    external_id: str
    city: str
    age: Optional[str]
    rank_name: Optional[str]
    competition_date: str
    date_raw: str
    comp_year: str

    # other details
    tagged: int
    kodokan_tagged: int
    published: str
    sc_countdown_offset: int
    fight_no: int
    contest_code_long: str
    media: Optional[str]
    id_competition_teams: Optional[str]
    id_fight_team: Optional[str]

    @field_validator("updated_at", mode="after")
    @classmethod
    def parse_updated_at(cls, value):
        return value.replace(tzinfo=timezone.utc)

    @field_validator("date_start_ts", mode="after")
    @classmethod
    def parse_date_start_ts(cls, value):
        return value.replace(tzinfo=timezone.utc)

    @field_validator("first_hajime_at_ts", mode="after")
    @classmethod
    def parse_first_hajime_at_ts(cls, value):
        return value.replace(tzinfo=timezone.utc)


class Competitor(BaseModel):
    """Represents the data about competitor which provide the judobase api"""

    family_name: str
    middle_name: Optional[str]
    given_name: str
    family_name_local: str
    middle_name_local: Optional[str]
    given_name_local: str
    short_name: Optional[str]
    gender: str
    folder: str
    picture_filename: str
    ftechique: Optional[str]
    side: str
    coach: str
    best_result: str
    height: str
    birth_date: datetime
    country: str
    id_country: str
    country_short: str
    file_flag: Optional[str]
    club: Optional[str]
    belt: Optional[str]
    youtube_links: Optional[str]
    status: Optional[str]
    archived: Optional[str]
    categories: List[str]
    dob_year: Optional[str]
    age: Optional[str]
    death_age: Optional[str]
    personal_picture: str
