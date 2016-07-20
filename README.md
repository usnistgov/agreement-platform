# agreement-platform
A sorption web platform for building a data set that agrees in a mean sense with all the reference data sets of a database..
<p align="center"><sup><strong>
AGREEMENT-PLATFORM
</strong></sup></p>
The agreement-platform is a sorption web platform for building a data set that agrees in a mean sense with all the reference data sets of a database.
The aim of this platform is to provide a central space for distributing ideal measurements data and the ideal mean reference from all of them.
Also one could submit a measurement data to validate it with the mean measurement data.
* **[SETUP](SETUP.md)** – setup instructions.
* **[LICENSE](LICENSE)** – the license.

# The architecture
## ref-db
The mongodb models and database instance for storing the data sets and the mean
reference.

## ref-core
The python flask REST API that gives access to the mongodb database.
It allows dataset maniuplation, reference management, plots and external data 
validation

## ref-view
An HTML5 basic standalone material design frontend for navigating through the platform.

This repository does not come with any sorption data. If you are interested into assessing
the fonctional nature of the platform, contact me.
The setup mechanism allows one to stand an instance of the platform.
The data set are sorption excel files and the schema is also not distributed in the 
repository.

