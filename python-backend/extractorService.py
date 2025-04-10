import re
from typing import Dict, Optional, List, Any


class WeatherExtractor:
    """
    Service for extracting weather-related information from text.
    """

    def __init__(self):
        """
        Initialize the WeatherExtractor with word lists for pattern matching.
        """
        # Words that indicate a weather query
        self.weather_words: List[str] = [
            "wetter", "temperatur", "regen", "schnee", "sonne", "wind",
            "kalt", "warm", "gewitter", "niederschlag", "bewölkt", "wolken",
            "grad", "celsius", "vorhersage"
        ]

        # List of German cities to recognize
        self.cities: List[str] = [
            "berlin", "hamburg", "münchen", "köln", "frankfurt", "stuttgart",
            "düsseldorf", "dresden", "leipzig", "hannover", "nürnberg",
            "dortmund", "essen", "bremen", "bonn", "mannheim", "heilbronn"
        ]

        # Time-related words
        self.today_words: List[str] = ["heute", "jetzt", "aktuell"]
        self.tomorrow_words: List[str] = ["morgen"]
        self.week_words: List[str] = ["woche", "tage", "übermorgen"]

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract weather-related information from text.

        Args:
            text: The text to extract information from

        Returns:
            Dictionary with:
                - is_weather_query: Whether the text is a weather query
                - location: The city mentioned in the text (if any)
                - time_period: The time period mentioned (today, tomorrow, week)
        """
        if not text:
            return {"is_weather_query": False, "location": None, "time_period": "today"}

        # Convert to lowercase for case-insensitive matching
        text = text.lower()

        # Check if this is a weather query
        is_weather = any(word in text for word in self.weather_words)

        # Find location (city)
        location = self._extract_location(text, is_weather)

        # If a city was found, it's definitely a weather query
        if location:
            is_weather = True

        # Determine time period
        time_period = self._extract_time_period(text)

        return {
            "is_weather_query": is_weather,
            "location": location,
            "time_period": time_period
        }

    def _extract_location(self, text: str, is_weather: bool) -> Optional[str]:
        """
        Extract location (city) from text.

        Args:
            text: The text to extract location from
            is_weather: Whether the text is a weather query

        Returns:
            The city mentioned in the text, or None if no city was found
        """
        # Check if any known city is mentioned
        for city in self.cities:
            if city in text:
                return city

        # If no city was found but it's a weather query, try to extract using regex
        if is_weather:
            # Pattern: "Wetter [Stadt]"
            pattern = r'wetter\s+([a-zäöüß]+)'
            match = re.search(pattern, text)
            if match:
                potential_city = match.group(1)
                # Make sure it's not a weather or time word
                if (potential_city not in self.weather_words and
                        potential_city not in self.today_words and
                        potential_city not in self.tomorrow_words and
                        potential_city not in self.week_words):
                    return potential_city

        return None

    def _extract_time_period(self, text: str) -> str:
        """
        Extract time period from text.

        Args:
            text: The text to extract time period from

        Returns:
            The time period mentioned (today, tomorrow, week)
        """
        # Default to today
        time_period = "today"

        # Check for tomorrow
        if any(word in text for word in self.tomorrow_words):
            time_period = "tomorrow"

        # Check for week (overrides tomorrow if both are mentioned)
        if any(word in text for word in self.week_words):
            time_period = "week"

        return time_period
