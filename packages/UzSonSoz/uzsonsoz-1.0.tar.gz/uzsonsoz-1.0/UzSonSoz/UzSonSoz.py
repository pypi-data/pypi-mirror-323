import re


def SondanSozga(n):  # noqa

    if not isinstance(n, int):
        return n

    if n == 0:
        return "nol"

    ones = ["", "bir", "ikki", "uch", "to‘rt", "besh", "olti", "yetti", "sakkiz", "to‘qqiz"]

    tens = ["", "o‘n", "yigirma", "o‘ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to‘qson"]

    thousands = ["", "ming", "million", "milliard"]

    def convert_hundreds(n):
        if n == 0:
            return ""
        elif n < 10:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + ('' if n % 10 == 0 else ' ' + ones[n % 10])
        else:
            return ones[n // 100] + " yuz" + ('' if n % 100 == 0 else ' ' + convert_hundreds(n % 100))

    def convert_large_numbers(n):
        if n == 0:
            return ""

        result = []
        place = 0
        while n > 0:
            if n % 1000 != 0:
                result.append(convert_hundreds(n % 1000) + ('' if thousands[place] == '' else ' ' + thousands[place]))
            n //= 1000
            place += 1

        return ' '.join(result[::-1])

    return convert_large_numbers(n)


def __change_apostrophe(text):
    # Function to change the sign of the letter o‘

    text = text.replace(f"o{chr(39)}", f"o{chr(8216)}")  # ord("'") -> ord("‘")

    text = text.replace(f"o{chr(96)}", f"o{chr(8216)}")  # ord("`") -> ord("‘")

    text = text.replace(f"o{chr(699)}", f"o{chr(8216)}")  # ord("ʻ") -> ord("‘")

    text = text.replace(f"o{chr(700)}", f"o{chr(8216)}")  # ord("ʼ") -> ord("‘")

    text = text.replace(f"o{chr(8217)}", f"o{chr(8216)}")  # ord("’") -> ord("‘")

    return text


def SozdanSonga(s):  # noqa

    if isinstance(s, int):
        return s

    ones = {
        "bir": 1, "ikki": 2, "uch": 3, "to‘rt": 4, "besh": 5, "olti": 6, "yetti": 7, "sakkiz": 8, "to‘qqiz": 9
    }

    tens = {
        "o‘n": 10, "yigirma": 20, "o‘ttiz": 30, "qirq": 40, "ellik": 50, "oltmish": 60, "yetmish": 70, "sakson": 80, "to‘qson": 90
    }

    large_numbers = {
        "ming": 1000, "million": 10 ** 6, "milliard": 10 ** 9
    }

    def parse_chunk(chunk):
        parts = chunk.split()

        current = 0
        for part in parts:
            if part in ones:
                current += ones[part]
            elif part in tens:
                current += tens[part]
            elif part == "yuz":
                current *= 100

        return current

    # Remove unnecessary spaces and handle case insensitivity
    original_s = s
    s = s.lower().strip()
    s = __change_apostrophe(s)

    if s == "nol":
        return 0

    # Match the large number groups (thousands, millions, billions)
    chunks = re.split(r'\s(?:ming|million|milliard)\s?', s)

    result = 0
    multiplier = 1

    # Process each chunk from largest to smallest
    for i, chunk in enumerate(reversed(chunks)):
        chunk_value = parse_chunk(chunk.strip())
        if chunk_value:
            result += chunk_value * (multiplier if i == 0 else large_numbers.get(chunks[-(i + 1)].strip(), 1))
        multiplier *= 1000

    if result == 0:
        return original_s
    else:
        return result
