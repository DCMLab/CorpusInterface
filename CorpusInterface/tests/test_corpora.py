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

class TestURLTSVCorpus(TestCase):

  def test_download(self):
    ci.download(name="testcorpus-http-tsv")
    
  def test_load(self): 
    fc = ci.load(name="testcorpus-http-tsv")





