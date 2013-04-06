#!/usr/local/bin/python
"""
macspeechX.py ; Python Interface to Speech Syntheis Mangaer on Macintosh OSX.
requires; ctypes module(0.9.6 or later) and latest python interpreter.
Python interpreter pre-installed on OS may not work with latest ctypes module.

macspeechX tryed to simulate old macspeech module bundled with python(in
Pre-MacOSX era). The document for macspeech module should work on macspeechX module.

(c) Noboru Yamamoto(KEK,JAPAN),2005
"""
import ctypes
from ctypes import cdll,byref
#load speachSynthesis dll
__SS_Available=None

try:
    __ssdll=cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/Frameworks/SpeechSynthesis.framework/Versions/Current/SpeechSynthesis")
    __SS_Available=1
except:
    raise "Speech Systheis is not available on this machine"

#
def C2PStr(aStr):
    return "%c%s"%(len(aStr),aStr)

def P2CStr(aStr):
    if aStr:
        return aStr[1:ord(aStr[0])+1]

#constants
_kNoEndingProsody = 1
_kNoSpeechInterrupt = 2
_kPreflightThenPause = 4

_kNeuter=0
_kMale=1
_kFemale=2

_kImmediate=0
_kEndOfWord=1
_kEndOfSentence=2

#_soVoiceDescription            = (ord('i')<<24)+(ord('n')<<16)+(ord('f')<<8)+(ord('o')<<0)
_soVoiceDescription = ctypes.c_ulong(0x696e666f)
#_soVoiceFile                   = (ord('f')<<24)+(ord('r')<<16)+(ord('e')<<8)+ord('f')
_soVoiceFile = ctypes.c_ulong(0x66726566)
# classes

class NumVersion(ctypes.Structure):
    _fields_=[("nonRelRev",ctypes.c_ubyte),
              ("stage",ctypes.c_byte),
              ("minorAndBugRev",ctypes.c_ubyte),
              ("majorRev",ctypes.c_ubyte)]
    
class SpeechChannelRecord(ctypes.Structure):
    _fields_=[("data",ctypes.c_long*1)]

class VoiceSpec(ctypes.Structure):
    _fields_=[ ("creator",ctypes.c_ulong),
               ("id",ctypes.c_ulong),    
               ]
        
class VoiceDescription(ctypes.Structure):
    _fields_=[ ("length",ctypes.c_long),
               ("voice",VoiceSpec),    
               ("version",ctypes.c_long),
               ("name",ctypes.c_char*64),
               ("comment",ctypes.c_char*256),
               ("gender",ctypes.c_short),
               ("age",ctypes.c_short),
               ("script",ctypes.c_short),
               ("language",ctypes.c_short),
               ("region",ctypes.c_short),        
               ("reserved",ctypes.c_long*4), 
               ]
    def __init__(self):
        ctypes.Structure.__init__(self)
        self.length=ctypes.c_long(ctypes.sizeof(VoiceDescription))

class SpeechStatusInfo(ctypes.Structure):
    _fields_=[("outputBusy",ctypes.c_ubyte),
              ("outputPaused",ctypes.c_ubyte),
              ("inputBytesLeft",ctypes.c_long),
              ("phonemeCode",ctypes.c_short)
              ]

class SpeechErrorInfo(ctypes.Structure):
    _fields_=[("count",ctypes.c_short),
              ("oldest",ctypes.c_short),
              ("oldPos",ctypes.c_long),
              ("newest",ctypes.c_short),
              ("newPos",ctypes.c_long)
              ]

class SpeechVersionInfo(ctypes.Structure):
    _fields_=[("synthType",ctypes.c_ulong),
              ("synthSubType",ctypes.c_ulong),
              ("synthManufacturer",ctypes.c_ulong),
              ("synthFlags",ctypes.c_long),
              ("synthVersion",NumVersion),
              ]
class PhonemeInfo(ctypes.Structure):
    _fields_=[("opcode",ctypes.c_short),
              ("phStr",ctypes.ARRAY(ctypes.c_char,16)),
              ("exampleStr",ctypes.ARRAY(ctypes.c_char,32)),
              ("hiliteStart",ctypes.c_short),
              ("hiliteEnd",ctypes.c_short),
              ]

class PhonemeDescriptor(ctypes.Structure):
    _fields_=[("phonemeCount",ctypes.c_short),
              ("thePhonemes",ctypes.ARRAY(PhonemeInfo,1)),
              ]

__fixed1=float(0x0010000L)
# from FixMath.h
def FixedToFloat(f):
    return (float(f)/__fixed1)

def FloatToFixed(f):
    return int(float(f)*__fixed1)


# classes for macspeech
__ssdll.GetVoiceDescription.argtypes=[ctypes.POINTER(VoiceSpec), ctypes.POINTER(VoiceDescription) ]
__ssdll.GetVoiceInfo.argtypes=[ctypes.POINTER(VoiceSpec), ctypes.c_ulong, ctypes.POINTER(VoiceDescription) ]

class SpeechChannel:
    __ssdll=globals()["__ssdll"]
    __ssdll.NewSpeechChannel.argtypes=[ctypes.POINTER(VoiceSpec), 
                                       ctypes.POINTER(ctypes.POINTER(SpeechChannelRecord))]

    __ssdll.TextToPhonemes.argtypes=[ctypes.POINTER(SpeechChannelRecord),
                                     ctypes.c_char_p,
                                     ctypes.c_ulong,
                                     ctypes.c_void_p,
                                     ctypes.POINTER(ctypes.c_ulong)]
    
    def __init__(self,v=None):
        if not v:
            v=Voice()
        self.channel=ctypes.pointer(SpeechChannelRecord())
        status=SpeechChannel.__ssdll.NewSpeechChannel(byref(v.voice),byref(self.channel))
        self.voice=v
        
    def __del__(self):
        SpeechChannel.__ssdll.DisposeSpeechChannel(self.channel)
	
    def SpeakText(self,s):
        status=SpeechChannel.__ssdll.SpeakText(self.channel, ctypes.c_char_p(s), len(s))
        return status

    def SpeakBuffer(self,  s, l, c=0):
        status=SpeechChannel.__ssdll.SpeakText(self.channel, s, ctypes.c_ulong(l), ctypes.c_long(c))
        return status

    def Stop(self):
        status=SpeechChannel.__ssdll.StopSpeech(self.channel)
        return status

    def StopAt(self,where=_kImmediate):
        status=SpeechChannel.__ssdll.StopSpeechAt(self.channel,where)
        return status

    def Pause(self,where=_kImmediate):
        status=SpeechChannel.__ssdll.PauseSpeechAt(self.channel,where)
        return status

    def Continue(self):
        status=SpeechChannel.__ssdll.ContinueSpeech(self.channel)
        return status
                    
    def GetPitch(self):
        """
        parameter. Typical voice frequencies range
        from around 90 hertz for a low-pitched male voice to perhaps 300 hertz for a high-pitched child!Gs
        voice. These frequencies correspond to approximate pitch values in the ranges of 30.000 to 40.000 and
        55.000 to 65.000, respectively. Although fixed-point values allow you to specify a wide range of pitches,
        not all synthesizers will support the full range of pitches. If your application specifies a pitch that a
        synthesizer cannot handle, it may adjust the pitch to fit within an acceptable range.
        noboru's comment:1unit is about half note step. 
        """
        pitch=ctypes.c_long(0)
        status=SpeechChannel.__ssdll.GetSpeechPitch(self.channel, byref(pitch))
        self.pitch=FixedToFloat(pitch.value)
        return self.pitch

    def SetPitch(self, pitch):
        fpitch=FloatToFixed(pitch)
        status=SpeechChannel.__ssdll.SetSpeechPitch(self.channel,ctypes.c_long(fpitch))
        self.pitch=pitch
        return pitch

    def GetRate(self):
        rate=ctypes.c_long(0)
        status=SpeechChannel.__ssdll.GetSpeechRate(self.channel,byref(rate))
        self.rate=FixedToFloat(rate.value)
        return self.rate

    def SetRate(self,rate):
        frate=FloatToFixed(rate)
        status=SpeechChannel.__ssdll.SetSpeechRate(self.channel,ctypes.c_long(frate))
        self.rate=rate
        return self.rate

    def TextToPhonemes(self,s):
        b=ctypes.create_string_buffer(len(s)*255)
        ptr=ctypes.cast(ctypes.pointer(b),ctypes.c_void_p)
        l=ctypes.c_ulong(0)
        status=SpeechChannel.__ssdll.TextToPhonemes(self.channel,
                                                    ctypes.c_char_p(s),
                                                    ctypes.c_ulong(len(s)),
                                                    ptr,
                                                    byref(l))
        return (b,l)
    
class Voice:
    __ssdll=globals()["__ssdll"]

    __ssdll.GetVoiceDescription.argtypes=[ctypes.POINTER(VoiceSpec),
                                          ctypes.POINTER(VoiceDescription),
                                          ctypes.c_long ]
    __ssdll.GetVoiceDescription.restype=ctypes.c_short

    __ssdll.GetVoiceInfo.argtypes=[ctypes.POINTER(VoiceSpec), ctypes.c_ulong, ctypes.c_voidp]
    __ssdll.GetVoiceInfo.restype=ctypes.c_short
    
    def __init__(self,ind=1):
        self.voice=VoiceSpec()
        Voice.__ssdll.GetIndVoice(ind, byref(self.voice))
        self.desc=None
	
    def GetDescription(self):
        if not self.desc:
            self.desc=VoiceDescription()  #create description object
        status=Voice.__ssdll.GetVoiceDescription(ctypes.pointer(self.voice),
                                                 ctypes.byref(self.desc),
                                                 ctypes.c_long(ctypes.sizeof(VoiceDescription)))
        if status:
            print "GetVoiceDescription RC:",status
            return None
        return (self.desc)
    
    def GetInfo(self,selector=_soVoiceDescription):
        if (selector != _soVoiceDescription):
            print "Sorry this option is not supported"
            return 
        self.desc=VoiceDescription()  #create description object
        status=Voice.__ssdll.GetVoiceInfo(ctypes.pointer(self.voice),
                                          _soVoiceDescription,
                                          ctypes.byref(self.desc))
        if status:
            print "GetInfo RC:",status
            self.desc=None
        return (self.desc)
        
        
    def GetGender(self):
        if not self.desc:
            self.GetDescription()
        if not self.desc.name:
            self.GetInfo()
        return self.desc.gender

    def NewChannel(self):
        return SpeechChannel(self)

#
def Available():
    return __SS_Available

def Version():
    vers=NumVersion()
    status=__ssdll.SpeechManagerVersion(byref(vers))
    return ((vers.nonRelRev<<24)+(vers.stage<<16)+(vers.minorAndBugRev<<8)+(vers.majorRev))
    
def SpeakString(s):
    return __ssdll.SpeakString(C2PStr(s))

SpeakText=SpeakString

def Busy():
    return __ssdll.SpeechBusy()

def BusySystemWide():
    return __ssdll.SpeechBusySystemWide()

__ssdll.CountVoices.argtypes=[ctypes.c_void_p]

def CountVoices():
    count=ctypes.c_short(0)
    status=__ssdll.CountVoices(byref(count))
    return count.value
    
def GetIndVoice(n=0):
    return Voice(n)
	
#test function.
def list_voice_name():
    n=CountVoices()
    gender={_kNeuter:"Neuter",_kMale:"Male",_kFemale:"Female"}
    for i in xrange(1,n+1):
        v=GetIndVoice(i)
        while Busy():
            pass
        d=v.GetDescription()
        ch=v.NewChannel()
        print "%d: %s, %d, %s"%(i, P2CStr(d.name), d.age, gender[d.gender])
        ch.SpeakText("my name is %s of age %d."%(P2CStr(d.name), d.age))
        while Busy():
            pass

def test():
    SpeakString("Hello!!\n Welcome to macspeech on MacOSX")
    # Embedded commands: See "SpeechSynthesisProgrammingGuide.pdf" page 38.
    while Busy(): pass
    SpeakString("[[char LTRL]] cat [[char NORM]],")
    while Busy(): pass
    SpeakString("[[cmnt This is a comment that will be ignored by the synthesizer.]]")
    while Busy(): pass
    SpeakString("[[ctxt WSKP]] GPS provides [[ctxt WORD]] coordinates.[[ctxt NORM]]")
    while Busy(): pass
    SpeakString("[[ctxt WSKP]] The post office [[ctxt WORD]]coordinates [[ctxt WSKP]] its deliveries. [[ctxt NORM]]")
    while Busy(): pass
    SpeakString("[[ctxt TSKP]] Your [[ctxt TEXT]] first step [[ctxtTSKP]] should be to relax. [[ctxt NORM]]")
    while Busy(): pass
    SpeakString("[[ctxt TSKP]] To relax should be your [[ctxt TEXT]]first step. [[ctxt NORM]]")
    while Busy(): pass
    SpeakString("Do [[emph +]] not [[emph -]] overtighten the screw.")
    while Busy(): pass
    SpeakString("Please call me at [[nmbr LTRL]] 5551990 [[nmbr NORM]].")
    while Busy(): pass
    SpeakString("In 1066 [[sync 0x000000A1]], William the Conqueror invaded England and by 1072 [[sync 0x000000A2]],the whole of England was conquered and united.")
    while Busy(): pass
    SpeakString("My name is [[inpt PHON]] AY1yIY2SAX [[inpt TEXT]].")

def test_tune():
    ch=SpeechChannel() #SpeakString just accept pascal string(less than 255 chars)
    ch.SpeakText("""[[inpt TUNE]]
    ~
    AA {D 120; P 176.9:0 171.4:22 161.7:61}
    r {D 60; P 166.7:0}
    ~
    y {D 210; P 161.0:0}
    UW {D 70; P 178.5:0}
    _
    S {D 290; P 173.3:0 178.2:8 184.9:19 222.9:81}
    1AX {D 280; P 234.5:0 246.1:39}
    r {D 170; P 264.2:0}
    ~
    y {D 200; P 276.9:0 274.9:17 271.0:50}
    UW {D 40; P 265.0:0 264.3:50}
    _
    b {D 140; P 263.6:0 263.5:13 263.3:60}
    r {D 110; P 263.1:0 260.4:43}
    1UX {D 30; P 256.8:0 256.8:6}
    S {D 190; P 256.1:0}
    t {D 20; P 252.0:0 253.6:47}
    ~
    y {D 30; P 255.5:0 257.8:45}
    AO {D 40; P 260.6:0 260.0:56}
    r {D 40; P 259.5:0}
    _
    t {D 190; P 251.3:0 250.0:16 245.9:68}
    1IY {D 260; P 243.4:0 248.1:8 286.1:72 288.5:84}
    T {D 220; P 291.6:0 262.8:27 220.0:67 184.8:100}
    ? {D 300}
    [[[inpt TEXT]]""")
    while Busy():pass # you must wait to finish reading it.

def test_hiragana():
    SpeakString("[[inpt PHON]]AA@ IY@ UW@ EH@ OW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]kAA@ kIY@ kUW@ kEH@ kOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]sAA@ sIY@ sUW@ sEH@ sOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]tAA@ tIY@ tUW@ tEH@ tOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]nAA@ nIY@ nUW@ nEH@ nOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]hAA@ hIY@ hUW@ hEH@ hOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]mAA@ mIY@ mUW@ mEH@ mOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]yAA@ yIY@ yUW@ yEH@ yOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]lAA@ lIY@ lUW@ lEH@ lOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]wAA@ wIY@ wUW@ wEH@ wOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]gAA@ gIY@ gUW@ gEH@ gOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]zAA@ zIY@ zUW@ zEH@ zOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]dAA@ dIY@ dUW@ dEH@ dOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]bAA@ bIY@ bUW@ bEH@ bOW [[inpt TEXT]]")
    while Busy(): pass

    SpeakString("[[inpt PHON]]SAA@ SIY@ SUW@ SEH@ SOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]PAA@ PIY@ PUW@ PEH@ POW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]TAA@ TIY@ TUW@ TEH@ TOW [[inpt TEXT]]")
    while Busy(): pass
    SpeakString("[[inpt PHON]]KOW NNN nIY tIY wAA[inpt TEXT]]")
    while Busy(): pass
