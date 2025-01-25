from __future__ import unicode_literals
import importlib
import json
import os
import re
import pymel.core as pm

from ciocore import data as coredata
from ciotemplate.expander import Expander
from ciopath.gpath import Path
from ciopath.gpath_list import PathList
from ciocore.package_environment import PackageEnvironment
from cioseq.sequence import Sequence

import maya.api.OpenMaya as om

from ciomaya.lib import const as k
from ciomaya.lib import context
from ciomaya.lib import scraper_utils


def maya_useNewAPI():
    pass


class conductorRender(om.MPxNode):
    # pass

    # static attributes
    aTitle = None

    aChunkSize = None
    
    aUseCustomRange = None
    aCustomRange = None
    aStartFrame = None
    aEndFrame = None
    aByFrame = None
    aAnimation = None
    aUseScoutFrames = None
    aScoutFrames = None

    aTaskTemplate = None

    aInstanceTypeName = None
    aPreemptible = None
    aProjectName = None
    aRenderLayers = None
    aCurrentRenderLayer = None
    aValidateAllLayers = None

    aHostSoftware = None
    aPluginSoftware = None
    aExtraAssets = None

    aAssetScraperName = None
    aAssetScraperActive = None
    aAssetScrapers = None

    aExtraEnvironment = None
    aExtraEnvironmentKey = None
    aExtraEnvironmentValue = None
    aExtraEnvironmentPolicy = None

    aMetadata = None
    aMetadataKey = None
    aMetadataValue = None

    aUseUploadDaemon = None

    aEmailAddresses = None
    aEmailAddress = None
    aEmailAddressActive = None

    aRetriesWhenPreempted = None

    aTaskLimit = None
    aDoScrape = None

    aFrameCount = None
    aTaskCount = None
    aScoutTaskCount = None
    aScoutFrameCount = None
    aResolvedChunkSize = None

    aAssetCount = None
    aAssetsSize = None
    aFrameSpec = None
    aScoutSpec = None
    aCurrentRenderer = None
    aCurrentTime = None

    aDestinationDirectory = None
    aLocationTag = None

    aAutosave = None
    aAutosaveTemplate = None
    aCleanupAutosave = None

    aShowTracebacks = None
    aFixturesDirectory = None
    aUseFixtures = None

    aOutput = None

    id = om.MTypeId(0x880500)

    @staticmethod
    def creator():
        return conductorRender()

    @classmethod
    def initialize(cls):
        cls.make_title_att()
        cls.make_frames_atts()
        cls.make_instance_type_att()
        cls.make_project_name_att()
        cls.make_layer_atts()
        cls.make_software_att()
        cls.make_assets_atts()
        cls.make_environment_atts()
        cls.make_task_atts()
        cls.make_upload_flag_atts()
        cls.make_notification_atts()
        cls.make_metadata_atts()
        cls.make_retries_atts()

        cls.make_hidden_atts()
        cls.make_info_atts()

        cls.make_autosave_atts()
        cls.make_developer_atts()
        cls.make_misc_atts()

        cls.make_output_att()

        cls.setup_attribute_affects()

    @staticmethod
    def _make_output_int_att(longname, shortname):
        nAttr = om.MFnNumericAttribute()
        att = nAttr.create(longname, shortname, om.MFnNumericData.kInt)
        nAttr.storable = False
        nAttr.writable = False
        nAttr.readable = True
        om.MPxNode.addAttribute(att)
        return att

    @classmethod
    def make_info_atts(cls):
        cls.aFrameCount = cls._make_output_int_att("frameCount", "frc")
        cls.aTaskCount = cls._make_output_int_att("taskCount", "tsc")
        cls.aScoutTaskCount = cls._make_output_int_att("scoutTaskCount", "stc")
        cls.aScoutFrameCount = cls._make_output_int_att("scoutFrameCount", "sfc")
        cls.aResolvedChunkSize = cls._make_output_int_att("resolvedChunkSize", "rcs")

        cls.aAssetCount = cls._make_output_int_att("assetCount", "asc")
        cls.aAssetsSize = cls._make_output_int_att("assetsSize", "asz")

        tAttr = om.MFnTypedAttribute()
        cls.aFrameSpec = tAttr.create("frameSpec", "fms", om.MFnData.kString)
        tAttr.storable = False
        tAttr.writable = False
        tAttr.readable = True
        om.MPxNode.addAttribute(cls.aFrameSpec)

        cls.aScoutSpec = tAttr.create("scoutSpec", "scs", om.MFnData.kString)
        tAttr.storable = False
        tAttr.writable = False
        tAttr.readable = True
        om.MPxNode.addAttribute(cls.aScoutSpec)

    @classmethod
    def make_title_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aTitle = tAttr.create("title", "ttl", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aTitle)

    @classmethod
    def make_instance_type_att(cls):
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        cls.aInstanceTypeName = tAttr.create(
            "instanceTypeName", "itn", om.MFnData.kString
        )
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aInstanceTypeName)

        cls.aPreemptible = nAttr.create(
            "preemptible", "prm", om.MFnNumericData.kBoolean, True
        )
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True
        om.MPxNode.addAttribute(cls.aPreemptible)

    @classmethod
    def make_project_name_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aProjectName = tAttr.create("projectName", "prn", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aProjectName)

    @classmethod
    def make_layer_atts(cls):
        eAttr = om.MFnEnumAttribute()
        nAttr = om.MFnNumericAttribute()
        tAttr = om.MFnTypedAttribute()

        cls.aRenderLayers = eAttr.create("renderLayers", "rl", k.CURRENT_LAYER)
        eAttr.addField("Current layer only", k.CURRENT_LAYER)
        eAttr.addField("Renderable layers in one job", k.LAYERS_ONE_JOB)
        eAttr.addField("One job per render layer", k.JOB_PER_LAYER)
        eAttr.hidden = False
        eAttr.keyable = True
        eAttr.storable = True
        om.MPxNode.addAttribute(cls.aRenderLayers)

        cls.aCurrentRenderLayer = nAttr.create(
            "currentRenderLayer", "crl", om.MFnNumericData.kInt
        )
        nAttr.hidden = False
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = False
        om.MPxNode.addAttribute(cls.aCurrentRenderLayer)

        cls.aCurrentRenderer = tAttr.create(
            "currentRenderer", "cren", om.MFnData.kString
        )
        tAttr.hidden = True
        tAttr.storable = True
        tAttr.readable = True
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aCurrentRenderer)
        
        cls.aValidateAllLayers = nAttr.create("validateAllLayers", "val", om.MFnNumericData.kBoolean, False)
        nAttr.hidden = False
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aValidateAllLayers)
        

    @classmethod
    def make_software_att(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aHostSoftware = tAttr.create("hostSoftware", "hsw", om.MFnData.kString)
        tAttr.hidden = False
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aHostSoftware)

        cls.aPluginSoftware = tAttr.create("pluginSoftware", "psw", om.MFnData.kString)
        tAttr.array = True
        tAttr.hidden = False
        tAttr.writable = True
        om.MPxNode.addAttribute(cls.aPluginSoftware)

    @classmethod
    def make_assets_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aAssetScraperName = tAttr.create(
            "assetScraperName", "asn", om.MFnData.kString
        )

        cls.aAssetScraperActive = nAttr.create(
            "assetScraperActive", "asa", om.MFnNumericData.kBoolean, True
        )

        cls.aAssetScrapers = cAttr.create("assetScrapers", "ascs")
        cAttr.array = True
        cAttr.hidden = False
        cAttr.writable = True
        cAttr.addChild(cls.aAssetScraperName)
        cAttr.addChild(cls.aAssetScraperActive)
        om.MPxNode.addAttribute(cls.aAssetScrapers)

        conductorRender.aExtraAssets = tAttr.create(
            "extraAssets", "eass", om.MFnData.kString
        )
        tAttr.array = True
        tAttr.hidden = False
        tAttr.writable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(conductorRender.aExtraAssets)

    @classmethod
    def make_environment_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        eAttr = om.MFnEnumAttribute()
        
        cls.aExtraEnvironmentKey = tAttr.create(
            "extraEnvironmentKey", "eek", om.MFnData.kString
        )
        cls.aExtraEnvironmentValue = tAttr.create(
            "extraEnvironmentValue", "eev", om.MFnData.kString
        )
        
        cls.aExtraEnvironmentPolicy = eAttr.create("extraEnvironmentPolicy", "eep", k.POLICY_APPEND)
        eAttr.addField("Exclusive", k.POLICY_EXCLUSIVE)
        eAttr.addField("Prepend", k.POLICY_PREPEND)
        eAttr.addField("Append", k.POLICY_APPEND)
        eAttr.hidden = False
        eAttr.keyable = True
        eAttr.storable = True

        cls.aExtraEnvironment = cAttr.create("extraEnvironment", "een")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aExtraEnvironmentKey)
        cAttr.addChild(cls.aExtraEnvironmentValue)
        cAttr.addChild(cls.aExtraEnvironmentPolicy)
        om.MPxNode.addAttribute(cls.aExtraEnvironment)

    @classmethod
    def make_metadata_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        cls.aMetadataKey = tAttr.create("metadataKey", "mdk", om.MFnData.kString)
        cls.aMetadataValue = tAttr.create("metadataValue", "mdv", om.MFnData.kString)

        cls.aMetadata = cAttr.create("metadata", "md")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aMetadataKey)
        cAttr.addChild(cls.aMetadataValue)
        om.MPxNode.addAttribute(cls.aMetadata)

    @classmethod
    def make_retries_atts(cls):
        nAttr = om.MFnNumericAttribute()

        cls.aRetriesWhenPreempted = nAttr.create(
            "retriesWhenPreempted", "rwp", om.MFnNumericData.kInt, 1
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aRetriesWhenPreempted)

    @classmethod
    def make_upload_flag_atts(cls):
        nAttr = om.MFnNumericAttribute()

        cls.aUseUploadDaemon = nAttr.create(
            "useUploadDaemon", "uud", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseUploadDaemon)

    @classmethod
    def make_frames_atts(cls):
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()
        uAttr = om.MFnUnitAttribute()

        cls.aStartFrame = uAttr.create(
            "startFrame", "stf", om.MFnUnitAttribute.kTime, 1
        )
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aStartFrame)

        cls.aEndFrame = uAttr.create("endFrame", "enf", om.MFnUnitAttribute.kTime, 10)
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aEndFrame)

        cls.aByFrame = nAttr.create("byFrame", "byf", om.MFnNumericData.kInt, 1)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aByFrame)

        cls.aAnimation = nAttr.create("animation", "ani", om.MFnNumericData.kBoolean)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aAnimation)

        cls.aChunkSize = nAttr.create("chunkSize", "csz", om.MFnNumericData.kInt, 1)
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        nAttr.setMin(1)
        om.MPxNode.addAttribute(cls.aChunkSize)

        cls.aUseCustomRange = nAttr.create(
            "useCustomRange", "ucr", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseCustomRange)

        cls.aCustomRange = tAttr.create("customRange", "crn", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aCustomRange)

        cls.aUseScoutFrames = nAttr.create(
            "useScoutFrames", "usf", om.MFnNumericData.kBoolean, True
        )
        nAttr.writable = True
        nAttr.keyable = False
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aUseScoutFrames)

        cls.aScoutFrames = tAttr.create("scoutFrames", "scf", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aScoutFrames)

        cls.aCurrentFrame = uAttr.create(
            "currentFrame", "cf", om.MFnUnitAttribute.kTime
        )
        uAttr.writable = True
        uAttr.keyable = False
        uAttr.storable = True
        om.MPxNode.addAttribute(cls.aCurrentFrame)

    @classmethod
    def make_task_atts(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aTaskTemplate = tAttr.create("taskTemplate", "ttm", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aTaskTemplate)

    @classmethod
    def make_notification_atts(cls):
        cAttr = om.MFnCompoundAttribute()
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aEmailAddress = tAttr.create("emailAddress", "eml", om.MFnData.kString)

        cls.aEmailAddressActive = nAttr.create(
            "emailAddressActive", "emla", om.MFnNumericData.kBoolean, True
        )

        cls.aEmailAddresses = cAttr.create("emailAddresses", "emls")

        cAttr.hidden = False
        cAttr.writable = True
        cAttr.array = True
        cAttr.addChild(cls.aEmailAddress)
        cAttr.addChild(cls.aEmailAddressActive)
        om.MPxNode.addAttribute(cls.aEmailAddresses)

    @classmethod
    def make_misc_atts(cls):
        tAttr = om.MFnTypedAttribute()
        cls.aDestinationDirectory = tAttr.create(
            "destinationDirectory", "ddr", om.MFnData.kString
        )
        tAttr.writable = True
        tAttr.storable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(cls.aDestinationDirectory)

        cls.aLocationTag = tAttr.create("locationTag", "lct", om.MFnData.kString)
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aLocationTag)

    @classmethod
    def make_developer_atts(cls):
        nAttr = om.MFnNumericAttribute()
        tAttr = om.MFnTypedAttribute()

        cls.aShowTracebacks = nAttr.create(
            "showTracebacks", "trc", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aShowTracebacks)

        cls.aUseFixtures = nAttr.create(
            "useFixtures", "ufx", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.storable = True
        # nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aUseFixtures)

        cls.aFixturesDirectory = tAttr.create(
            "fixturesDirectory", "fdr", om.MFnData.kString
        )
        tAttr.writable = True
        tAttr.storable = True
        tAttr.usedAsFilename = True
        om.MPxNode.addAttribute(cls.aFixturesDirectory)

    @classmethod
    def make_autosave_atts(cls):
        tAttr = om.MFnTypedAttribute()
        nAttr = om.MFnNumericAttribute()

        cls.aAutosaveTemplate = tAttr.create(
            "autosaveTemplate", "ast", om.MFnData.kString
        )
        tAttr.writable = True
        tAttr.storable = True
        om.MPxNode.addAttribute(cls.aAutosaveTemplate)

        cls.aAutosave = nAttr.create(
            "autosave", "aus", om.MFnNumericData.kBoolean, True
        )
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aAutosave)

        cls.aCleanupAutosave = nAttr.create(
            "cleanupAutosave", "cua", om.MFnNumericData.kBoolean, True
        )
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.storable = True
        om.MPxNode.addAttribute(cls.aCleanupAutosave)

    @classmethod
    def make_hidden_atts(cls):
        nAttr = om.MFnNumericAttribute()
        cls.aDoScrape = nAttr.create(
            "doScrape", "dsc", om.MFnNumericData.kBoolean, False
        )
        nAttr.writable = True
        nAttr.storable = False
        nAttr.hidden = True
        nAttr.default = False
        om.MPxNode.addAttribute(cls.aDoScrape)

        cls.aTaskLimit = nAttr.create("taskLimit", "tsl", om.MFnNumericData.kInt, 10)
        nAttr.writable = True
        nAttr.storable = True
        nAttr.hidden = True
        om.MPxNode.addAttribute(cls.aTaskLimit)

    @classmethod
    def make_output_att(cls):
        """
        Output atttribute.
        """
        tAttr = om.MFnTypedAttribute()
        cls.aOutput = tAttr.create("output", "out", om.MFnData.kString)
        tAttr.readable = True
        tAttr.storable = False
        tAttr.writable = False
        tAttr.keyable = False

        om.MPxNode.addAttribute(cls.aOutput)

    @classmethod
    def setup_attribute_affects(cls):
        om.MPxNode.attributeAffects(cls.aTitle, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aInstanceTypeName, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aPreemptible, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aProjectName, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aHostSoftware, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aPluginSoftware, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aExtraEnvironment, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aTaskTemplate, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aTaskLimit, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aDoScrape, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aExtraAssets, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aAssetScrapers, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aMetadata, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aRetriesWhenPreempted, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aUseUploadDaemon, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aEmailAddresses, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aDestinationDirectory, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aLocationTag, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentRenderLayer, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentRenderer, cls.aOutput)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aOutput)

        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aFrameCount)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aFrameCount)

        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aTaskCount)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aTaskCount)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aScoutTaskCount)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutTaskCount)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aScoutFrameCount)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutFrameCount)

        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aFrameSpec)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aFrameSpec)

        om.MPxNode.attributeAffects(cls.aUseScoutFrames, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aScoutFrames, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aScoutSpec)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aScoutSpec)
        
 
        om.MPxNode.attributeAffects(cls.aChunkSize, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aUseCustomRange, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aCustomRange, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aStartFrame, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aEndFrame, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aByFrame, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aAnimation, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aRenderLayers, cls.aResolvedChunkSize)
        om.MPxNode.attributeAffects(cls.aCurrentFrame, cls.aResolvedChunkSize)


    def compute(self, plug, data):
        """Compute output json from input attribs."""
        if not (
            (plug == self.aOutput)
            or (plug == self.aFrameCount)
            or (plug == self.aTaskCount)
            or (plug == self.aScoutTaskCount)
            or (plug == self.aScoutFrameCount)
            or (plug == self.aResolvedChunkSize)
            or (plug == self.aFrameSpec)
            or (plug == self.aScoutSpec)
        ):
            return None

        try:
            sequence = self.get_sequence(data)
        except (ValueError, TypeError):
            om.MGlobal.displayWarning("Invalid frame sequence specified.")
            return None

        resolved_chunk_size = sequence.chunk_size

        node_name = om.MFnDependencyNode(self.thisMObject()).name()

        scout_sequence = self.get_scout_sequence(data, sequence)
        frame_count = len(sequence)
        task_count = sequence.chunk_count()

        scout_task_count = 0
        scout_frame_count = 0
        scout_tasks_sequence = None
        if scout_sequence:
            scout_chunks = sequence.intersecting_chunks(scout_sequence)
            if scout_chunks:
                scout_tasks_sequence = Sequence.create(
                    ",".join(str(chunk) for chunk in scout_chunks)
                )
                scout_task_count = len(scout_chunks)
                scout_frame_count = len(scout_tasks_sequence)

        self.set_frame_info_plugs(
            data, frame_count, task_count, scout_frame_count, scout_task_count, resolved_chunk_size
        )

        self.set_frame_and_scout_spec(data, sequence, scout_tasks_sequence)

        if plug != self.aOutput:
            return self

        job_context = context.job_context(pm.PyNode(node_name))
        job_expander = Expander(**job_context)

        destination_context = context.destination_context(pm.PyNode(node_name))
        destination_expander = Expander(**destination_context)

        handle = data.outputValue(self.aOutput)

        amendments = self.get_amendments(data, node_name)
        path_amendments = [p["path"] for p in amendments["paths"]]
        env_amendments = amendments["env"]

        result = {}
        result.update(self.get_title(data, job_expander))
        result.update(self.get_project(data))
        result.update(self.get_instance_type(data))
        result.update(self.get_destination_directory(data, destination_expander))
        result.update(self.get_scout_frames(scout_sequence))
        result.update(self.get_software_environment(data, env_amendments))
        result.update(self.get_notifications(data))
        result.update(self.get_location_tag(data))
        result.update(self.get_upload_flags(data))
        result.update(self.get_retry_policy(data))
        result.update(self.get_metadata(data, job_expander))
        
        result.update(self.get_tasks(data, sequence, job_context))
        result.update(self.get_upload_paths(data, path_amendments))

        handle.setString(json.dumps(result))

        data.setClean(plug)
        return self

    @classmethod
    def get_sequence(cls, data):
        chunk_size = data.inputValue(cls.aChunkSize).asInt()
        use_custom_range = data.inputValue(cls.aUseCustomRange).asBool()
        if not data.inputValue(cls.aAnimation).asBool():
            return Sequence.create(
                int(
                    data.inputValue(cls.aCurrentFrame)
                    .asTime()
                    .asUnits(om.MTime.uiUnit())
                )
            )

        if use_custom_range:
            custom_range = data.inputValue(cls.aCustomRange).asString()
            sequence = Sequence.create(
                custom_range, chunk_size=chunk_size, chunk_strategy="progressions"
            )
        else:
            start_frame = (
                data.inputValue(cls.aStartFrame).asTime().asUnits(om.MTime.uiUnit())
            )
            end_frame = data.inputValue(cls.aEndFrame).asTime().asUnits(om.MTime.uiUnit())
            by_frame = data.inputValue(cls.aByFrame).asInt()
            sequence =  Sequence.create(
                int(start_frame),
                int(end_frame),
                by_frame,
                chunk_size=chunk_size,
                chunk_strategy="progressions",
            )
        
        sequence.cap_chunk_count(k.MAX_TASKS)
        return sequence


    @classmethod
    def get_scout_sequence(cls, data, main_sequence):
        use_scout_frames = data.inputValue(cls.aUseScoutFrames).asBool()
        if not use_scout_frames:
            return

        scout_frames = data.inputValue(cls.aScoutFrames).asString().strip()

        match = re.compile(r"^auto[, :]+(\d+)$").match(scout_frames)
        if match:
            samples = int(match.group(1))
            return main_sequence.subsample(samples)

        try:
            return Sequence.create(scout_frames)
        except (ValueError, TypeError):
            return

    @classmethod
    def get_scout_frames(cls, scout_sequence):
        return {"scout_frames": ",".join([str(s) for s in scout_sequence or []])}

    @classmethod
    def set_frame_info_plugs(
        cls, data, frame_count, task_count, scout_frame_count, scout_task_count, resolved_chunk_size
    ):
        handle = data.outputValue(cls.aFrameCount)
        handle.setInt(frame_count)
        handle.setClean()
        handle = data.outputValue(cls.aTaskCount)
        handle.setInt(task_count)
        handle.setClean()
        handle = data.outputValue(cls.aScoutFrameCount)
        handle.setInt(scout_frame_count)
        handle.setClean()
        handle = data.outputValue(cls.aScoutTaskCount)
        handle.setInt(scout_task_count)
        handle.setClean()
        handle = data.outputValue(cls.aResolvedChunkSize)
        handle.setInt(resolved_chunk_size)
        handle.setClean()

    @classmethod
    def set_frame_and_scout_spec(cls, data, sequence, scout_sequence):
        handleFrameSpec = data.outputValue(cls.aFrameSpec)
        handleScoutSpec = data.outputValue(cls.aScoutSpec)
        if scout_sequence:
            handleScoutSpec.setString(str(scout_sequence))
        else:
            handleScoutSpec.setString("")
        handleFrameSpec.setString(str(sequence))

        handleScoutSpec.setClean()
        handleFrameSpec.setClean()

    @classmethod
    def get_instance_type(cls, data):
        return {
            "instance_type": data.inputValue(cls.aInstanceTypeName).asString(),
            "preemptible": data.inputValue(cls.aPreemptible).asBool(),
        }

    @classmethod
    def get_title(cls, data, expander):
        title = data.inputValue(cls.aTitle).asString()
        return {"job_title": expander.evaluate(title)}

    @classmethod
    def get_project(cls, data):
        return {"project": data.inputValue(cls.aProjectName).asString()}

    @classmethod
    def get_software_environment(cls, data, env_amendments):
        """Build software environment.

        Env components are:
        1. Env derived from package data: Software location etc.
        2. Env amendments added by scrapers: OCIO or maybe others.
        3. Extra env added by user: Something missing that we didn't account for.
        """

        extra_env = cls.get_extra_env(data)
        account_level_env = coredata.data().get("extra_environment", [])
        packages_data = cls.get_software_packages(data)
        packages_data["env"].extend(env_amendments)
        packages_data["env"].extend(account_level_env)
        packages_data["env"].extend(extra_env)
        return {
            "environment": dict(packages_data["env"]),
            "software_package_ids": packages_data["ids"],
        }

    @classmethod
    def get_software_packages(cls, data):
        """Get package IDs and env based on selected software.

        When making queries to the package tree, we must qualify host and plugin paths with the
        platform. The platform was previously stripped away because it was not needed in a single
        platform environment. We don't want to have the word linux next to every entry in the
        dropdown.

        * "maya 1.0.0" must be "maya 1.0.0 linux"
        * "maya 1.0.0 linux/arnold 5.0.0" must be "maya 1.0.0 linux/arnold 5.0.0 linux"
        """
        tree_data = coredata.data().get("software")
        platform = list(coredata.platforms())[0]
        paths = []
        host_path = "{} {}".format(
            data.inputValue(cls.aHostSoftware).asString(), platform
        )
        paths.append(host_path)
        array_handle = data.inputArrayValue(cls.aPluginSoftware)

        while not array_handle.isDone():
            plugin_path = "{}/{} {}".format(
                host_path, array_handle.inputValue().asString(), platform
            )
            paths.append(plugin_path)
            array_handle.next()

        result = {"ids": [], "env": PackageEnvironment()}

        for package in filter(
            None, [tree_data.find_by_path(path) for path in paths if path]
        ):
            if package:
                result["ids"].append(package["package_id"])
                result["env"].extend(package)
        result["ids"] = list(set(result["ids"]))
        return result

    @classmethod
    def get_extra_env(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aExtraEnvironment)
        while not array_handle.isDone():
            name = array_handle.inputValue().child(cls.aExtraEnvironmentKey).asString()
            value = (
                array_handle.inputValue().child(cls.aExtraEnvironmentValue).asString()
            )
            policy = array_handle.inputValue().child(cls.aExtraEnvironmentPolicy).asInt()

            name = name.strip()
            value = value.strip()

            if name and value:
                result.append(
                    {
                        "name": name,
                        "value": value,
                        "merge_policy":  k.ENV_POLICIES[policy],
                    }
                )
            array_handle.next()
        return result

    @classmethod
    def get_renderable_camera(cls):
        """Get a comma-separated list of renderable cameras."""
        return ",".join(
            [c.name() for c in pm.ls(type="camera") if c.attr("renderable").get()]
        )

    @classmethod
    def get_tasks(cls, data, sequence, job_context):
        tasks = []
        template = data.inputValue(cls.aTaskTemplate).asString()
        limit = data.inputValue(cls.aTaskLimit).asInt()
        chunks = sequence.chunks()
        if limit < 0:
            limit = len(chunks)
        for i, chunk in enumerate(chunks):
            if i >= limit:
                break
            task_context = context.task_context(chunk, job_context)
            expander = Expander(**task_context)
            tasks.append({"command": expander.evaluate(template), "frames": str(chunk)})
        return {"tasks_data": tasks}

    @classmethod
    def get_upload_flags(cls, data):
        return {
            "local_upload": not data.inputValue(cls.aUseUploadDaemon).asBool(),
        }

    @classmethod
    def get_retry_policy(cls, data):
        return {
            "autoretry_policy": {
                "preempted": {
                    "max_retries": data.inputValue(cls.aRetriesWhenPreempted).asInt()
                }
            }
        }

    @classmethod
    def get_notifications(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aEmailAddresses)
        while not array_handle.isDone():
            if array_handle.inputValue().child(cls.aEmailAddressActive).asBool():
                value = (
                    array_handle.inputValue()
                    .child(cls.aEmailAddress)
                    .asString()
                    .strip()
                )
                if value:
                    result.append(value)
            array_handle.next()
        return {"notify": result}

    def get_upload_paths(self, data, path_amendments):
        path_list = PathList()
        path_list.add(*path_amendments)
        path_list.add(*self.get_extra_asset_paths(data))
        path_list.real_files()
        return {"upload_paths": sorted([p.fslash() for p in path_list])}

    @classmethod
    def get_amendments(cls, data, node):
        result = {"paths": [], "env": []}
        if not data.inputValue(cls.aDoScrape).asBool():
            return result
        array_handle = data.inputArrayValue(cls.aAssetScrapers)
        scraper_scripts = []
        while not array_handle.isDone():
            if array_handle.inputValue().child(cls.aAssetScraperActive).asBool():
                script = (
                    array_handle.inputValue().child(cls.aAssetScraperName).asString()
                )
                if script:
                    scraper_scripts.append(script)
            array_handle.next()

        return scraper_utils.run_scrapers(node, scraper_scripts)

    @classmethod
    def get_extra_asset_paths(cls, data):
        result = []
        array_handle = data.inputArrayValue(cls.aExtraAssets)
        while not array_handle.isDone():
            path = array_handle.inputValue().asString().strip()
            if path:
                result.append(path)
            array_handle.next()
        return result

    @classmethod
    def get_metadata(cls, data, expander):
        metadata = {}
        array_handle = data.inputArrayValue(cls.aMetadata)
        while not array_handle.isDone():
            key = array_handle.inputValue().child(cls.aMetadataKey).asString().strip()
            value = (
                array_handle.inputValue().child(cls.aMetadataValue).asString().strip()
            )

            metadata[key] = value

            array_handle.next()

        return {"metadata": expander.evaluate(metadata)}

    @classmethod
    def get_location_tag(cls, data):
        result = data.inputValue(cls.aLocationTag).asString().strip()
        return {"location": result} if result else {}

    @classmethod
    def get_destination_directory(cls, data, expander):
        """
        Return output_path sub object.

        It should be impossible forthis path to have backslashes at this point, however, just in
        case we re-enforce forward slashes.
        """
        output_path = data.inputValue(cls.aDestinationDirectory).asString().strip()
        output_path = Path(expander.evaluate(output_path)).fslash()
        if not output_path:
            pm.displayError(
                "The Destination directory is invalid. Find it at the top of the submitter UI."
            )
        return {"output_path": output_path}
