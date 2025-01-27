# -*- coding: utf-8 -*-
"""\
* *[IcmLib]* :: Sets-up/updates pals, palsSivd and palsSi bases by creating links to var,tmp, etc.
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
** TODO [[elisp:(org-cycle)][| ]]  Current     :: For now it is an ICM. Turn it into ICM-Lib. [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:icm:py:name :style "fileName"
icmInfo['moduleName'] = "palsBases"
####+END:

####+BEGIN: bx:icm:py:version-timestamp :style "date"
icmInfo['version'] = "202112254432"
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
*  This file:/bisos/git/auth/bxRepos/bisos-pip/pals/py3/bisos/pals/palsBases.py :: [[elisp:(org-cycle)][| ]]
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


import os
# import pwd
# import grp
import collections
# import enum
#

#import traceback

import pathlib

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/importUcfIcmG.py"
from unisos import ucf
from unisos import icm

icm.unusedSuppressForEval(ucf.__file__)  # in case icm and ucf are not used

G = icm.IcmGlobalContext()
# G.icmLibsAppend = __file__
# G.icmCmndsLibsAppend = __file__
####+END:

# from bisos.platform import bxPlatformConfig
# from bisos.platform import bxPlatformThis

# from bisos.basics import pattern

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.icm import fpath

import pathlib

<<<<<<< HEAD
####+BEGIN: bx:icm:py3:section :title "BaseGet Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *BaseGet Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:icm:py3:func :funcName "palsBaseThere" :funcType "" :retType "" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-      [[elisp:(outline-show-subtree+toggle)][||]] /palsBaseThere/  [[elisp:(org-cycle)][| ]]
#+end_org """
def palsBaseThere(
=======

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "icmParams"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-ParSpec :: /commonParamsSpecify/ retType= argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
    icmParams,
):
####+END:
    icmParams.parDictAdd(
        parName='there',
        parDescription="Path to There",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--there',
    )


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "thereExamples" :cmndType "Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "there" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cmnd-FWrk  :: /thereExamples/ =FrameWrk: ICM Examples= parsMand= parsOpt=there argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class thereExamples(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'there', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        there=None,         # or Cmnd-Input
    ) -> icm.OpOutcome:
        cmndOutcome = self.getOpOutcome()
        if not self.obtainDocStr:
            if interactive:
                if not self.cmndLineValidate(outcome=cmndOutcome):
                    return cmndOutcome

            callParamsDict = {'there': there, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            there = callParamsDict['there']

####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): icm.ex_gExecMenuItem(execLine=cmndStr)

        therePath = os.getcwd()
        if there: therePath = there

        icm.cmndExampleMenuChapter('*PalsAbsorb There*')

        cmndName = "palsAbsorbHere" ; cmndArgs = "" ; cps=cpsInit() ; menuItem(verbosity='little')
        cmndArgs = "palsId" ; menuItem(verbosity='little')

        cmndName = "palsAbsorbThere" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['there'] = therePath ; menuItem(verbosity='little')
        cmndArgs = "instRelPath" ; menuItem(verbosity='little')

        return(cmndOutcome)




####+BEGIN: bx:icm:py3:section :title "BaseGet Classes"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *BaseGet Functions*  [[elisp:(org-cycle)][| ]]
"""
####+END:



####+BEGIN: bx:dblock:python:class :className "BpoAbsorbed" :superClass "" :comment "Is super class for PalsAbsorbed" :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /BpoAbsorbed/ object =Is super class for PalsAbsorbed=  [[elisp:(org-cycle)][| ]]
"""
class BpoAbsorbed(object):
>>>>>>> b0098b755777439380913124b8872f2b7af5eac2
####+END:
    """
** Based on therePath, corresponding Bpo is identified and absorbed.
*** TODO Common bpo repositories need to be analyzed and absorbed as well.
"""
    def __init__(
            self,
            therePath,
    ):
        pathList = pathlib.Path(therePath).parts

        if len(pathList) < 5:
            icm.EH_problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[0] != "/":
            icm.EH_problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[1] != "bxo":
            icm.EH_problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[2] != "r3":
            icm.EH_problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[3] != "iso":
            icm.EH_problem_usageError(f"bad input: {therePath}")
            raise ValueError

        self._bpoId = pathList[4]
        self._bpoHome = os.path.expanduser(f"~{self._bpoId}")

    @property
    def bpoId(self) -> str:
        return self._bpoId

    @property
    def bpoHome(self) -> str:
        return self._bpoHome


####+BEGIN: bx:dblock:python:class :className "PalsAbsorbed" :superClass "BpoAbsorbed" :comment "Absorbes si, sivd, etc." :classType "basic"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Class-basic :: /PalsAbsorbed/ BpoAbsorbed =Absorbes si, sivd, etc.=  [[elisp:(org-cycle)][| ]]
"""
class PalsAbsorbed(BpoAbsorbed):
####+END:
    """
** Based on therePath, corresponding Bpo is identified and absorbed.
*** TODO Common bpo repositories need to be analyzed and absorbed as well.
"""
    def __init__(
            self,
            therePath,
    ):
        super().__init__(therePath)

        self.siEffective = None
        self.sivdEffective = None

        pathList = pathlib.Path(therePath).parts

        # >= 5
        self._palsId = self.bpoId
        self._palsHome = self.bpoHome

        self._si_svcProv = ""
        self._si_svcInst = ""

        self._sivd_svcProv = ""
        self._sivd_svcType = ""
        self._sivd_svcInst = ""

        self._liveParams = ""

        self._si_instRelPath = ""
        self._sivd_instRelPath = ""

        if len(pathList) > 5:
            sansSi = pathList[5].removeprefix("si_")
            sansSivd = pathList[5].removeprefix("sivd_")

            if sansSi in palsSis.PalsSis.svcProv_primary_available():
                self._si_svcProv = sansSi
            elif sansSivd in palsSis.PalsSis.svcProv_virDom_available():
                self._sivd_SvcProv = sansSivd
            elif pathList[5] == "liveParams":
                self._liveParams = pathList[5]
            else:
                icm.EH_problem_usageError(f"bad input: {therePath}")
                return

        if len(pathList) > 6:
            if self._si_svcProv:
                self._si_svcInst = pathList[6]
                self._si_instRelPath = f"{self._si_svcProv}/{pathList[6]}"
            elif self._sivd_svcProv:
                self._sivd_svcType = pathList[6]
            else:
                icm.EH_problem_usageError(f"bad input: {therePath}")
                return

        if len(pathList) > 7:
            if self._sivd_svcProv:
                self._sivd_svcInst = pathList[7]
                self._sivd_instRelPath = f"{pathList[5]}/{pathList[6]}/{pathList[7]}"
            else:
                icm.EH_problem_usageError(f"bad input: {therePath}")
                return

    @property
    def palsId(self) -> str:
        return self._palsId

    @property
    def palsHome(self) -> str:
        return self._palsHome

    @property
    def si_svcProv(self) -> str:
        return self._si_svcProv

    @property
    def si_svcInst(self) -> str:
        return self._si_svcInst

    @property
    def si_instRelPath(self) -> str:
        return self._si_instRelPath

    @property
    def sivd_svcProv(self) -> str:
        return self._sivd_svcProv

    @property
    def sivd_svcType(self) -> str:
        return self._sivd_svcType

    @property
    def sivd_svcInst(self) -> str:
        return self._sivd_svcInst

    @property
    def sivd_instRelPath(self) -> str:
        return self._sivd_instRelPath

    def getAttrByName(self,
                      name: str,
                      ):
        if name == 'palsId':
            return self.palsId
        if name == 'instRelPath':
            if self.sivd_instRelPath:
                return self.sivd_instRelPath
            elif self.si_instRelPath:
                return self.si_instRelPath
            else:
                return  "Missing instRelPath"

        else:
            return "Unknown"


####+BEGIN: bx:icm:py3:section :title "ICM Commands"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *ICM Commands*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "palsAbsorbThere" :parsMand "there" :parsOpt "" :argsMin "0" :argsMax "5" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /palsAbsorbThere/ parsMand=there parsOpt= argsMin=0 argsMax=5 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class palsAbsorbThere(icm.Cmnd):
    cmndParamsMandatory = [ 'there', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        there=None,         # or Cmnd-Input
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

            callParamsDict = {'there': there, }
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome
            there = callParamsDict['there']

            cmndArgsSpecDict = self.cmndArgsSpec()
            if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
                return cmndOutcome
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Preformed fullActions, AcctCreat, NonInteractive, ReposCreate
***** TODO Not implemeted yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        absorbedPals = PalsAbsorbed(there)

        cmndArgs = list(self.cmndArgsGet("0&5", cmndArgsSpecDict, effectiveArgsList))  # type: ignore
        #

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&5")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices
        if len(cmndArgs) <= 2:
            for each in cmndArgs:
                print(f"""{absorbedPals.getAttrByName(each,)}""")
        else:
            print(f"palsId={absorbedPals.palsId}")
            print(f"sivd_svcProv={absorbedPals.sivd_svcProv}")
            print(f"si_svcProv={absorbedPals.si_svcProv}")
            print(f"si_svcInst={absorbedPals.si_svcInst}")
            print(f"si_instRelPath={absorbedPals.si_instRelPath}")

        return icm.opSuccessAnNoResult(cmndOutcome)


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
            argPosition="0&5",
            argName="cmndArgs",
            argDefault='all',
            argChoices=['all', 'palsId', 'instRelPath', 'other',],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: bx:icm:python:cmnd:classHead :cmndName "palsAbsorbHere" :comment "" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "5" :asFunc "" :interactiveP ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  ICM-Cmnd   :: /palsAbsorbHere/ parsMand= parsOpt= argsMin=0 argsMax=5 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class palsAbsorbHere(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
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

            callParamsDict = {}
            if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
                return cmndOutcome

            cmndArgsSpecDict = self.cmndArgsSpec()
            if not self.cmndArgsValidate(effectiveArgsList, cmndArgsSpecDict, outcome=cmndOutcome):
                return cmndOutcome
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Preformed fullActions, AcctCreat, NonInteractive, ReposCreate
***** TODO Not implemeted yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        cmndOutcome = palsAbsorbThere().cmnd(
             there=os.getcwd(),
             argsList=effectiveArgsList,
        )

        return icm.opSuccessAnNoResult(cmndOutcome)

####+BEGIN: bx:icm:py3:section :title "End Of Editable Text"
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    :: *End Of Editable Text*  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
