# MyPower
A python script which helps determine the best power offers available through [powertochoose.org](powertochoose.org), a Public Utility Commission of Texas website. While [powertochoose.org](powertochoose.org) has lots of valid/useful information for consumers to sort though, the search format leads to many companies offering "teaser" type rates which make it more difficult for consumers to understand what their utility bills will truely be.

This script attempts to clean up results by outputting the top offers based on the consumer's average Kwh consumption. Additional questions will be added to allow to sort by renewable energy plans and length of term.

## Instructions
Download this repository, navigate into MyPower with your terminal.

Run MyPower with:
`python3 mypower.py`

### Database updated
MyPower pulls data from powertochoose.org to create its "offers" database. The first prompt for the user is to ask them whether or not they want to update the local database. The default is no.

### User preferences
There are multiple prompts for user input to help narrow down the final results
1. Enter your [TDU](http://quickelectricity.com/utility-providers/) provider 
2. Enter you avergage energy consumption. This information can be found on your current providers website.
3. Do you want 100% renewable energy. Selecting yes will prioritize renewables over cost.
4. Minimum contract length desired in months (default is 0).

## Results
MyPower will output a table of the top ten electrical plans based on your inputs. It will soon allow for the user to select one of the plans to display additional details.
