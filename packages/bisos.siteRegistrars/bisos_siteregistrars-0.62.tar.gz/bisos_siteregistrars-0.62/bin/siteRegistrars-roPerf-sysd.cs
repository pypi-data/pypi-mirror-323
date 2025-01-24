#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/auth/bxRepos/bisos-pip/binsprep/py3/bin/exmpl-func-binsPrep.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/lcnt/lcntScreencasting/subTitles/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b

from bisos.debian import systemdSeed

def sysdUnitFileFunc():
    """Produce the unit file as a string. execPath can be different for testing vs stationable."""

    # Sometimes we may be running this script in the cwd -- shutil.which  does not do the equivalent of -a
    cmndOutcome = b.subProc.WOpW(invedBy=None, log=0).bash(
                f"""which -a svcPerfSiteRegistrars.cs | grep -v '\./svcPerfSiteRegistrars.cs' | head -1""",
    )
    if cmndOutcome.isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))
    execPath = cmndOutcome.stdout.strip()
    # print(execPath)

    # ExecStart={execPath} -v 20 --svcName="svcSiteRegistrars"  -i csPerformer

    templateStr = f"""
[Unit]
Description=Site Registrar Service
Documentation=man:siteRegistrar(1)

[Service]
ExecStart={execPath} -v 1 --callTrackings monitor+ --callTrackings invoke+  --svcName="svcSiteRegistrars"  -i csPerformer
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
    return templateStr


systemdSeed.setup(
    seedType="sysdSysUnit",  # or userUnit
    sysdUnitName="siteRegistrars",
    sysdUnitFileFunc=sysdUnitFileFunc,
)


####+BEGIN: b:py3:cs:seed/withWhich :seedName "/bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  seed       [[elisp:(outline-show-subtree+toggle)][||]] <</bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs>>   [[elisp:(org-cycle)][| ]]
#+end_org """
import shutil
import os
import sys

seedName = '/bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs'
seedPath = shutil.which(seedName)
if seedPath is None:
    print(f'sys.exit() --- which found nothing for {seedName} --- Aborting')
    sys.exit()

__file__ = os.path.abspath(seedPath)
with open(__file__) as f:
    exec(compile(f.read(), __file__, 'exec'))

####+END:
