# -*- coding: utf-8 -*-
"""\
* *[IcmLib]* :: For providing jekyll service instances.
"""

import typing

icmInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** concept             -- Description of concept
**      [End-Of-Description]
""", }

icmInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]
**      How-Tos:
**      Import it, include it in g_importedCmndsModules and include its params in g_paramsExtraSpecify.
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
icmInfo['moduleName'] = "siJekyll"
####+END:

####+BEGIN: bx:icm:py:version-timestamp :style "date"
icmInfo['version'] = "202112254422"
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
*  This file:/bisos/git/auth/bxRepos/bisos-pip/pals/py3/bisos/pals/siJekyll.py :: [[elisp:(org-cycle)][| ]]
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

from bisos.icm import clsMethod
# from bisos.icm import fp

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.pals import palsBases

from bisos import bpf


####+BEGIN: bx:icm:python:icmItem :itemType "=ImportICMs=" :itemTitle "*Imported Commands Modules*"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =ImportICMs= :: *Imported Commands Modules*  [[elisp:(org-cycle)][| ]]
"""
####+END:

g_importedCmndsModules = [       # Enumerate modules from which CMNDs become invokable
    'blee.icmPlayer.bleep',
    'bisos.pals.siJekyll',
    'bisos.pals.palsBases',
]


####+BEGIN: bx:icm:python:func :funcName "g_paramsExtraSpecify" :comment "FWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-FrameWrk :: /g_paramsExtraSpecify/ =FWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
"""
def g_paramsExtraSpecify(
    parser,
):
####+END:
    """Module Specific Command Line Parameters.
    g_argsExtraSpecify is passed to G_main and is executed before argsSetup (can not be decorated)
    """
    G = icm.IcmGlobalContext()
    icmParams = icm.ICM_ParamDict()

    bleep.commonParamsSpecify(icmParams)

    clsMethod.commonParamsSpecify(icmParams)  # --cls, --method

    bpo.commonParamsSpecify(icmParams)
    palsSis.commonParamsSpecify(icmParams)

    icm.argsparseBasedOnIcmParams(parser, icmParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(icmParams)

    return


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "examples" :cmndType "Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "bpoId si" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cmnd-FWrk  :: /examples/ =FrameWrk: ICM Examples= parsMand= parsOpt=bpoId si argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class examples(icm.Cmnd):
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] ICM examples, all on one place.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = "pmi_ByD-100001"
        oneSiRelPath = "jekyll/main"

        if bpoId: oneBpo = bpoId
        if si: oneSiRelPath = si

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Examples For Specified Params*')

        cmndName = "examples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='none', comment="# For specified bpoId and si")

        icm.cmndExampleMenuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# empty place holder")

        icm.cmndExampleMenuChapter('*siBaseStart -- Initialize siBaseDir*')

        cmndName = "siBaseAssemble" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs more testing")

        cmndName = "siBaseUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# siBaseAssemble + palsBases.basesUpdateSi (logs,data)")

        icm.cmndExampleMenuChapter('*Jekyll Site Initializations*')

        cmndName = "siInvoke" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath ; cps['method'] = 'jekyllSiteAdd'
        menuItem(verbosity='little', comment="# general purpose testing")
        menuItem(verbosity='full', comment="# general purpose testing")

        digestedSvcsExamples().cmnd(bpoId=oneBpo,)

        return(cmndOutcome)

####+BEGIN: bx:icm:py3:section :title "ICM Example Commands"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *ICM Example Commands*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "svcExamples" :cmndType "ICM-Ex-Cmnd"  :comment "Full Action Examples" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "999" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /svcExamples/ =Full Action Examples= parsMand=bpoId si parsOpt= argsMin=0 argsMax=999 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class svcExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
        si=None,         # or Cmnd-Input
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

            callParamsDict = {'bpoId': bpoId, 'si': si, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']
            si = callParamsDict['si']

            cmndArgsSpecDict = self.cmndArgsSpec()
            if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
                return cmndOutcome
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        cmndName = "fullDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        cmndName = "serviceDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        return(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "configExamples" :cmndType "ICM-Ex-Cmnd"  :comment "configUpdate etc" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /configExamples/ =configUpdate etc= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class configExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Service Config Actions*')

        cmndName = "jekyll_configUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# Place Holder")

        return(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "setupExamples" :cmndType "ICM-Ex-Cmnd"  :comment "baseUpdate, etc" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /setupExamples/ =baseUpdate, etc= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class setupExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        # logControler = icm.LOG_Control()
        # logControler.loggerSetLevel(20)

        icm.icmExampleMyName(G.icmMyName(), G.icmMyFullName())

        icm.G_commonBriefExamples()

        bleep.examples_icmBasic()

        icm.cmndExampleMenuChapter('*Service Setup Actions*')

        cmndName = "basesUpdateSi" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# to be tested")

        return(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "hereExamples" :cmndType "ICM-Ex-Cmnd"  :comment "baseUpdate, etc" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /hereExamples/ =baseUpdate, etc= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class hereExamples(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] To be inserted in hereAgent.py menus.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        icm.cmndExampleMenuChapter('*SiJekyll Here Actions*')

        cmndName = "siJekyll_siteDumpAndTriggers" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs to be followed by triggers")

        cmndName = "siJekyll_siteDump" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs to be followed by triggers")

        cmndName = "siJekyll_siteTriggers" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# args ro be added")


        return(cmndOutcome)



####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "digestedSvcsExamples" :cmndType "ICM-Ex-Cmnd"  :comment "Examples lines for each digested svc" :parsMand "" :parsOpt "bpoId" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Ex-Cmnd :: /digestedSvcsExamples/ =Examples lines for each digested svc= parsMand= parsOpt=bpoId argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class digestedSvcsExamples(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        bpoId=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'bpoId': bpoId, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            bpoId = callParamsDict['bpoId']

####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        oneBpo = bpoId

        # logControler = icm.LOG_Control()
        # logControler.loggerSetLevel(20)

        icm.cmndExampleMenuChapter('*Pals BPO-Info*')

        cmndArgs = "" ;  cps=cpsInit() ; cps['bpoId'] = oneBpo ;
        cmndName = "examples" ; menuItem(icmName="palsBpoManage.py",  verbosity='none')
        cmndName = "enabledSisInfo" ; menuItem(icmName="palsBpoManage.py",  verbosity='little')

        icm.cmndExampleMenuChapter('*Existing PALS-VirDom-SIs Example-Cmnds*')

        thisBpo = palsBpo.obtainBpo(oneBpo,)
        thisBpo.sis.sisDigest()

        cmndArgs = "" ; cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            eachSiId = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            if "jekyll" in eachSiId:
                cps['si'] = eachSiId
                cmndName = "configExamples" ; menuItem(verbosity='none', comment="# actions impacting plone site")
                cmndName = "setupExamples" ; menuItem(verbosity='none', comment="# create siBases, etc")

        return(cmndOutcome)


####+BEGIN: bx:icm:py3:section :title "ICM Commands"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *ICM Commands*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "fullUpdate" :comment "Place Holder" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /fullUpdate/ =Place Holder= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class fullUpdate(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siBaseAssemble" :comment "Assemble a base for si" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siBaseAssemble/ =Assemble a base for si= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siBaseAssemble(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Initial action that creates the siRepo
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return cmndOutcome.set(opError=icm.EH_critical_usageError(f"missing bpoId={bpoId}"))

        svcProvBaseDir = palsSis.si_svcBaseDir(bpoId, si)
        if not os.path.exists(svcProvBaseDir):
            os.makedirs(svcProvBaseDir)
            # NOTYET, addition of siInfo for svcProvider
        else:
            icm.TM_here(f"svcProvBaseDir={svcProvBaseDir} exists, creation skipped.")

        svcInstanceBaseDir = palsSis.si_instanceBaseDir(bpoId, si)
        if not os.path.exists(svcInstanceBaseDir):
            os.makedirs(svcInstanceBaseDir)
        else:
            icm.TM_here(f"svcInstanceBaseDir={svcInstanceBaseDir} exists, creation skipped.")

        icm.TM_here(f"svcInstanceBaseDir={svcInstanceBaseDir} being updated.")

        thisBpo.sis.sisDigest()

        siPath = palsSis.siIdToSiPath(bpoId, si)
        thisSi = palsSis.EffectiveSis.givenSiPathFindSiObj(bpoId, siPath,)

        thisSi.assemble() # type: ignore

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siBaseUpdate" :comment "Place holder for logBase as root" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siBaseUpdate/ =Place holder for logBase as root= parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siBaseUpdate(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if siBaseAssemble(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(icm.EH_badOutcome(cmndOutcome))

        if palsBases.basesUpdateSi(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(icm.EH_badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siJekyll_siteCreate" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siJekyll_siteCreate/ parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siJekyll_siteCreate(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        jekyllInstance = Jekyll_Inst(bpoId, si)

        dataDir = os.path.join(jekyllInstance.siPath, "data")
        bpf.dir.createIfNotThere(dataDir)

        inDirSubProc = bpf.subProc.WOpW(invedBy=self, cd=dataDir)

        # site is the name of the site being created
        if inDirSubProc.bash(f"""jekyll new site""",
        ).isProblematic():  return(icm.EH_badOutcome(cmndOutcome))

        if inDirSubProc.bash(f"""ls -ld site""",
        ).isProblematic():  return(icm.EH_badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siJekyll_siteDumpAndTriggers" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siJekyll_siteDumpAndTriggers/ parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siJekyll_siteDumpAndTriggers(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]] Status: Has not been tested yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if siJekyll_siteDump(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(icm.EH_badOutcome(cmndOutcome))

        if siJekyll_siteTriggers(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(icm.EH_badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siJekyll_siteDump" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siJekyll_siteDump/ parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siJekyll_siteDump(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
***** TODO du_jekyll/sites/main/dump needs to be created and parameterized.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        jekyllInstance  = Jekyll_Inst(bpoId, si)

        palsBaseDir = bpo.bpoBaseDir_obtain(bpoId,)
        dumpDir = os.path.join(palsBaseDir, "du_jekyll/sites/main/dump")

        siteDir = os.path.join(jekyllInstance.siPath, "data/site")

        inDirSubProc = bpf.subProc.WOpW(invedBy=self, cd=siteDir)
        # Build as a pure html site
        if inDirSubProc.bash(f"""bundle exec jekyll build -d {dumpDir}""",
        ).isProblematic():  return(icm.EH_badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "siJekyll_siteTriggers" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /siJekyll_siteTriggers/ parsMand=bpoId si parsOpt= argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class siJekyll_siteTriggers(icm.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Triggers can be specified as destination args.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if bpf.subProc.WOpW(invedBy=self,).bash(
                f"""cntnrGitShTriggers.py -i gitSh_invoker_trigger_jekyll /tmp/trigger-jekyll""",
        ).isProblematic():  return(icm.EH_badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:icm:py3:section :title "Supporting Classes And Functions"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:dblock:python:class :className "SiRepo_Jekyll" :superClass "palsSis.SiRepo" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /SiRepo_Jekyll/ palsSis.SiRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class SiRepo_Jekyll(palsSis.SiRepo):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("eee  SiRepo_Jekyll")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass


####+BEGIN: bx:dblock:python:class :className "Jekyll_Inst" :superClass "palsSis.SiSvcInst" :comment "Expected to be subclassed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /Jekyll_Inst/ palsSis.SiSvcInst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class Jekyll_Inst(palsSis.SiSvcInst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            si,
    ):
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, si,):
            icm.EH_critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={si}")
        else:
            super().__init__(bpoId, si,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

        self.bpo = palsBpo.obtainBpo(bpoId,)
        self.siPath = palsSis.siIdToSiPath(bpoId, si,)
        self.siId = si
        self.invContext = invoke.context.Context(config=None)

    def obtainFromFPs(self,):
        pass

    def setVar(self, value,):
        self.setMyVar = value

    def domainShow(self,):
        pass

    def stdout(self,):
        pass

    def assemble(self,):
        svcInstanceBaseDir = self.siPath
        bsiAgentFile = os.path.join(svcInstanceBaseDir, "bsiAgent.sh")

        shutil.copyfile("/bisos/apps/defaults/pals/si/common/bsiAgent.sh", bsiAgentFile)

        siInfoBase = os.path.join(svcInstanceBaseDir, "siInfo")

        if not os.path.exists(siInfoBase): os.makedirs(siInfoBase)

        icm.FILE_ParamWriteTo(siInfoBase, 'svcCapability', __file__) # NOTYET, last part

        invContext = invoke.context.Context(config=None)

        with invContext.cd(svcInstanceBaseDir):
            invContext.run("bxtStartCommon.sh  -v -n showRun -i startObjectGen auxLeaf")



####+BEGIN: bx:icm:py3:func :funcName "digestAtSvcProv_obsoleted" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-      :: /digestAtSvcProv_obsoleted/  [[elisp:(org-cycle)][| ]]
"""
def digestAtSvcProv_obsoleted(
####+END:
     bpoId,
     siRepoBase,
):
    icm.TM_here("Incomplete")
    palsSis.createSiObj(bpoId, siRepoBase, SiRepo_Jekyll)

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for (_, dirNames, _,) in os.walk(siRepoBase):
        for each in dirNames:
            if each == "siInfo":
                continue
            # verify that it is a svcInstance
            siRepoPath = os.path.join(siRepoBase, each)
            digestPrimSvcInstance_obsoleted(bpoId, siRepoPath, each,)
            thisBpo.sis.svcInst_primary_enabled.append(siRepoPath,)
        break


####+BEGIN: bx:icm:py3:func :funcName "digestPrimSvcInstance_obsoleted" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase instanceName"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-      :: /digestPrimSvcInstance_obsoleted/  [[elisp:(org-cycle)][| ]]
"""
def digestPrimSvcInstance_obsoleted(
####+END:
    bpoId,
    siRepoBase,
    instanceName,
):
    icm.TM_here("Incomplete")

    thisSi = palsSis.createSiObj(bpoId, siRepoBase, Jekyll_Inst)

    thisSi.setVar(22) # type: ignore

    icm.TM_here(f"bpoId={bpoId}, siRepoBase={siRepoBase}, instanceName={instanceName}")


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
