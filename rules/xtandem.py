# XTandem:
rule xtandem:
    input:
        mzml = "mzml/{datafile}.mzML",
        fasta = 'work/database/target_decoy_database.fasta',
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
        "XTandemAdapter "
        "-in {input.mzml} "
        "-out {output.idxml} "
        "-database {input.fasta} "
        "-xtandem_executable tandem.exe "
        "-precursor_mass_tolerance {precursor_mass_tolerance} "
        "-precursor_error_units {precursor_error_units} "
        "-fragment_mass_tolerance {config[fragment][mass_tolerance]} "
        "-fragment_error_units {fragment_error_units} "
        "-enzyme {enzyme} -missed_cleavages {missed_cleavages} "
        "-fixed_modifications {fixed_modifications} "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
