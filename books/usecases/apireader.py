import requests


class ApiReader():
    """Provides basic Books API operations

    Raises:
        ConnectionError: Unable to reach google api
    """

    api_url = 'https://www.googleapis.com/books/v1/volumes'

    def count(self, keywords):
        """
        Returns estimated total number of
        books for specified keywords

        Args:
            keywords (String): search keywords

        Returns:
            Int: estimated books number
        """

        params = {
            'q': keywords,
            # I dont know why,
            # totalItems is different when maxResults is smaller than 40
            'maxResults': 1,
        }
        json_data = self.make_request(params)
        total = json_data.get("totalItems", 0)
        return total

    def get_books(self, keywords, begin, end):
        """Returns some of the books results for keywords query

        Args:
            keywords (String): search keywords
            begin (Int): range begin
            end (Int): range end

        Returns:
            JSON: compelete response
        """

        params = {
            'q': keywords,
            'startIndex': begin,
            'maxResults': end-begin,
        }
        json_data = self.make_request(params)
        return json_data

    def make_request(self, params):
        """ Makes single api request

        Args:
            params (Dict): request GET parameters

        Raises:
            ConnectionError: Unable to reach google api

        Returns:
            JSON: compelete response
        """

        result = requests.get(url=self.api_url, params=params)
        code = result.status_code

        if(code != 200):
            print("Cant connect Google API - code: " + str(result))
            print(result.url)
            raise ConnectionError(
                "Can't connect to the Goole API. Response code: " + str(code)
            )

        json_data = result.json()
        return json_data
