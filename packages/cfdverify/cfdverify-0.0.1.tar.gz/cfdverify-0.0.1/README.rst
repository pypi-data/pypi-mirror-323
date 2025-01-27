CFDverify
=========

This repository holds code to conduct solution verification of CFD simulations.

Installation
------------

To install CFDverify, copy this repository to a suitable location on your computer, (optionally) launch your virtual environment, and install with pip.

.. code-block:: console

    $ git clone git@github.com:ORNL/cfd-verify.git
    $ cd cfd-verify
    $ source /path/to/your/venv/bin/activate
    $ pip install .

To install dependencies for testing the code, install with the command :code:`pip install .[tests]`. Likewise, to install documentation dependencies use the command :code:`pip install .[docs]`. Alternatively, install all optional dependencies using the command :code:`pip install .[full]`.

Documentation
-------------

To build CFDverify's documentation, execute the command :code:`make html` in the docs directory of CFDverify, or

.. code-block:: console

    $ cd cfd-verify/docs
    $ make html

The documentation can then be read using any web browser by opening the file cfd-verify/docs/build/html/index.html. Install CFDverify using :code:`pip install .[docs]` to ensure you have all the required dependencies to build the documentation.

Testing
-------

To run CFDverify's tests, execute the command :code:`pytest` in the top level of the CFDverify directory or in the tests sub-directory. Install CFDverify using :code:`pip install .[tests]` to ensure you have all the required dependencies for runnning tests.

Author
------

Justin Weinmeister: <weinmeistejr@ornl.gov>
