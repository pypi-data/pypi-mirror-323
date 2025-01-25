from typing import Dict, TypedDict, Literal, overload

from .auth import get_client


class SearchResponse(TypedDict):
    status: str
    data: Dict


# Examples to help IDE
ISRCStr = Literal["USRC17607839", "USUM71703692"]
TrackStr = Literal["Yesterday", "Stairway to Heaven", "Hey Jude"]

SearchType = Literal["track", "album", "isrc", "upc"]


class Search:
    """Search interface for the Metdley API.

    Available methods:
        - search.track(artist, track) - Search by track name
        - search.album(artist, album) - Search by album name
        - search.isrc(isrc) - Search by ISRC code
        - search.upc(upc) - Search by UPC code
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_client()
        return self._client

    def _perform_search(self, search_type: SearchType, **params: str) -> SearchResponse:
        client = self._get_client()
        return client.request("POST", f"/v1/search/{search_type}", data=params)

    @overload
    def track(self, artist: str, track: str) -> SearchResponse: ...

    def track(self, artist: str, track: str) -> SearchResponse:
        """Search for a track by artist and track name.

        Args:
            artist: The artist name (e.g., "The Beatles")
            track: The track name (e.g., "Yesterday")

        Returns:
            SearchResponse: The search results

        Example:
            >>> search.track("The Beatles", "Yesterday")
        """
        return self._perform_search("track", artist=artist, track=track)

    @overload
    def album(self, artist: str, album: str) -> SearchResponse: ...

    def album(self, artist: str, album: str) -> SearchResponse:
        """Search for an album by artist and album name.

        Args:
            artist: The artist name (e.g., "Pink Floyd")
            album: The album name (e.g., "The Wall")

        Returns:
            SearchResponse: The search results

        Example:
            >>> search.album("Pink Floyd", "The Wall")
        """
        return self._perform_search("album", artist=artist, album=album)

    @overload
    def isrc(self, isrc: str) -> SearchResponse: ...

    def isrc(self, isrc: str) -> SearchResponse:
        """Search by ISRC code.

        Args:
            isrc: The ISRC code (e.g., "USRC17607839")

        Returns:
            SearchResponse: The search results

        Example:
            >>> search.isrc("USRC17607839")
        """
        return self._perform_search("isrc", isrc=isrc)

    @overload
    def upc(self, upc: str) -> SearchResponse: ...

    def upc(self, upc: str) -> SearchResponse:
        """Search by UPC code.

        Args:
            upc: The Universal Product Code (e.g., "123456789012")

        Returns:
            SearchResponse: The search results

        Example:
            >>> search.upc("123456789012")
        """
        return self._perform_search("upc", upc=upc)


# Create instance
search = Search()
