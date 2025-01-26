![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CircleCI](https://dl.circleci.com/insights-snapshot/gh/hasii2011/untanglepyut/master/main/badge.svg?window=30d)](https://app.circleci.com/insights/github/hasii2011/untanglepyut/workflows/main/overview?branch=master&reporting-window=last-30-days&insights-snapshot=true)

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/untanglepyut/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/untanglepyut/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI version](https://badge.fury.io/py/untanglepyut.svg)](https://badge.fury.io/py/untanglepyut)

This project is intended to be used by [Pyut Plugin](https://github.com/hasii2011/pyutplugincore) developers to convert [Pyut](https://github.com/hasii2011/PyUt) XML files to the [Ogl Model](https://github.com/hasii2011/ogl) classes.  These model classes can then be used by the Pyut UI to display as UML Diagrams.

------

Use as follows:

```python
from untanglepyut.Types import Document
from untanglepyut.Types import DocumentTitle

from untanglepyut.Types import UntangledOglClasses
from untanglepyut.Types import UntangledOglLinks
from untanglepyut.Types import UntangledOglNotes
from untanglepyut.Types import UntangledOglTexts

from untanglepyut.UnTangler import UnTangler

fqFileName: str = 'MultiLinkDocument.xml'
untangler: UnTangler = UnTangler()

untangler.untangleFile(fqFileName=fqFileName)

document: Document = untangler.documents[DocumentTitle('Diagram-1')]

oglClasses: UntangledOglClasses = document.oglClasses
oglLinks: UntangledOglLinks = document.oglLinks
oglNotes: UntangledOglNotes = document.oglNotes
oglTexts: UntangledOglTexts = document.oglTexts

```



The following is the UML diagram for the Pyut Untangler

![UntanglePyut](./docs/UntanglePyut.png)

___

## Developer Notes
This project uses [buildlackey](https://github.com/hasii2011/buildlackey) for day to day development builds


## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.
Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2025



---
I am concerned about GitHub's Copilot project

![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/SillyGitHub.png)

I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from
[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done  without my permission.  I do not consent to GitHub's use of this project's  code in Copilot.
