#!/bin/env python
# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: An =ICM=: a beginning template for development of new ICMs.
"""

import typing

icmInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': ["""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** concept             -- Desctiption of concept
**      [End-Of-Description]
"""], }

icmInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""


icmInfo['moduleStatus'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:icm:py:name :style "fileName"
icmInfo['moduleName'] = "sivdApache2"
####+END:

####+BEGIN: bx:icm:py:version-timestamp :style "date"
icmInfo['version'] = "202112254424"
####+END:

####+BEGIN: bx:icm:py:status :status "Production"
icmInfo['status']  = "Production"
####+END:

icmInfo['credits'] = ""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/icmInfo-mbNedaGplByStar.py"
icmInfo['authors'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
icmInfo['copyright'] = "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]"
icmInfo['licenses'] = "[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"
icmInfo['maintainers'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
icmInfo['contacts'] = "[[http://mohsen.1.banan.byname.net/contact]]"
icmInfo['partOf'] = "[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]"
####+END:

icmInfo['panel'] = "{}-Panel.org".format(icmInfo['moduleName'])
icmInfo['groupingType'] = "IcmGroupingType-pkged"
icmInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"


####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/bisos/git/auth/bxRepos/bisos-pip/pals/py3/bisos/pals/sivdApache2.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:


####+BEGIN: bx:icm:python:topControls :partof "bystar" :copyleft "halaal+minimal"
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
"""
####+END:
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/pyWorkBench.org"
"""
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Imports=  :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import collections
import os
import shutil
import invoke
# import tempfile

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/importUcfIcmBleepG.py"
from unisos import ucf
from unisos import icm

icm.unusedSuppressForEval(ucf.__file__)  # in case icm and ucf are not used

G = icm.IcmGlobalContext()
# G.icmLibsAppend = __file__
# G.icmCmndsLibsAppend = __file__

from blee.icmPlayer import bleep
####+END:

from bisos.basics import pyRunAs

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.pals import repoProfile
from bisos.pals import palsBases

from bisos.icm import shRun

####+BEGIN: bx:icm:py3:section :title "ICM Example Commands"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *ICM Example Commands*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "svcExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "999" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /svcExamples/ =FrameWrk: ICM Examples= parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=999 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class svcExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome
                effectiveArgsList = G.icmRunArgsGet().cmndArgs  # type: ignore
            else:
                effectiveArgsList = argsList

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

            cmndArgsSpecDict = self.cmndArgsSpec()
            if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
                return cmndOutcome
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd


        logControler = icm.LOG_Control()
        logControler.loggerSetLevel(20)

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "fullDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "serviceDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        icm.cmndExampleMenuChapter('*siBaseStart -- Initialize siBaseDir*')

        cmndName = "siBaseStart" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "sivdBaseUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        icm.cmndExampleMenuChapter('*dbaseInitialContent for Bystar Account*')

        cmndName = "palsBpoInfo" ; cmndArgs = "notyet" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')
        menuItem(verbosity='full')

        # ${G_myName} ${extraInfo} -p bpoId="${oneBystarAcct}" -p ss=${oneSr} -p dbase=banan -i imagesList | bueGimpManage.sh -h -v -n showRun -i scaleReplaceHeightTo 200
        # $( examplesSeperatorChapter "Access, Verification And Test" )
        # ${G_myName} ${extraInfo} -i  visitUrl

        return(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "configExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /configExamples/ =FrameWrk: ICM Examples= parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class configExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd

        # logControler = icm.LOG_Control()
        # logControler.loggerSetLevel(20)

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Service Config Actions*')

        cmndName = "sivd_configStdout" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configVerify" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configInfo" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        return(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "setupExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /setupExamples/ =FrameWrk: ICM Examples= parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class setupExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd

        # logControler = icm.LOG_Control()
        # logControler.loggerSetLevel(20)

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Service Setup Actions*')

        cmndName = "basesUpdateSivd" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        return(cmndOutcome)



####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "digestedSvcsExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "bpoId" :argsMin "0" :argsMax "999" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /digestedSvcsExamples/ =FrameWrk: ICM Examples= parsMand= parsOpt=bpoId argsMin=0 argsMax=999 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class digestedSvcsExamples(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        argsList=[],         # or Args-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome
                effectiveArgsList = G.icmRunArgsGet().cmndArgs  # type: ignore
            else:
                effectiveArgsList = argsList

            callParamsDict = {'bpoId': bpoId, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']

            cmndArgsSpecDict = self.cmndArgsSpec()
            if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
                return cmndOutcome
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        # def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)
        def extMenuItem(verbosity): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, icmName=icmExName, verbosity=verbosity) # 'little' or 'none'

        oneBpo = bpoId

        # logControler = icm.LOG_Control()
        # logControler.loggerSetLevel(20)

        icm.cmndExampleMenuChapter('*Digest-SIs Example-Cmnds*')

        icmExName = "palsBpoManage.py" ; cmndName = "enabledSisInfo" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;
        extMenuItem(verbosity='none')

        icm.cmndExampleMenuChapter('*PALS-SIs Example-Cmnds*')

        thisBpo = palsBpo.obtainBpo(oneBpo,)
        thisBpo.sis.sisDigest()

        icmExName = "palsSiPlone3.py" ; cmndName = "examples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            cps['si'] = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            extMenuItem(verbosity='none')

        icm.cmndExampleMenuChapter('*Existing PALS-VirDom-SIs Example-Cmnds*')

        cmndName = "configExamples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSivdPath in thisBpo.sis.svcInst_virDom_enabled:
            cps['sivd'] = palsSis.siPathToSiId(oneBpo, eachSivdPath,)
            menuItem(verbosity='none')

        icm.cmndExampleMenuChapter('*Missing PALS-VirDom-SIs Example-Cmnds*')

        cmndName = "setupExamples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            eachSiId = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            for eachSivdPath in thisBpo.sis.svcInst_virDom_enabled:
                eachSivdId = palsSis.siPathToSiId(oneBpo, eachSivdPath,)
                if eachSiId in eachSivdId:
                    # print(f"skipping over {eachSiId} in {eachSivdId}")
                    break
                else:
                    missingSivdId = "apache2/{eachSiId}".format(eachSiId=eachSiId)
                    cps['sivd'] = missingSivdId
                    menuItem(verbosity='none')


        return(cmndOutcome)


####+BEGIN: bx:icm:python:method :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&999",
            argName="actionPars",
            argChoices='any',
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: bx:icm:py3:section :title "ICM Commands"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *ICM Commands*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "fullUpdate" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /fullUpdate/ parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class fullUpdate(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        print("NOTYET -- To be implemented.")

        return cmndOutcome.set(
            opError=icm.OpError.Success,  # type: ignore
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Creates bases.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siBaseStart" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siBaseStart/ parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siBaseStart(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        print(f"""{bpoId} {sivd}""")
        primInstanceBaseDir = palsSis.sivd_primInstanceBaseDir(bpoId, sivd)
        if not os.path.exists(primInstanceBaseDir):
            icm.EH_critical_usageError(f"primInstanceBaseDir={primInstanceBaseDir} should have existed.")
            return cmndOutcome.set(
                opError=icm.OpError.Failure,  # type: ignore
                opResults=None,
            )

        svcInstanceBaseDir = palsSis.sivd_instanceBaseDir(bpoId, sivd)
        if not os.path.exists(svcInstanceBaseDir):
            os.makedirs(svcInstanceBaseDir)

        print(f"svcInstanceBaseDir={svcInstanceBaseDir}")

        bsiAgentFile = os.path.join(svcInstanceBaseDir, "bsiAgent.sh")

        shutil.copyfile("/bisos/apps/defaults/pals/si/common/bsiAgent.sh", bsiAgentFile)

        siInfoBase = os.path.join(svcInstanceBaseDir, "siInfo")

        if not os.path.exists(siInfoBase): os.makedirs(siInfoBase)

        icm.FILE_ParamWriteTo(siInfoBase, 'svcCapability', __file__) # NOTYET, last part

        c = invoke.context.Context(config=None)

        with c.cd(svcInstanceBaseDir):
            c.run("bxtStartCommon.sh  -v -n showRun -i startObjectGen auxLeaf")


        c.run(f"ls -ld {primInstanceBaseDir}")

        return cmndOutcome.set(
            opError=icm.OpError.Success,  # type: ignore
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Creates bases.
"""


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivdBaseUpdate" :comment "Place holder for logBase as root" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivdBaseUpdate/ =Place holder for logBase as root= parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivdBaseUpdate(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        if palsBases.basesUpdateSivd(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                sivd=sivd,
        ).isProblematic(): return(icm.EH_badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=icm.OpError.Success,  # type: ignore
            opResults=None,
        )

####+BEGIN: bx:icm:python:method :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Method-anyOrNone :: /cmndDocStr/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(self):
####+END:
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Creates bases.
"""


####+BEGIN: bx:icm:python:method :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Method-anyOrNone :: /cmndArgsSpec/ retType=bool argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
"""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = icm.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName='dbaseName',
            argChoices='any',
            argDescription="Name of the geneweb database",
        )

        return cmndArgsSpecDict


####+BEGIN: bx:icm:py3:section :title "Class Definitions"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Class Definitions*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:dblock:python:class :className "A2SivdRepo" :superClass "bpo.BpoRepo" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2SivdRepo/ bpo.BpoRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2SivdRepo(bpo.BpoRepo):
####+END:
    """
** Refers to the entirety of bpo/apache2 repo.
"""
    def __init__(
            self,
            bpoId,
    ):
        super().__init__(bpoId)
        if not bpo.EffectiveBpos.givenBpoIdGetBpo(bpoId):
            icm.EH_critical_usageError(f"Missing BPO for {bpoId}")
            return

    def repoBase(self,):
        return os.path.join(self.bpo.baseDir, "apache2") # type: ignore


####+BEGIN: bx:dblock:python:class :className "AaSivdRepo_Apache2" :superClass "palsSis.SiRepo" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /AaSivdRepo_Apache2/ palsSis.SiRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class AaSivdRepo_Apache2(palsSis.SiRepo):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("eee  AaSivdRepo_Apache2")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass


####+BEGIN: bx:dblock:python:class :className "A2_Svc_Type" :superClass "palsSis.SiVirDomSvcType" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2_Svc_Type/ palsSis.SiVirDomSvcType =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2_Svc_Type(palsSis.SiVirDomSvcType):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("fff  A2_Svc_Type")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


####+BEGIN: bx:dblock:python:class :className "A2_Svc_Inst" :superClass "palsSis.SiSvcInst" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2_Svc_Inst/ palsSis.SiSvcInst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2_Svc_Inst(palsSis.SiSvcInst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("ggg  A2_Svc_Inst")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

    def obtainFromFPs(self,):
        pass


####+BEGIN: bx:dblock:python:class :className "A2_Plone3_Type" :superClass "A2_Svc_Type" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2_Plone3_Type/ A2_Svc_Type =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2_Plone3_Type(A2_Svc_Type):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
        self,
            bpoId,
            siPath,
    ):
        # print("hhh  A2_Plone3_Type")
        if palsSis.EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass

    def domainShow(self,):
        pass

    def stdout(self,):
        pass


####+BEGIN: bx:dblock:python:class :className "A2_Plone3_Inst" :superClass "A2_Svc_Inst" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2_Plone3_Inst/ A2_Svc_Inst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2_Plone3_Inst(A2_Svc_Inst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
        self,
            bpoId,
            siPath,
    ):
        # print("iii  A2_Plone3_Inst")
        if palsSis.EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

    def obtainFromFPs(self,):
        pass

    def setVar(self, value,):
        self.setMyVar = value

    def domainShow(self,):
        pass

    def stdout(self,):
        pass




####+BEGIN: bx:dblock:python:class :className "A2_Geneweb_VirDom" :superClass "A2_Svc_Type" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /A2_Geneweb_VirDom/ A2_Svc_Type =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class A2_Geneweb_VirDom(A2_Svc_Type):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
        self,
    ):
        pass

    def obtainFromFPs(self,):
        pass

    def domainShow(self,):
        pass

    def stdout(self,):
        pass



####+BEGIN: bx:icm:py3:section :title "Function Definitions"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Function Definitions*  [[elisp:(org-cycle)][| ]]
"""
####+END:


####+BEGINNOT: bx:icm:python:func :funcName "listOfA2VirDomTypes" :funcType "anyOrNone" :retType "List" :deco "" :argsList ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /listOfA2VirDomSvcs/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def listOfA2VirDomTypes() -> typing.List:
####+END:
    return (
        [
            'plone3',
            'geneweb',
            'squirrelmail',
            'django',
            'gitweb',
            'gitolite',
            'gallery',
            'jekyll',
            'www',
        ]
    )


####+BEGIN: bx:icm:python:func :funcName "digestAtVirDomSvcProv" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /digestAtVirDomSvcProv/ retType= argsList=(bpoId siRepoBase)  [[elisp:(org-cycle)][| ]]
"""
def digestAtVirDomSvcProv(
    bpoId,
    siRepoBase,
):
####+END:
    """
** TODO: Needs to be commented, generalized and re-written.
    """
    icm.TM_here("Incomplete")
    palsSis.createSiObj(bpoId, siRepoBase, AaSivdRepo_Apache2)

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for each in listOfA2VirDomTypes():
            siRepoPath = os.path.join(siRepoBase, each)
            if os.path.isdir(siRepoPath):
                if each == "plone3" or each == "jekyll":
                    plone3SvcTypeObj = palsSis.createSiObj(bpoId, siRepoPath, A2_Plone3_Type)
                    digestAtVirDomSvcType(bpoId, siRepoPath, plone3SvcTypeObj)
                    thisBpo.sis.svcType_virDom_enabled.append(siRepoPath)

                icm.TM_here(f"is {siRepoPath}")
            else:
                icm.TM_here(f"is NOT {siRepoPath} -- skipped")


####+BEGIN: bx:icm:python:func :funcName "digestAtVirDomSvcType" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /digestAtVirDomSvcType/ retType= argsList=(bpoId siRepoBase svcTypeObj)  [[elisp:(org-cycle)][| ]]
"""
def digestAtVirDomSvcType(
    bpoId,
    siRepoBase,
    svcTypeObj,
):
####+END:
    icm.TM_here("Incomplete")

    #palsBpo.createSiObj(bpoId, siRepoBase, AaSivdRepo_Apache2) # BAD USAGE

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for (_, dirNames, _,) in os.walk(siRepoBase):
        for each in dirNames:
            if each == "siInfo":
                continue
            # verify that it is a svcInstance
            siRepoPath = os.path.join(siRepoBase, each)
            digestVirDomSvcInstance(bpoId, siRepoPath, svcTypeObj, each)
            thisBpo.sis.svcInst_virDom_enabled.append(siRepoPath)
        break


####+BEGIN: bx:icm:python:func :funcName "digestVirDomSvcInstance" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj instanceName"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /digestVirDomSvcInstance/ retType= argsList=(bpoId siRepoBase svcTypeObj instanceName)  [[elisp:(org-cycle)][| ]]
"""
def digestVirDomSvcInstance(
    bpoId,
    siRepoBase,
    svcTypeObj,
    instanceName,
):
####+END:
    icm.TM_here("Incomplete")

    #thisSi = palsSis.createSiObj(bpoId, siRepoBase, A2_Plone3_Inst)

    #thisSi.setVar(22)

    icm.TM_here(f"bpoId={bpoId}, siRepoBase={siRepoBase}, svcTypeObj={svcTypeObj} instanceName={instanceName}")


####+BEGIN: bx:icm:python:func :funcName "sivdAsTag" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj instanceName"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /sivdAsTag/ retType= argsList=(bpoId siRepoBase svcTypeObj instanceName)  [[elisp:(org-cycle)][| ]]
"""
def sivdAsTag(
    bpoId,
    siRepoBase,
    svcTypeObj,
    instanceName,
):
####+END:
    virDomProvider = palsSis.si_svcName(sivd,)
    primarySvcName = palsSis.sivd_virDomSvcName(sivd,)
    primaryInstanceName = palsSis.si_instanceName(sivd,)

    icm.TM_here(f"virDomProvider={virDomProvider} primarySvcName={primarySvcName} primaryInstanceName={primaryInstanceName}")

    if not virDomProvider in palsSis.PalsSis.svcProv_virDom_available():
        return icm.EH_problem_usageError(
            f"Unexepected virDomProvider={virDomProvider}"
        )
    if not primarySvcName in palsSis.PalsSis.svcProv_primary_available():
        return icm.EH_problem_usageError(
            f"Unexepected primarySvcName={primarySvcName}"
        )

    virDomProvTag=""
    if virDomProvider == "apache2":
        virDomProvTag = "a2"
    elif virDomProvider == "qmail":
        virDomProvTag = "qm"
    else:
        return icm.EH_critical_oops("Implementation Error")

    capitalizedPrimarySvcName = primarySvcName[0].upper() + primarySvcName[1:]

    return f"""{virDomProvTag}{capitalizedPrimarySvcName}"""


####+BEGIN: bx:icm:py3:func :funcName "writeToFileAsRoot" :funcType "" :retType "" :deco "pyRunAs.User(\"root\")" :argsList ""  :comment "_ALERT_"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-      :: /writeToFileAsRoot/ =_ALERT_= deco=pyRunAs.User("root")  [[elisp:(org-cycle)][| ]]
"""
@pyRunAs.User("root")
def writeToFileAsRoot(
####+END:
        destFilePath,
        inBytes,
):
    with open(destFilePath, "w") as thisFile:
        thisFile.write(inBytes + '\n')



####+BEGIN: bx:icm:py3:section :title "sivd_config Abstracted Facilities"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *sivd_config Abstracted Facilities*  [[elisp:(org-cycle)][| ]]
"""
####+END:


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivd_configStdout" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivd_configStdout/ parsMand=bpoId sivd parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivd_configStdout(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:
        virDomProvider = palsSis.si_svcName(sivd,)
        primarySvcName = palsSis.sivd_virDomSvcName(sivd,)
        primaryInstanceName = palsSis.si_instanceName(sivd,)

        icm.TM_here(f"virDomProvider={virDomProvider} primarySvcName={primarySvcName} primaryInstanceName={primaryInstanceName}")

        if not virDomProvider in palsSis.PalsSis.svcProv_virDom_available():
            return icm.icm.EH_problem_usageError(
                f"Unexepected virDomProvider={virDomProvider}"
            )
        if not primarySvcName in palsSis.PalsSis.svcProv_primary_available():
            return icm.icm.EH_problem_usageError(
                f"Unexepected primarySvcName={primarySvcName}"
            )

        thisBpo = palsBpo.obtainBpo(bpoId,)
        #liveParamsInst = pattern.sameInstance(baseLiveTargets.PalsBase_LiveParams, bpoId)

        palsProfile = repoProfile.PalsRepo_Profile(bpoId)
        bpoFpsBaseInst = palsProfile.fps_baseMake()

        baseDomain = bpoFpsBaseInst.fps_getParam('baseDomain').parValueGet()
        #bystarType = bpoFpsBaseInst.fps_getParam('bystarType').parValueGet()
        #correspondingEntity = bpoFpsBaseInst.fps_getParam('correspondingEntity').parValueGet()

        siBaseDomain = "www.{baseDomain}".format(baseDomain=baseDomain)

        bpoBasePath = thisBpo.baseDir
        bpoSivdBasePath = palsSis.sivd_instanceBaseDir(
            bpoId,
            sivd,
        )

        configTemplateFuncName = f"{sivdAsTag(sivd,)}_configTemplate"

        if not configTemplateFuncName in globals():
            return icm.EH_critical_oops(f"Implementation Error -- Missing {configTemplateFuncName}")

        # globals()[key] is equivalent of getattr for current module
        resStr = globals()[configTemplateFuncName]().format(
            baseDomain=baseDomain,
            siBaseDomain=siBaseDomain,
            bpoBasePath=bpoBasePath,
            bpoSivdBasePath=bpoSivdBasePath,
        )

        if interactive:
            print(resStr)

        cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=resStr
        )

        return resStr

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivd_configUpdate" :comment "" :parsMand "" :parsOpt "bpoId sivd" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivd_configUpdate/ parsMand= parsOpt=bpoId sivd argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivd_configUpdate(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'sivd', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:

        if not (resStr := sivd_configStdout(cmndOutcome=cmndOutcome).cmnd(
            interactive=False,
            bpoId=bpoId,
            sivd=sivd,
        )):  return(icm.EH_badOutcome(cmndOutcome))


        palsProfile = repoProfile.PalsRepo_Profile(bpoId)
        bpoFpsBaseInst = palsProfile.fps_baseMake()

        baseDomain = bpoFpsBaseInst.fps_getParam('baseDomain').parValueGet()
        siBaseDomain = "www.{baseDomain}".format(baseDomain=baseDomain)

        configFilePath = sivd_configFilePath(siBaseDomain,)

        writeToFileAsRoot(configFilePath, resStr)

        if interactive:
            shRun.cmnds(f"""ls -l {configFilePath}""",
                       outcome=cmndOutcome,).log()

        shRun.sudoCmnds(f"""a2ensite {siBaseDomain}.conf""",
                        outcome=cmndOutcome,).log()

        shRun.sudoCmnds(f"""/etc/init.d/apache2 force-reload""",
                        outcome=cmndOutcome,).log()

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=siBaseDomain,
        )


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivd_configVerify" :comment "" :parsMand "" :parsOpt "bpoId sivd" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivd_configVerify/ parsMand= parsOpt=bpoId sivd argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivd_configVerify(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'sivd', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        sivd=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            sivd = callParamsDict['sivd']

####+END:
        return


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivd_configInfo" :comment "" :parsMand "" :parsOpt "bpoId si" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivd_configInfo/ parsMand= parsOpt=bpoId si argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivd_configInfo(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'si', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        si=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'si': si, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            si = callParamsDict['si']

####+END:
        return


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "sivd_configDelete" :comment "" :parsMand "" :parsOpt "bpoId si" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /sivd_configDelete/ parsMand= parsOpt=bpoId si argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class sivd_configDelete(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'si', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        si=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, 'si': si, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            si = callParamsDict['si']

####+END:
        return


####+BEGIN: bx:icm:py3:func :funcName "sivd_configFilePath" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /sivd_configFilePath/  [[elisp:(org-cycle)][| ]]
"""
def sivd_configFilePath(
####+END:
        siBaseDomain,
):

    result = os.path.join(
        "/etc/apache2/sites-available",
        "{siBaseDomain}.conf".format(siBaseDomain=siBaseDomain),
    )
    return result

####+BEGIN: bx:icm:py3:section :title "Apache2-PrimaryService Specific Facilities"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Apache2-PrimaryService Specific Facilities*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:func :funcName "a2Plone3_configTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /a2Plone3_configTemplate/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def a2Plone3_configTemplate():
####+END:
    templateStr = """
# VirtualHost for {siBaseDomain} Generated by G_myName:G_thisFunc on dateTag -- Do Not Hand Edit

<VirtualHost *:80>
    ServerName  {siBaseDomain}
    ServerAlias {baseDomain}
    ServerAdmin webmaster@{baseDomain}

    RewriteEngine On
    RewriteRule ^/(.*) http://127.0.0.1:8080/VirtualHostBase/http/{siBaseDomain}:80/{baseDomain}/VirtualHostRoot/\$1 [L,P]

    DocumentRoot {bpoSivdBasePath}/var/htdocs
    #ScriptAlias /cgi-bin/ "{bpoSivdBasePath}/cgi-bin/"
    ErrorLog {bpoSivdBasePath}/log/error_log
    CustomLog {bpoSivdBasePath}/log/access_log common

        <Directory />
                Options FollowSymLinks
                AllowOverride All
        </Directory>
        <Directory {bpoSivdBasePath}/htdocs>
                Options Indexes FollowSymLinks MultiViews
                AllowOverride All
                Order allow,deny
                allow from all
        </Directory>

        <Proxy "*">
	        Order deny,allow
	        Allow from all
        </Proxy>
</VirtualHost>
"""
    return templateStr

####+BEGIN: bx:icm:python:func :funcName "a2Jekyll_configTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /a2Jekyll_configTemplate/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def a2Jekyll_configTemplate():
####+END:
    templateStr = """

# VirtualHost for {siBaseDomain} Generated by G_myName:G_thisFunc on dateTag -- Do Not Hand Edit

<VirtualHost *:80>
    ServerName  {siBaseDomain}
    ServerAlias {baseDomain}
    ServerAdmin webmaster@{baseDomain}

    DocumentRoot {bpoSivdBasePath}/var/site
    #ScriptAlias /cgi-bin/ "{bpoSivdBasePath}/cgi-bin/"
    ErrorLog {bpoSivdBasePath}/log/error_log
    CustomLog {bpoSivdBasePath}/log/access_log common

    <Directory />
        Require all granted
    </Directory>

    <Directory {bpoSivdBasePath}/var/site>
        Options +Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
"""
    return templateStr


####+BEGIN: bx:icm:py3:section :title "Supporting Classes And Functions"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:py3:section :title "Common/Generic Facilities -- Library Candidates"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:py3:section :title "Unused Facilities -- Temporary Junk Yard"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Unused Facilities -- Temporary Junk Yard*  [[elisp:(org-cycle)][| ]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:icm:py3:section :title "End Of Editable Text"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *End Of Editable Text*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
