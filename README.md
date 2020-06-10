# NYC_311_Dash
Interactive [Bokeh](https://docs.bokeh.org/en/latest/index.html) dashboard to visualize 311 (non-emergency) call activity in NYC, since the beginning of 2020 onwards. The dashboard is powered by this [311 Service Requests](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) dataset from NYC Open Data.

For all visualizations, users can drag the date slider to one point to another to animate call volume movement and observe gradual shifts over time. Each tab  allows users to select a combination of the five boroughs, and includes tooltips to display exact counts when hovered over. 

### Calls by Location:
View relative call volume by latitude and longitude across the Bronx, Manhattan, Brooklyn, Staten Island, and Queens. 

![](mapgif.gif)

### Calls by Category:
Call volume breakdown by borough and category, where category options include agency type, complaint type, zip code, status (resolved, closed, unresolved, etc), location type (apartment, commercial, school, etc) and city. 

![](categorygif.gif)

### Calls by Time:
A heatmap displaying call volume broken down by day of the week and time of the day. 

![](timegif.gif)

### Calls by Type:
A heatmap displaying call volume by type, which is a description of the nature of the call. 

![](typegif.gif)

## Setup:
To clone and run this application, you'll need [Git](https://git-scm.com/) installed on your computer. You will also need to get an API key from NYC Open Data and Google API credentials to connect with google sheets. From your command line:
```
# Clone this repository
$ git clone https://github.com/christinejiang11/NYC_311_Dash.git

# Install necessary libraries
$ pip install requirements.txt

# Run the app through bokeh server
$ bokeh serve --show main.py
```
## Project outline:


## Credits:
