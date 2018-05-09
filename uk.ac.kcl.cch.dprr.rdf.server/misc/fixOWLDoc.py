import os.path
import os
import re

baseDir = "d:/research/DPRR/OWLDoc/"
dirs = ['annotationproperties', 'classes', 'dataproperties', 'datatypes', 'objectproperties', 'ontologies']

def addTarget(forFile):
    iFile = open(forFile,"r")
    iText = iFile.read()
    iFile.close()
    if not re.findall(r'target="content"', iText):
        iText = re.sub(r'("[a-z/A-Z]+___-?\d+.html")', r'\1 target="content"', iText)
        iFile = open(forFile, "w")
        iFile.write(iText)
        iFile.close()
   

def doDir(dir):
    indexFile = baseDir+dir+"/index.html"
    if os.path.exists(baseDir+dir+"/index-ontology.html"):
        newIndexFile = baseDir+dir+"/index-ontology.html"
        os.remove(indexFile)
        os.rename(newIndexFile, indexFile)
    addTarget(indexFile)
  
for dir in dirs:
    doDir(dir)
addTarget(baseDir+"index-all.html")