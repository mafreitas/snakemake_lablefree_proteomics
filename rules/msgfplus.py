# MSGFPlusIndexDB:
rule msgfplus_db_index:
    input:
        fasta = 'work/database/target_decoy_database.fasta'
    output:
        index = 'work/database/target_decoy_database.canno'
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/database/MSGFPlusIndexDB.log'
    shell:
        "java -Xmx3500M -cp /usr/local/openms_thirdparty/All/MSGFPlus/MSGFPlus.jar "
        "edu.ucsd.msjava.msdbsearch.BuildSA "
        "-d {input.fasta} "
        "-tda 0 "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

# MSGFPlus
rule msgfplus:
    input:
        mzml = "mzml/{datafile}.mzML",
        fasta = 'work/database/target_decoy_database.fasta',
        index = 'work/database/target_decoy_database.canno'
    output:
        idxml = "work/%s/{datafile}/dbsearch_{datafile}.idXML" % search
    singularity:
        config['singularity']['default']
    threads:
        4
    priority:
        10
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/dbsearch_{datafile}.log' % search
    shell:
        "MSGFPlusAdapter "
        "-in {input.mzml} -out {output.idxml} -database {input.fasta} "
        "-executable "
        "/usr/local/openms_thirdparty/All/MSGFPlus/MSGFPlus.jar "
        "-precursor_mass_tolerance {precursor_mass_tolerance} "
        "-precursor_error_units {precursor_error_units} "
        "-enzyme {enzyme} "
        "-fixed_modifications {fixed_modifications} "
        "-java_memory 8192 "
        "-isotope_error_range 0,0 "
        "-instrument Q_Exactive "
        "-max_precursor_charge 4 "
        "-add_features "
        "-max_mods 3 "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
