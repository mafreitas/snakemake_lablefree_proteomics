import errno, glob, os, os.path, sys

lc_peak_width='120'
precursor_mass_tolerance='20'
fragment_mass_tolerance='20'
precursor_error_units='ppm'
fragment_error_units='ppm'
enzyme="Trypsin/P"
missed_cleavages = "3"
fixed_modifications = "\"Carbamidomethyl (C)\""
variable_modifications = ""
fido_protein_fdr_filter = "0.95"
peptide_fdr_filter = "0.05"
# list of search engines
# valid entries include xtandem, myrimatch, comet or msgfplus (Default)
DBSEARCH = ["msgfplus","xtandem"]
#DBSEARCH = ["xtandem"]
#debugLevel = 10


SAMPLES = []
MZMLFILES = glob.glob("raw/*")
allowed_exts = [".mzml",".mzML","MZML"]
for rawfile in MZMLFILES:
    rbase = os.path.basename(rawfile)
    rbase,rext = os.path.splitext(rbase)
    if rext in allowed_exts:
        SAMPLES.append(rbase)

DBFILES = glob.glob("fasta/*")
DATABASES = []
allowed_exts = [".fasta",".FASTA"]
for dbfile in DBFILES:
    dbase = os.path.basename(dbfile)
    dbase,dext = os.path.splitext(dbase)
    if dext in allowed_exts:
        DATABASES.append(dbase)

shell.prefix('')
configfile: "config.yaml"

if 'debugLevel' not in vars():
  debug = 0
else:
  debug = debugLevel

# Setup Targets for Pipeline
rule targets:
    input:
        expand("work/{dbsearch}/{sample}/dbsearch_{sample}.idXML", dbsearch=DBSEARCH,sample=SAMPLES),
        expand("work/featurefindermultiplex/{sample}/multiplex_{sample}.featureXML", sample=SAMPLES),
#        expand("work/{dbsearch}/{sample1}/pi_mapalignid_{sample2}.idXML", dbsearch=DBSEARCH,sample1=SAMPLES,sample2=SAMPLES),
#        expand("work/{dbsearch}/{sample}/idmerge_external_{sample}.idXML", dbsearch=DBSEARCH,sample=SAMPLES),
#        expand("work/{dbsearch}/{sample}/ffid_{sample}.featureXML", dbsearch=DBSEARCH,sample=SAMPLES),
#        expand("work/{dbsearch}/proteinid/fido_fdr_filt.idXML", dbsearch=DBSEARCH),
        expand("csv/{dbsearch}_combined_proteinCounts.csv", dbsearch=DBSEARCH),
        expand("csv/ffm_{dbsearch}_proteinIntensities.csv", dbsearch=DBSEARCH),
        expand("csv/ffc_{dbsearch}_proteinIntensities.csv", dbsearch=DBSEARCH),
        expand("csv/ffidi_{dbsearch}_proteinIntensities.csv", dbsearch=DBSEARCH),
#        expand("csv/ffida_{dbsearch}_proteinIntensities.csv", dbsearch=DBSEARCH),
#        expand("csv/ffi_full_{dbsearch}_combined_proteinIntensities.csv", dbsearch=DBSEARCH)

# Construct Concatenated Databases With Decoys
include: "rules/decoy_database.py"

# Remove Compression
include: "rules/file_conversion.py"

# Perform Database Search
for search in DBSEARCH:
    include: "rules/%s.py" % search

# Perfrom Post Processing of Database Searches
include: "rules/search_post_processing.py"

# Perform Protein Inference
include: "rules/fido.py"

# Perfrom Post Processing of Database Searches
include: "rules/feature_finder_identification_internal.py"

# Perfrom Feature Finding
include: "rules/feature_finder_multiplex.py"

# Perfrom Feature Finding
include: "rules/feature_finder_centroid.py"

# Determine Spectral Counts
include: "rules/spectral_counts.py"
