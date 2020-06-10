# NYC_311_Dash
Interactive [Bokeh](https://docs.bokeh.org/en/latest/index.html) dashboard to visualize 311 (non-emergency) call activity in NYC since the beginning of 2020 onwards. The dashboard is powered by the [311 Service Requests](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) dataset from NYC Open Data.

For all visualizations, users can drag the date slider to one point to another to animate call volume movement and observe gradual shifts over time. Each tab also allows users to select a combination of the five boroughs and includes tooltips to display exact counts when hovered over. 

### Calls by Location
View relative call volume by latitude and longitude across the Bronx, Manhattan, Brooklyn, Staten Island, and Queens. 

![](mapgif.gif)

### Calls by Category
Call volume breakdown by borough and category, where category options include agency name (NYPD, Dept. of Housing, Dept. of Transportation, etc.), complaint type, zip code, status (resolved, closed, unresolved, etc.), location type (apartment, commercial, school, etc.) and city. 

![](categorygif.gif)

### Calls by Time
A heatmap displaying call volume broken down by day of the week and time of the day. 

![](timegif.gif)

### Calls by Type
A heatmap displaying call volume by complaint description / call type. 

![](typegif.gif)

## Setup
To clone and run this application, you'll need the following:
- [Git](https://git-scm.com/) installed on your computer. 
- A Google Developer account to generate credentials used to access a google account. To do this, follow the instructions on the [pygsheets documentation](https://pygsheets.readthedocs.io/en/stable/authorization.html). Rename your credentials file 'client_secret.json'. 
- An application token for the Socrata Open Data API, which will be used to authenticate access to the 311 calls dataset. To do this, create an account with [OpenData](https://opendata.socrata.com/login), go to Developer Settings in the left-hand navigation bar, and pick "Create New App Token". Then copy the generated App Token to your client_secret.json file. 

After meeting these requirements, run the following from your command line:
```
# Clone this repository
$ git clone https://github.com/christinejiang11/NYC_311_Dash.git

# Install necessary libraries
$ pip install requirements.txt

# Run the app through bokeh server
$ bokeh serve --show main.py
```

## Libraries
The following libraries were used in this project:
- [bokeh](https://docs.bokeh.org/en/latest/index.html)
- [sodapy](https://github.com/xmunoz/sodapy)
- [pygsheets](https://pygsheets.readthedocs.io/en/stable/)
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
- [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html)
- [numpy](https://numpy.org)
- [json](https://docs.python.org/3/library/json.html)

