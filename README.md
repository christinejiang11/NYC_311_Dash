# NYC_311_Dash
Interactive bokeh dashboard to visualize 311 (non-emergency) call activity in NYC, since the beginning of 2020 onwards. 

### Calls by Location:
View relative call volume by latitude and longitude across the Bronx, Manhattan, Brooklyn, Staten Island, and Queens. Filter the number of data points shown and the dates in the visualization. 
![](mapgif.gif)

### Calls by Category:
![](categorygif.gif)

### Calls by Time:
![](timegif.gif)

### Calls by Type:
![](typegif.gif)

## Setup:
To clone and run this application, you'll need [Git](https://git-scm.com/) installed on your computer. From your command line:
```
# Clone this repository
$ git clone https://github.com/christinejiang11/NYC_311_Dash.git

# Install necessary libraries
$ pip install requirements.txt

# Run the app through bokeh server
$ bokeh serve --show main.py
```
