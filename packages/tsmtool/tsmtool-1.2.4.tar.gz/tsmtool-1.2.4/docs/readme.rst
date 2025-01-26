
Tarsnap Status Monitor Reporting Tool
=====================================


.. image:: https://img.shields.io/github/license/rstms/tsmtool
   :target: https://raw.githubusercontent.com/rstms/tsmtool/master/LICENSE
   :alt: Image



.. image:: https://img.shields.io/pypi/v/tsmtool.svg
   :target: https://pypi.org/project/tsmtool/
   :alt: Image



.. image:: https://circleci.com/gh/rstms/tsmtool/tree/master.svg?style=shield
   :target: https://app.circleci.com/pipelines/github/rstms/tsmtool?branch=master&filter=all
   :alt: Image



.. image:: https://readthedocs.org/projects/tsmtool/badge/?version=latest
   :target: http://tsmtool.readthedocs.io/
   :alt: Image



.. image:: https://pyup.io/repos/github/rstms/tsmtool/shield.svg
   :target: https://pyup.io/account/repos/github/rstms/tsmtool/
   :alt: Image


Tarsnap Status Monitor

Introduction
------------

The most excellent backup service `Tarsnap <https://www.tarsnap.com>`_ provides a clean
and functional interface for managing one's account.  This tool connects to that web
interface and queries data, producing a JSON-formated report.  The current balance is
read, and an estimated monthly cost is calculated based on the site's daily cost data.

Example Output
^^^^^^^^^^^^^^

Here's an example of output from the author's tarsnap account:

.. code-block::

   (tsmtool) mkrueger@beaker:~/src/tsmtool$ tsmtool rstms
   {
     "balance": 32.51,
     "account": "mkrueger@rstms.net",
     "monthly_cost": 23.51
   }

Configuration
-------------

A config file may be used for account data, or the email account / password may be passed as command line options.
The config file is a whitespace delimited text file with one line per account.
Each line has these fields:

``~/.tsmtool``\ : 

.. code-block::

   ACCOUNT_NAME    EMAIL_ADDRESS   PASSWORD


* Free software: MIT license
* Documentation: https://tsmtool.readthedocs.io.

Credits
-------

`Tarsnap <https://www.tarsnap.com>`_ 

This package was created with Cookiecutter and ``rstms/cookiecutter-python-cli``\ , a fork of the ``audreyr/cookiecutter-pypackage`` project template.

`audreyr/cookiecutter <https://github.com/audreyr/cookiecutter>`_
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`_
`rstms/cookiecutter-python-cli <https://github.com/rstms/cookiecutter-python-cli>`_
