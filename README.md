# Covid-Dashboard

## Introduction:

The purpose of this project was to create a dashboard to visualize and analyze Covid data in India. The data was collected from an open source JSON URL and several Excel sheets containing state-level data such as population and location. The data was cleaned and stored in a local, normalized SQL database. The dashboard was created using Dash, Plotly.express, and Dash Bootstrap Components.

## Data Collection and preparation
1. Data was collected from an open source JSON url, which contained daily covid data for each state in India.
2. The data was cleaned and stored in a local normalized SQL database using the pandas and sqlite3 libraries.
3. The data was stored in three tables: 'State', 'Data', and 'State_Data'.
4. The 'State' table contained a list of all states in India, the 'Data' table contained the daily covid data for each state, and the 'State_Data' table contained information on the area and population of each state.
5. In addition to the JSON data, an Excel sheet containing information on the population and area of each state was also read in and cleaned. This data was also stored in the 'State_Data' table.
6. A for loop was used to iterate through the states, dates, and delta data in the JSON file and store this information in the 'State', 'Data', and 'State_Data' tables.
7. Try and except statements were used to handle cases where data was not available for a particular date or state.
8. The data was committed to the database using the 'conn.commit()' command.

## Applications
For the creation of the dashboards, the following steps were taken:

1. The necessary libraries were imported, including dash, plotly.express, dash_bootstrap_components, and pandas.
2. The data was read in from the SQL database using the pandas library and stored in a dataframe called 'Joined_DF'.
3. The 'Joined_DF' dataframe was then used to create a summary table containing the total number of cases, deaths, partially vaccinated individuals, and fully vaccinated individuals for each state.
4. A dropdown menu was created using the dash library, allowing users to select a state to view data for.
5. Two graphs were created using plotly.express, one showing the number of confirmed cases and deaths over time for the selected state, and the other showing the cumulative number of confirmed cases and deaths for the selected state.
6. A map of India was created using a geojson file and the dash library, with each state colored according to the number of confirmed cases.
7. The layout of the dashboard was created using dash_bootstrap_components, including the dropdown menu, graphs, and map.
8. The app was then hosted using Heroku, allowing users to access the dashboard online.The link is not active now as Heroku discontinued the free web-hosting services to users. :(
9. For the vaccination data dashboard, a similar process was followed. The necessary libraries were imported and the data was read in from the SQL database and stored in a dataframe. A dropdown menu was created allowing users to select a state to view data for, and a line graph was created showing the daily and cumulative number of individuals vaccinated for the selected state. The layout of the dashboard was created using dash_bootstrap_components, including the dropdown menu and graph.

## Conclusion
In conclusion, the project aimed to create dashboards for Covid-19 data in India. The data was collected from an open source JSON URL and Excel sheets containing state data such as population and location. The data was cleaned using SQL and stored in a local normalized SQL database. The dashboards were created using Dash, Plotly.express, and Dash_bootstrap_components. The dashboards provided insights into the spread of the virus and the progress of vaccination efforts in the country. The project was hosted using Heroku, and the link is no longer active as it is monetized now. The project serves as a useful tool for tracking and understanding the ongoing pandemic in India.
