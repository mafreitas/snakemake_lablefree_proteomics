# File Conversion:
rule fix_mzml_files:
    input:
        mzml = expand("{location}/{{datafile}}.mzML",location=config["mzml"]["location"]),
    output:
        mzml = temp("mzml/{datafile}.mzML")
    singularity:
        config['singularity']['default']
    threads: 1
    priority: 1
    params:
        debug = '-debug {0}'.format(config["debug"]),
        log = 'mzml/{datafile}.log'
    shell:
        "FileConverter "
        "-in {input.mzml} "
        "-out {output.mzml} "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
