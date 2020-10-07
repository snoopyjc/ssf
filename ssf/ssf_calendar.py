class SSF_CALENDAR:
    """Handle alternative calendars.
    This is a stub for now"""
    (DEFAULT, GREGORIAN_LOCAL, GREGORIAN_US, JAPANESE, TAIWAN, KOREAN,       # 00-05
    HIJRI, THAI, JEWISH, GREGORIAN_MIDDLE_EASTERN_FRENCH, GREGORIAN_ARABIC, # 06-0A
    GREGORIAN_TRANSLITERATED_ENGLISH, GREGORIAN_TRANSLITERATED_FRENCH, x0D, # 0B-0D
    LUNAR_x0E, x0F, x10, LUNAR_x11, LUNAR_x12,                              # 0E-12
    LUNAR_x13, x14, x15, x16, x17, x18, x19, x1A, x1B, x1C, x1D, x1E, x1F) = range(0x20)

    # Each converter takes a tuple (year, month, day) and returns a tuple (year, month, day)

    def to_japanese(ymd):
        pass

    def to_taiwan(ymd):
        pass

    def to_korean(ymd):
        pass

    def to_hijri(ymd):
        pass

    def to_thai(ymd):
        pass

    def to_jewish(ymd):
        pass

    def to_lunar_x0e(ymd):
        pass

    def to_lunar_x11(ymd):
        pass

    def to_lunar_x12(ymd):
        pass

    def to_lunar_x13(ymd):
        pass

    def month_names(calendar, length='mmmm'):
        pass

    def day_names(calendar, length='dddd'):
        pass

    _calendar_converter = [None, None, None, to_japanese, to_taiwan, to_korean,
        to_hijri, to_thai, to_jewish, None, None, None, None, None, to_lunar_x0e,
        None, None, to_lunar_x11, to_lunar_x12, to_lunar_x13, None, None, None, 
        None, None, None, None, None, None, None, None, None]

