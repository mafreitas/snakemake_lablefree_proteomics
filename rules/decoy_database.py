#DecoyDatabase
rule make_database:
    input:
        expand('fasta/{database}.fasta', database=DATABASES)
    output:
        'work/database/target_decoy_database.fasta'
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        decoy_string = "-decoy_string {0}".format(config["database"]["decoy_string"]),
        decoy_string_position = "-decoy_string_position {0}".format(config["database"]["decoy_string_position"]),
        debug = '-debug %s' % debug,
        log = "work/database/target_decoy_database.log",
    shell:
        "DecoyDatabase "
        "-in {input} "
        "-out {output} "
        "-threads {threads} "
        "{params.decoy_string} "
        "{params.decoy_string_position} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
