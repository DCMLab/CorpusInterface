from unittest import TestCase
import CorpusInterface as ci

# What are the tests?

# Check download/file/git access (assume network access)
#   * Construct test corpora with known properties
#   * Check that download works (return values, exceptions etc.)
#   * Check that files exist in correct places, with non-zero size
# Check loading of TSV/CSV/MIDI/eventually MXML/MEI
#   * Use above test corpora
#   * Check that load works (return values, exceptions etc.)
#   * Check properties of known corpora
#      * Number of entries
#      * Basic parsing of entries (need to keep up with datatypes in that case)
#    

class TestGitMIDICorpus(TestCase):

  def test_download(self):
    ci.download(name="testcorpus-git-midi")
    
  def test_load(self): 
    fc = ci.load(name="testcorpus-git-midi")
    assert(len(fc.document_list) == 1)
    assert(list(fc.document_list[0].__iter__())[0].data.velocity == 80)


class TestURLTSVCorpus(TestCase):

  def test_download(self):
    ci.download(name="testcorpus-http-tsv")
    
  def test_load(self): 
    fc = ci.load(name="testcorpus-http-tsv")
    assert(len(fc.document_list) == 1)
    assert(list(fc.document_list[0].__iter__())[0].duration.real == 2.5)

class TestGITJSONCorpus(TestCase):

  def combine_data(self,zipp, meter):
    return ci.datatypes.Event(ci.datatypes.LinearTime(zipp[1] * meter + zipp[2]), None, zipp[0]) 

  def extract_chords(self,json):
    meter = json['meter']['numerator'] / json['meter']['denominator']
    zipped = zip(json['chords'], json['measures'], json['beats'])
    return map(lambda x : self.combine_data(x, meter), zipped)
    

  def test_load(self):
    jc = ci.load(name="testcorpus-git-json", document_reader=self.extract_chords, allow_download=True)
    document_list = list(jc.document_list)
    assert(len(document_list) == 1)
    assert(list(document_list[0].__iter__())[0].data == "D7")

class TestGITCSVCorpus(TestCase):

  def test_load(self):
    jc = ci.load(name="testcorpus-git-csv", allow_download=True)
    document_list = list(jc.document_list)
    assert(len(document_list) == 1)
    assert(document_list[0][1]['chord'][0] == "D")



