from wherobots.db import connect
from wherobots.db.region import Region
from wherobots.db.runtime import Runtime
import geopandas as gpd
import pandas as pd
from shapely import wkt

class WherobotsCloud:
    """
    Class for interacting with the Wherobots Cloud API.

    Attributes:
        conn: Connection object for Wherobots Cloud API.
        curr: Cursor object for Wherobots Cloud API.
        api_key: API key for authentication.
        host: Host URL for the API (default: api.cloud.wherobots.com).
        runtime: Runtime environment for the API (default: Runtime.SEDONA).
        region: Region for the API (default: Region.AWS_US_WEST_2).

    Methods:
        open_connection: Opens a connection to the Wherobots Cloud API.
        test_connection: Tests the connection to the API.
        query: Executes a spatial SQL query and returns the results as a Pandas DataFrame.
        close_connection: Closes the connection to the API.
        query_to_gdf: Executes a SQL query and returns the results as a GeoDataFrame.
        one_off_query: Executes a single SQL query using a separate connection and closing it when done.
        one_off_query_to_gdf: Executes a single SQL query and returns the results as a GeoDataFrame, closing the connection when done.
        pro_data_catalog: Retrieves the list of schemas in the Wherobots Cloud Pro Data catalog.
    """
    def __init__(self, api_key, host='api.cloud.wherobots.com', runtime=Runtime.SEDONA, region=Region.AWS_US_WEST_2):
        self.conn = None
        self.curr = None
        self.api_key = api_key
        self.host = host
        self.runtime = runtime
        self.region = region

    def open_connection(self):
        self.conn = connect(
            api_key=self.api_key,
            runtime=self.runtime,
            region=self.region,
            host=self.host
        )
        self.curr = self.conn.cursor()
        return self.conn, self.curr

    def test_connection(self) -> None:
        try:
            self.curr.execute("SELECT 1")
            print("Connection is working")
        except:
            print("Connection failed")

    def query(self, sql) -> pd.DataFrame:
        if self.conn is None or self.curr is None:
            print("Connection is not open. Please open the connection before executing queries.")
            return
        self.curr.execute(sql)
        results = self.curr.fetchall()
        return results

    def close_connection(self):
        if self.curr is not None:
            self.curr.close()
        if self.conn is not None:
            self.conn.close()

    def query_to_gdf(self, sql) -> gpd.GeoDataFrame:
        results = self.query(sql)
        results['geometry'] = results['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(results, geometry='geometry')
        gdf = gdf.set_crs(epsg=4326)
        return gdf

    def one_off_query(self, sql) -> pd.DataFrame:
        with connect(
                api_key=self.api_key,
                runtime=self.runtime,
                region=self.region,
                host=self.host
        ) as conn:
            curr = conn.cursor()
            curr.execute(sql)
            results = curr.fetchall()
        return results

    def one_off_query_to_gdf(self, sql) -> gpd.GeoDataFrame:
        results = self.one_off_query(sql)
        results['geometry'] = results['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(results, geometry='geometry')
        gdf = gdf.set_crs(epsg=4326)
        return gdf

    def pro_data_catalog(self) -> pd.DataFrame:
        if self.conn is None or self.curr is None:
            print("Connection is not open. Please open the connection before executing queries.")
            return
        return self.query("SHOW SCHEMAS IN wherobots_pro_data")