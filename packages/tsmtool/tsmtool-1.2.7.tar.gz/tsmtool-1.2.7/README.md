# Tarsnap Status Monitor Reporting Tool


[![Image](https://img.shields.io/github/license/rstms/tsmtool)](https://raw.githubusercontent.com/rstms/tsmtool/master/LICENSE)

[![Image](https://img.shields.io/pypi/v/tsmtool.svg)](https://pypi.org/project/tsmtool/)

[![Image](https://circleci.com/gh/rstms/tsmtool/tree/master.svg?style=shield)](https://app.circleci.com/pipelines/github/rstms/tsmtool?branch=master&filter=all)

[![Image](https://readthedocs.org/projects/tsmtool/badge/?version=latest)](http://tsmtool.readthedocs.io/)

[![Image](https://pyup.io/repos/github/rstms/tsmtool/shield.svg)](https://pyup.io/account/repos/github/rstms/tsmtool/)

Tarsnap Status Monitor

## Introduction 
The most excellent backup service [Tarsnap](https://www.tarsnap.com) provides a clean
and functional interface for managing one's account.  This tool connects to that web
interface and queries data, producing a report as a table or JSON.  The current balance is
read, and an estimated monthly cost is calculated based on the site's daily cost data.

### Example Output
Here's an example of output from the author's tarsnap account:
```
(tsmtool) mkrueger@beaker:~/src/tsmtool$ tsmtool --json rstms
{
  "balance": 32.51,
  "account": "mkrueger@rstms.net",
  "monthly_cost": 23.51
}
```

## Configuration 
A config file may be used for account data, or the email account / password may be passed as command line options.
The config file is a whitespace delimited text file with one line per account.
Each line has these fields:

`~/.tsmtool`: 
```
ACCOUNT_NAME    EMAIL_ADDRESS   PASSWORD
```

* Free software: MIT license
* Documentation: https://tsmtool.readthedocs.io.



## Credits

[Tarsnap](https://www.tarsnap.com) 

This package was created with Cookiecutter and `rstms/cookiecutter-python-cli`, a fork of the `audreyr/cookiecutter-pypackage` project template.

[audreyr/cookiecutter](https://github.com/audreyr/cookiecutter)
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
[rstms/cookiecutter-python-cli](https://github.com/rstms/cookiecutter-python-cli)
```
```
