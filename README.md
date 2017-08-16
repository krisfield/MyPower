# MyPower
MyPower makes it easy for Texas residents to input their average monthly electricity consumption (Kwh) and view the lowest priced plans available to them. Data for MyPower is pulled from [powertochoose.org](powertochoose.org), a Public Utility Commission of Texas website. Results are output in estimated monthly cost to make comparing plans as easy as possible.

## Instructions
Download this repository, navigate to MyPower with your terminal.

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
MyPower will output a table of the top ten electrical plans based on your inputs. Further details of each offer can be viewed by entering in the corresponding id#.

### Results table
![MyPower Results](https://github.com/krisfield/MyPower/blob/master/images/results_table.png?raw=true)

## Requirements
1. Python3
2. Terminaltables
