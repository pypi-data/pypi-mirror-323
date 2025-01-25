############################
Heimdall - MariaDB connector
############################

.. image:: https://img.shields.io/badge/license-AGPL3.0-informational?logo=gnu&color=success
   :target: https://www.gnu.org/licenses/agpl-3.0.html
.. image:: https://www.repostatus.org/badges/latest/active.svg
   :target: https://www.repostatus.org/#project-statuses
.. image:: https://img.shields.io/pypi/v/pyheimdall-mariadb
   :target: https://pypi.org/project/pyheimdall-mariadb/
   :alt: PyPI Version
.. image:: https://img.shields.io/badge/documentation-api-green
   :target: https://datasphere.readthedocs.io/projects/heimdall/
.. image:: https://gitlab.huma-num.fr/datasphere/heimdall/connectors/mariadb/badges/main/pipeline.svg
   :target: https://gitlab.huma-num.fr/datasphere/heimdall/connectors/mariadb/pipelines/latest
.. image:: https://gitlab.huma-num.fr/datasphere/heimdall/connectors/mariadb/badges/main/coverage.svg
   :target: https://datasphere.gitpages.huma-num.fr/heimdall/connectors/mariadb/coverage/index.html


*************
What is this?
*************

`pyHeimdall <https://datasphere.readthedocs.io/projects/heimdall/>`_ is a tool for converting more easily one or more databases from one format to another.
It leverages modules called "connectors", responsible for conversion of data between specific databases schemas and the HERA format.

This repository implements a connector to retrieve data from a MariaDB database.
The implementation doesn't need any intervention on pyHeimdall proper.


*****************
How can I use it?
*****************

Setup
=====

This MariaDB pyHeimdall connector is available as a `PyPI package <https://pypi.org/project/pyheimdall-mariadb/>`_ named ``pyheimdall-mariadb``.
You can install it using the `pip <https://pip.pypa.io/en/stable/>`_ package manager:

.. code-block:: bash

   pip install pyheimdall-mariadb

You can use `pip <https://pip.pypa.io/en/stable/>`_ to either upgrade or uninstall this connector, too:

.. code-block:: bash

   pip install --upgrade pyheimdall-mariadb
   pip uninstall pyheimdall-mariadb

Usage
=====

.. code-block:: python

   import heimdall

   tree = heimdall.getDatabase(
           format='sql:mariadb',
           url='mariadb://myusername:mypassword@myhost:myport/mydatabase',
           entities=('mytable', 'myothertable', ),
           )
   heimdall.createDatabase(tree, format='xml:hera', url='mydatabase.xml')

Please note that you don't need to use ``pyheimdall-mariadb`` functions directly.
As long as the package is installed on your system, pyHeimdall will automatically discover its features and allow you to use them as long as any other `default <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/tree/main/src/heimdall/connectors>`_ or `external <https://gitlab.huma-num.fr/datasphere/heimdall/connectors>`_ connector.


*************
Is it tested?
*************

Of course!
Here's `the coverage report <https://datasphere.gitpages.huma-num.fr/heimdall/connectors/mariadb/coverage/index.html>`_.


*********************
How can I contribute?
*********************

This project welcomes any feedback or proposal.
Details can be accessed `here <https://gitlab.huma-num.fr/datasphere/heimdall/python/-/blob/main/CONTRIBUTING.rst>`_


*******
License
*******

`GNU Affero General Public License version 3.0 or later <https://choosealicense.com/licenses/agpl/>`_
