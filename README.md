# SI507finalproj
WN18 SI507 Final Project

Main program: finalproj.py

This program lets a user view the average, minimum, and maximum ratings of different restaurant categories (e.g. American, Bars, Breakfast) as a list or as plotly charts.

Required files to run the program:
- help.txt
- secrets.py (Place your API keys in this file saved as: yelp_key = <api_key from Yelp>, zomato_key = <api_key from Zomato>). See next section on instructions on how to get API keys.
  
Data sources and api_key requirements:
- Yelp (An API key is required to access this data source. To get an API key, go to https://www.yelp.com/developers/documentation/v3/authentication)

- Zomato (An API key is required to access this data source. To get an API key, go to https://developers.zomato.com/api)

Other useful info:
Getting started with Plotly for Python - https://plot.ly/python/getting-started/
  
Program structure:
This program uses API key authorization, json, requests, caching, sqlite, and plotly.It is divided into 8 main functions:

1. ask_user: Main function. Interactively asks the user for a city input. This function kicks off the other functions.
2. create_db_tables: Creates the db and main tables YelpResto and ZomatoResto.
3. insert_tables: Inserts data in the YelpResto and ZomatoResto tables.
4. create_categories: Creates the Categories table and inserts unique categories based on the Yelp search.
5. create_cuisines: Creates the Cuisines table and inserts unique cuisines based on the Zomato search.
6. upd_ids: Updates the category and cuisine ids in the main tables.
7. upd_ave_rating: Averages the rating of restaurants that belong in the same category and updates the averating column in the Categories and Cuisines tables.
8. ask_next: Set of interactive commands such as list, plot, new, help, and exit. See User Guide for more info on the specific commands.

User Guide:
1. A predefined list (Top 25 most-visited cities in the US) is displayed.
2. Enter the number of choice to start searching for restaurants (a maximum of 100 records each are retrieved from Yelp and Zomato).
3. Enter command. Main commands are list, plot, new, help, and exit. See below for details.

list: Lists restaurant categories/cuisines and their corresponding ratings (average, minimum, and maximum) according to the specified parameters.

	Options:
		* yelp | zomato
		Description: Required. Specifies source of data - Yelp or Zomato

		* top | bottom
		Description: Required. Specifies whether to list the top or bottom matches.

		* <limit>
		Description: Optional. Specifies whether to list the top <limit> matches or the
		bottom <limit> matches. If not specified, all results will be displayed.

	Sample list commands:
		"list yelp top 10"
		"list zomato bottom"

plot: Creates and launches plotly charts. Types of charts displayed are based on specified parameters.

	Options:
		* bar
		Description: Only available when the list command is used. Displays a bar chart of the results from a previous list command call. Values displayed are average ratings.

		* groupedbar
		Description: Displays a grouped bar chart matching similar categories and cuisines from Yelp and Zomato. Values displayed are average ratings.

		* pie <source>
		Source options: yelp | zomato
		Description: Displays a pie chart of all categories/cuisines from the specified <source>. Values displayed are proportion of restaurants that belong in a category/cuisine.

		* donut
		Description: Displays side-by-side donut charts of matching categories/cuisines from Yelp and Zomato. Values displayed are proportion of restaurants that belong in these categories.

	Sample plot commands:
		"plot bar"
		"plot zomato pie"

new: Begins a new city search.

help: Prints command instructions.

exit: Terminates program.




