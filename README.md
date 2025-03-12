# Papernest geo api test

This project intends to solve the problem of getting network coverage for a text address. 



## Build project

I chose Docker to build the project because of the easiness and go-to availability it provides. Simply clone the project 

``git clone git@github.com:pahidela-dev/papernest-geoapi.git``

And then run 

``docker compose build && docker compose up -d`` (or ``docker-compose`` depending on your Docker version)

to get the API up and running. Docker will handle for us the project build, dependencies, etc. Whatever runs in my machine will run in yours. 

## Testing the API

You can check that the API is working by sending a GET request to localhost:8000/
You should see ``{"Hello": "World"}``

There are basically two endpoints exposed, 
/search/
/search_under_km/

You can test them by sending GET requests to them via your web browser, using or curl, or using the API documentation here: http://localhost:8000/docs

For example, if we send a GET request to this url http://localhost:8000/search/?q=42%20rue%20papernest%2075011%20Paris

We get the following result

 ``{"Orange":{"2G":true,"3G":true,"4G":false},"SFR":{"2G":true,"3G":false,"4G":false},"Bouygues":{"2G":true,"3G":false,"4G":false},"Free":{"2G":false,"3G":true,"4G":true}}``

This response follows the expected format. 

## Comments, assumptions and considerations

### 1. Geographic logic
The test does explicitly say that it is not intended to work on a precise geographic match, rather a city level precision is enough. In light of this, I have a followed a simple logic to process data. 

#### 1. 1. First element as closest points.
The API fetches data from https://data.geopf.fr and assumes that  the first item encountered in the result list is already a valid location. This is assumed due to the geographic closeness of the results this third-party API yields (I checked the coordinates of the results for one query). Since we want to find network coverage in this area, this point should be valid for this purpose. 

#### 1.2. Usage of Lambert93
 The third-party API returns already the Lambert93 coordinates under the "properties" key in each item. Due to this, I have found it more simple to ditch completely the conversion between the latitude and longitude spherical coordinates and just use the "properties.x" and "properties.y" to compute distances between points. If this API already gives us data in the format of our network coverage data source, it seems like a good idea to use this coordinate system and avoid conversions.

### 2. Format of the payload/response
We have followed the same format in our endpoint design and response than that proposed in the test. 

### 3. Response content
Since our API takes into consideration all geographic points no further than 1km, chances that our query always has information about all 4 operators are high. Especially in a city like Paris (test query). However, this does not hold true for queries for "lost" places. Take for example a request like this:

 ``GET http://localhost:8000/search/?q=10 Rte de Garaibie, 64130 Ordiarp``

Our API returns this JSON content:  ``{"Orange":{"2G":true,"3G":true,"4G":true}} ``

It does seem to make sense that one random point in the middle of the Pyrenees has not a lot of network coverage. However, let's look a bit under the hood. If we check the other exposed endpoint:

 ``GET http://localhost:8000/search_under_km/?q=10 Rte de Garaibie, 64130 Ordiarp``

We obtain this response:

``[{"operator":"Orange","2G":1.0,"3G":1.0,"4G":1.0,"x":382392.0,"y":6244554.0,"distance":5604.200579797572}]``

This is happening because, by design, our API will always retrieve data for *at least* one geographic point, no matter how far. In fact, we can see that the closest record found in the csv data source is 5.6 km away. Since our API is designed to stop at anything further than 1 km, then it only retrieves this point. 

It would be fair to say that 5.6 km could make no sense when it comes to network geographic coverage and, by design, any point further than an arbitrary distance should not be considered. This is something that could be easily changed by simply modifying the boolean condition and using this arbitrary threshold, and our API would return an empty body. 

### 4. Tests

I started following a TDD approach to design and implement the API until I realized that the example in the test wasn't necessarily showing a correct response body (or that's what I think). Since I was only testing the API root "/" endpoint, I chose to drop the tests as soon as I had everything working as expected. 

