# Setting up dft-crossfilter

To setup this platform we recommend installing an environment management
system. For this purpose we installed [anaconda](https://www.continuum.io/downloads). Then create and load an
environment where we will install all the paltform dependencies.

    $ conda create -n agree-plt python=2.7 anaconda

We recommand that you have three terminal windows to run these following
sections. Each will producing a trace in the terminal that you might want
to look into. All three of them are servers and will not return the 
terminal input unless you detach them with '&'.  Every section commands
should be run after activating the environment we just created.

## The database setup

You will have to build the database models and run a mongodb instance.
Note that if you have an instance running already you just need the
database models. In case you don't have one you need to get the absolute
path to the data folder in ref-production. This is required for storing
the database file and mongod only takes absolutepaths.

    $ source activate agree-plt
    $ cd agreement-platform/ref-db
    $ pip install -r requirements.txt
    $ python setup.py install

Go to [Mongodb](https://docs.mongodb.com/manual/installation/) and install
it on your system. Then start it. In ubuntu you can do so by:

    $ sudo service mongod start

At this point you should have a mongodb instance running.

## The core rest api setup

After starting the database, we now need to install the api dependencies.
Then run it.

    $ source activate agree-plt
    $ cd agreement-platform/ref-core
    $ pip install -r requirements.txt
    $ python run.py --host 0.0.0.0 --port 4100

## frontend view

Now that you have the database instance up and running and the core REST
service connected to the database and exposing its endpoints we can stand
the frontend instance.
To do so you will need to install jekyll. Goto [Jekyll Installation](https://jekyllrb.com/docs/installation/).
When done installing:

    $ cd agreement-platform/ref-view
    $ sudo jekyll serve --watch --port 4000 --host 0.0.0.0

At this point you should have a bare instance running. Go to [Instance](http://0.0.0.0:4000/).
This instance has no data and no reference mean. To add some datasets you will have to go
to the sets and upload some data sets. Then include or exclude the datasets to be considered
for the agreement mean reference and go back to the home page by clicking on Reference
in the top banner. Then click on 'Build reference'. The fake image should then be replaced
by a plot of the mean plot and some other information.
