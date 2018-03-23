# IDPosteriorErrorProbability
rule calc_peptide_posterior_error:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/dbsearch_{datafile}.idXML"
    output:
        idxml = "work/{dbsearchdir}/{datafile}/idpep_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/idpep_{datafile}.log' % search
    shell:
        "IDPosteriorErrorProbability "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "


# PeptideIndexer
rule index_peptides:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/idpep_{datafile}.idXML",
        fasta = 'work/database/target_decoy_database.fasta'
    output:
        idxml = "work/{dbsearchdir}/{datafile}/pi_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        decoy_string = "-decoy_string {0}".format(config["database"]["decoy_string"]),
        decoy_string_position = "-decoy_string_position {0}".format(config["database"]["decoy_string_position"]),
        missing_decoy_action = "-missing_decoy_action {0}".format(config["database"]["missing_decoy_action"]),
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/pi_{datafile}.log' % search
    shell:
        "PeptideIndexer "
        "-in {input.idxml} "
        "-fasta {input.fasta} "
        "-out {output.idxml} "
        "{params.decoy_string} "
        "{params.decoy_string_position} "
        "{params.missing_decoy_action} "
        "-allow_unmatched "
        "-IL_equivalent "
        "-enzyme:name {enzyme} "
        "-enzyme:specificity none "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "


# FalseDiscoveryRate:
rule peptide_fdr:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/pi_{datafile}.idXML"
    output:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/fdr_{datafile}.log' % search
    shell:
        "FalseDiscoveryRate "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "


# IDFilter
rule filter_peptide_fdr:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_{datafile}.idXML"
    output:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_filt_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/fdr_filt_{datafile}.log' % search
    shell:
        "IDFilter "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "-score:pep 0.10 "
        "-score:prot 0 "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
