import psycopg2
import re

conn_string = "host='localhost' dbname='app_dprr_lcl' user='yyyyyyyy' password='xxxxxxxx'"
dirName = "d:/research/DPRR/d2rq-0.8.1/"
infile_name = dirName+"dprr_dump.ttl"
outfile_name = dirName+"dprr_clean.ttl"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

praenomens = 100*['']
stmt = "select id, abbrev from promrep_praenomen"
cursor.execute(stmt)
records = cursor.fetchall()
for record in records:
    id = record[0]
    abbrev = record[1]
    praenomens[id] = abbrev.strip()

def buildName(id):
    global praenomens
    stmt = "select sex_id, praenomen_id, alt_praenomen_id, praenomen_uncertain, nomen, re_number, filiation, cognomen, other_names,dprr_id from promrep_person where id="+str(id)
    cursor.execute(stmt)
    records = cursor.fetchall()
    if len(records) != 1:
        print "unexpected number of records for person id:",str(id)
        return ""
    (sex_id, praenomen_id, alt_praenomen_id, praenomen_uncertain, nomen, re_number, filiation, cognomen, other_names, dprr_id) = records[0]
    # modelled after code from Luis Figueira: actual function that computes head names in DPRR
    name = ""
    if dprr_id and len(dprr_id) > 0:
        name += dprr_id+' '
    # only show praenomen for men
    if sex_id == 1 and praenomen_id:
        name += praenomens[praenomen_id]
        if alt_praenomen_id:
            name += " (or " + praenomens[alt_praenomen_id] + ")"
        elif praenomen_uncertain:
            name += "?"
    if nomen:
        name += ' ' + nomen
    if re_number:
        name += ' (' + re_number + ')'
    if filiation:
        if filiation not in ['- f. - n.', '- f.', '- n.']:
            name += ' ' + filiation
    stmt2 = "select t.abbrev from promrep_tribe as t, promrep_tribeassertion as ta where ta.tribe_id=t.id and ta.person_id="+str(id)
    cursor.execute(stmt2)
    tribes = cursor.fetchall()
    for t in tribes:
        name += " " + t[0]
    if cognomen:
        name += " " + cognomen
    if other_names:
        name += ' ' + other_names
    return name.strip()

def getstmt():
    l = infile.readline()
    l = re.sub(r'"t"',r"true",l) 
    if len(l) == 0:
        return l
    if l == "\n":
        return l
    if l.startswith("@prefix"):
        return l
    r = re.findall(r'"""',l)
    if r:
        loop = True
        while loop:
            l1 = infile.readline()
            l1 = re.sub(r'"t"',r"true",l1) 
            l += l1
            loop = len(re.findall(r'"""', l1)) == 0
        return l
    lnl = l.strip()
    if len(lnl) > 0 and (lnl[-1] not in [";", "."]):
        l1 = infile.readline()
        l1 = re.sub(r'"t"',r"true",l1) 
        return l + l1
    return l

infile = file(infile_name,"r")
outfile = file(outfile_name,"w")

stmt = getstmt()
while len(stmt) != 0:
    if stmt.startswith("@prefix") or stmt=="\n":
        outfile.write(stmt)
    else:
        stmt = re.sub(r'entity/Praenomen/\-\.',r'entity/Praenomen/missing',stmt)
        r = re.findall(r'"f?"', stmt)
        r1 = re.findall(r'"""', stmt)
        if r and (not r1):
            stm2 = stmt.strip()
            if(stm2[-1] == "."):
                outfile.write(".\n")
        else:
            r = re.findall(r'Person: #(\d+)', stmt)
            if r:
                pid = r[0]
                # stmt = '      rdfs:label "'+buildName(pid)+'" ;\n'
                stmt = '      vocab:hasPersonName "'+buildName(pid)+'" ;\n'
            chrs = re.sub(r"\s", "", stmt)
            if len(chrs) > 4 or chrs == ".":
                outfile.write(stmt)
    stmt = getstmt()
    if re.findall(r"Province: \#Sicilia",stmt):
        print "statement found"

infile.close()
outfile.close()
print "Done!"
