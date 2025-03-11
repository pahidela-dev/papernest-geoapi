import math
import pandas
import requests
from services.cache import cache

class NetworkFetcher:
    def __init__(self, q: str):
        self.query = q
        self.csv = self._read_csv_network_data()
        
    def _read_csv_network_data(self) -> pandas.DataFrame:
        return pandas.read_csv("/app/network_data.csv", sep=";")
    
    @staticmethod
    def _get_lambert93(query: str) -> tuple[float, float]:
        geocodage: dict = requests.get(
            url='https://data.geopf.fr/geocodage/search/', 
            params={'q': query}, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0'},
        ).json()
        for feature in geocodage.get("features", []):
            if feature.get("geometry", {}).get("type") == "Point":
                properties = feature.get("properties")
                return properties["x"], properties["y"]
        return None, None
    
    @staticmethod
    def _sort_dict_by_value(unsorted_dict: dict) -> list[tuple[int, float]]:
        return sorted(unsorted_dict.items(), key=lambda item: item[1])
    
    def _get_closest_points(self, query: str) -> list[dict]:
        """
        Returns a list of geographic points withiin a distance of 1 km.
        Each item of the list contains the network coverage of a specific operator.
        """
        if result := cache.get(query):
            return result

        lambert93_x, lambert93_y = self._get_lambert93(query)
        index_to_distance: dict[int, float] = {}
        for index, row in self.csv.iterrows():
            index_to_distance[index] = math.sqrt((lambert93_x - row["x"])**2 + (lambert93_y - row["y"])**2)
        sorted_list = self._sort_dict_by_value(index_to_distance)

        operators = {20801: "Orange", 20810: "SFR", 20815: "Free", 20820: "Bouygues"}
        closest_points = []
        for tup in sorted_list:
            closest_points.append({
                "operator": operators[self.csv.iloc[tup[0]]["Operateur"]],
                "2G": self.csv.iloc[tup[0]]["2G"],
                "3G": self.csv.iloc[tup[0]]["3G"],
                "4G": self.csv.iloc[tup[0]]["4G"],
                "x": self.csv.iloc[tup[0]]["x"],
                "y": self.csv.iloc[tup[0]]["y"],
                "distance": tup[1],
            })
            if tup[1] > 1000:  # Distance greater than 1 km
                break
        
        cache[query] = closest_points
        return closest_points

    def get_points_under_km(self) -> dict:
        return self._get_closest_points(self.query)

    def get_network_coverage(self) -> dict:
        closest_points = self._get_closest_points(self.query)
        network_coverage = {}
        for point in closest_points:
            if point["operator"] not in network_coverage:
                network_coverage[point["operator"]] = {
                    "2G": True if point["2G"] else False,
                    "3G": True if point["3G"] else False,
                    "4G": True if point["4G"] else False,
                }
            if (
                "Orange" in network_coverage
                and "SFR" in network_coverage
                and "Free" in network_coverage
                and "Bouygues" in network_coverage
            ):
                break
        return network_coverage



        
        