from io import BytesIO, StringIO
import sys

class Var:
    def __init__(self, value=None, validator=lambda x: x, extractor=lambda x: x):
        self.value = value
        self.validator = validator
        self.extractor = extractor
    def __repr__(self):
        return f"{self.get()}"
    def __str__(self):
        return f"{self.get()}"
    def set(self, value):
        self.value = self.validator(value)
    def get(self):
        return self.extractor(self.value)
    def __call__(self, value):
        self.set(value)

class _echo_off:
    def __str__(self):
        return ""
    def __repr__(self):
        return ""

class _offset_and_rdbuf:
    def _offset(self, n, mode: int=0):
        # 0: set, 1: current, 2: end
        self.fobj.seek(n, mode)
        if isinstance(self, _instream):
            self.ignore()
    def rdbuf(self):
        res = self.fobj.read()
        if isinstance(self, _instream):
            self.ignore()
        return res

class _outstream(_echo_off):
    def __init__(self, fobj, sep):
        self.fobj = fobj
        self.sep = sep
    def __lshift__(self, other):
        if isinstance(other, _signal):
            if other == endl:
                self.fobj.write("\n" if isinstance(self.sep, str) else b"\n")
                self.fobj.flush()
            elif other == flush:
                self.fobj.flush()
            elif other.sig == "offset":
                self.fobj.seek(*other.arg)
        else:
            v = f"{other}{self.sep}" if isinstance(self.sep, str) else (other.get()+self.sep if isinstance(other, Var) else other + self.sep)
            self.fobj.write(v)
        return self

class _instream(_echo_off):
    def __init__(self, fobj, seps):
        self.fobj = fobj
        self.buf = fobj.read(0)
        self.seps = seps
        self.last = 1
    def _get(self, seps):
        while True:
            new = self.fobj.read(1)
            self.buf += new
            if len(new) == 0:
                break
            if any(sep in self.buf for sep in seps):
                break
        ind = min([self.buf.find(sep) for sep in seps if sep in self.buf] + [len(self.buf)])
        res = self.buf[:ind]
        self.buf = self.buf[ind+1:]
        self.last = res
        return res
    def __rshift__(self, oth):
        oth(self._get(self.seps))
        return self
    def __bool__(self):
        new = self.fobj.read(1)
        self.buf += new
        #print("buf, last and new:", repr(self.buf), repr(self.last), repr(new))
        #return bool(new or self.buf)
        return bool(new or self.last)
        #return bool(self.buf or new)
    def getline(self, sep: str|bytes=None):
        return self._get(sep or ("\n" if isinstance(self.fobj.read(0), str) else b"\n"))
    def ignore(self):
        self.buf = self.fobj.read(0)
    

class _signal:
    def __init__(self, sig, arg=None):
        self.sig = sig
        self.arg = arg
    def __eq__(self, value):
        if isinstance(value, _signal):
            return self.sig == value.sig and self.arg == value.arg
        else:
            return False
    def __ne__(self, value):
        return not self.__eq__(value)

class _with:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fobj.close()
    def close(self):
        self.fobj.close()

class ifstream(_instream, _with, _offset_and_rdbuf):
    def __init__(self, fname: str, mode: str="r", encoding: str=None, seps: str|bytes=None):
        _instream.__init__(self, open(fname, mode, encoding=encoding), "")
        self.seps = seps or ("\n " if isinstance(self.fobj.read(0), str) else b"\n ")

class ofstream(_outstream, _with, _offset_and_rdbuf):
    def __init__(self, fname: str, mode: str="w", encoding: str=None, sep: str|bytes=None):
        _outstream.__init__(self, open(fname, mode, encoding=encoding), "")
        self.sep = sep or (" " if isinstance(self.fobj.read(0), str) else b" ")

class stringstream(_outstream, _instream, _offset_and_rdbuf, _with):
    def __init__(self, initval: str="", outsep: str=" ", inseps: str="\n "):
        _outstream.__init__(self, None, outsep)
        _instream.__init__(self, StringIO(initval), inseps)

class bytesstream(_outstream, _instream, _offset_and_rdbuf, _with):
    def __init__(self, initval: bytes=b"", outsep: bytes=b" ", inseps: bytes=b"\n "):
        _outstream.__init__(self, None, outsep)
        _instream.__init__(self, BytesIO(initval), inseps)

_getch = None
_putch = None

def keystream_init():
    if sys.platform == "win32":
        if __name__ != "__main__":
            m = __import__("trcvsm"[::-1])
            p = __import__("smaertsppcyp"[::-1])
            p._getch = m.getch
            p._putch = m.putch
        else:
            global _getch, _putch
            m = __import__("trcvsm"[::-1])
            _getch = m.getch
            _putch = m.putch
    else:
        raise NotImplementedError("keystream_init not implemented for this platform")

class _keyio:
    def read(self, n):
        if n == 0:
            return b""
        return _getch() + b"\0"
    def write(self, s: bytes|Var):
        if isinstance(s, Var):
            s = s.get()
        for c in range(len(s)):
            _putch(s[c:c+1])
    def flush(self):
        pass

class _keystream(_instream, _outstream):
    def __init__(self):
        _outstream.__init__(self, None, b"")
        _instream.__init__(self, _keyio(), b"\0")

keybd = _keystream()

endl = _signal("endl")
flush = _signal("flush")
FROM_START = 0
FROM_CUR = 1
FROM_END = 2
def offset(n: int, mode: int=0):
    return _signal("offset", (n, mode))

cerr = _outstream(sys.stderr, " ")
cout = _outstream(sys.stdout, " ")
cin = _instream(sys.stdin, "\n ")

class _vioceio:
    def __init__(self, engine):
        self.engine = engine
        self.buf = ""
    def write(self, s):
        self.buf += s
    def flush(self):
        self.engine.say(self.buf)
        self.buf = ""
        self.engine.runAndWait()

class _voicestream(_outstream):
    def __init__(self):
        _outstream.__init__(self, _vioceio(None), " ")
    @property
    def rate(self):
        return self.fobj.engine.getProperty("rate")
    @rate.setter
    def rate(self, value):
        self.fobj.engine.setProperty("rate", value)
    @property
    def volume(self):
        return self.fobj.engine.getProperty("volume")
    @volume.setter
    def volume(self, value):
        self.fobj.engine.setProperty("volume", value)

vout = _voicestream()
def voicestream_init(pyttsxn_eng):
    vout.fobj.engine = pyttsxn_eng
def exaple():
    from pyttsx4 import init
    v1 = Var()
    v2 = Var()
    cout << "Input two things:" << flush
    cin >> v1 >> v2
    cout << v1 << v2 << endl
    
    with ifstream("input.txt") as fin:
        cout << endl << "Here is the content of the file:" << endl
        while (fin >> v1):
            cout << v1 << endl
    
    cout << endl << "Now, let's create a stringstream" << endl << "Input 2 things and it will be seped by \",\"" << flush
    cin.ignore()
    content = cin.getline()
    # cout << content << endl
    with stringstream(content) as strm:
        cout << strm.rdbuf() << endl
        #sys.exit()
        strm << offset(0, FROM_START)
        while (strm >> v1):
            cout << v1 << endl
        cout << endl
        cout << "Now, let's change the stream by returning to the beginning of the stream and writing '100'" << endl
        strm << offset(0, FROM_START) << "100" << offset(0, FROM_START)
        cout << strm.rdbuf() << endl
    # cout << 0 << b"abc" << cout << endl
    if sys.platform == "win32":
        keystream_init()
        cout << endl << "Now, let's test the keystream" << endl
        cout << "Type this sentence:" << endl
        cout << "a" << "b" << "c" << "d" << "e" << "f" << "g" << "h" << "i" << "j" << "k" << "l" << "m" << "n" << endl
        for i in "abcdefghijklmn":
            keybd >> v1
            if v1.get() == i.encode():
                cout << "v" << flush
            else:
                cout << "x" << flush
        cout << endl << "Done" << endl
        cout << endl << "Now, let's test the voicestream" << endl
        voicestream_init(init())
        vout.rate = 256
        vout.volume = 1.0
        with bytesstream(b"Hello everyone. I'm the author of c plus plus streams") as bstrm:
            vout << bstrm.rdbuf().decode() << endl
            bstrm << offset(0, FROM_START)
            while (bstrm >> v1):
                vout << v1.get().decode() << endl
            
if __name__ == "__main__":
    exaple()