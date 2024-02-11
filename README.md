# ProjetSAW

Project G1G2 from école centrale lille, that exploits the technology from the sensors SAW to determinate the concentration of a gaz in a controled environment.


## Installation

To run this project, firstly install the libraries on ```src/requirements.txt```. Python 3.8 or higher is required.

## Running

In order to run the application, the following steps are required:

* Firstly, connect all the required components
* Check the network analyser in order to get the correct central frequency, which will later be used as an input in the user interface
* Verify if the serial number in the ```src/.env``` file corresponds to the equipment you're currently using
* On a terminal, run the script with the following command  ```python src/saw_V4.py```