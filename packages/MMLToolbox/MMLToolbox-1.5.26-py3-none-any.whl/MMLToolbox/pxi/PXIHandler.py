import matplotlib.pyplot as plt
import numpy as np
import sys

from MMLToolbox.pxi.StoreSetup import StoreSetup 
from MMLToolbox.pxi.PXIControl import PXIControl
from MMLToolbox.util.types import *

class PXIHandler:
    def __init__(self, storeSetup:StoreSetup):
        self.ss = storeSetup
        self.handler = PXIControl()

        # PXI Parameter
        self.wavepoints = storeSetup.readInfoValue("wavepoints")
        self.sampleFrequency = storeSetup.readInfoValue("sampleFrequency")
        self.niOutput = storeSetup.readInfo("niOutput")
        self.niInput = storeSetup.readInfo("niInput")
        self.niDMM = storeSetup.readInfo("niDMM")

        self.__define_niOutput()
        self.__define_niInput()
        self.__define_niDMM()

    def __define_niOutput(self):
        for key,item in self.niOutput.items():
            item["rate"] = self.sampleFrequency
            self.niOutput[key] = item

    def __define_niInput(self):
        for key,item in self.niInput.items():
            item["rate"] = self.sampleFrequency
            item["wavepoints"] = self.wavepoints
            self.niInput[key] = item

    def __define_niDMM(self):
        for key,item in self.niDMM.items():
            item["sampleFreq"] = self.sampleFrequency
            item["wavepoints"] = self.wavepoints
            self.niDMM[key] = item

    def doMeasurement(self,signal,iteration):
        self.handler.connectHardware(dmmDict=self.niDMM,analogOutDict=self.niOutput,anlaogInDict=self.niInput,switchSlotName="PXI1Slot13")
        self.ss.writeOutputSignal(iteration,self.niOutput.keys(),[signal[0,:],signal[1,:]])

        self.handler.triggerDevices(signal)
        dmm_results = self.handler.getMeasResults()
        daq_results = self.handler.analogInResults
        self.handler.closeAnalogOutputTask()
        self.ss.writeData(iteration,self.niDMM.keys(),dmm_results)
        self.ss.writeData(iteration,self.niInput.keys(), daq_results)
        