# IDFilter
# Remove unmatched peptides (decoys)
rule filter_peptides_ffi:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_{datafile}.idXML"
    output:
        idxml = temp("work/{dbsearchdir}/{datafile}/ffidi_fdr_filt_{datafile}.idXML")
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        pepfdr = '-score:pep {0}'.format(config["peptide"]["fdr"]),
        debug = '-debug {0}'.format(config["database"]),
        log = 'work/%s/{datafile}/pi_filt_ur_{datafile}.log' % search
    shell:
        "IDFilter "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "{params.pepfdr} "
        "-score:prot 0 "
        "-delete_unreferenced_peptide_hits "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

# FeatureFinderIdentification
rule feature_finder_indentification:
    input:
        mzml = "mzml/{datafile}.mzML",
        idxml = "work/{dbsearchdir}/{datafile}/ffidi_fdr_filt_{datafile}.idXML",
    output:
        featurexml = "work/{dbsearchdir}/{datafile}/ffidi_filt_{datafile}.featureXML"
    threads:
        4
    singularity:
        "shub://mafreitas/singularity-openms:latest"
    params:
        lc_peak_width = "-detect:peak_width {0}".format(config["lc"]["peak_width"]),
        debug = '-debug {0}'.format(config["database"]),

        log = 'work/{dbsearchdir}/{datafile}/ffidi_filt_{datafile}.log'
    shell:
        "FeatureFinderIdentification "
        "-in {input.mzml} "
        "-id {input.idxml} "
        "-out {output.featurexml} "
        "{params.lc_peak_width} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#MapAlignerPoseClustering:
rule align_ffi_maps:
    input:
        featurexmls = expand("work/{{dbsearchdir}}/{sample}/ffidi_filt_{sample}.featureXML",sample=SAMPLES)
    output:
        featurexmls =
        temp(expand("work/{{dbsearchdir}}/{sample}/ffidi_filt_align_{sample}.featureXML",sample=SAMPLES))
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        mz_max_difference = "-algorithm:pairfinder:distance_MZ:max_difference 20",
        mz_unit = "-algorithm:pairfinder:distance_MZ:unit ppm",
        debug = '-debug {0}'.format(config["database"]),

        log = 'work/{dbsearchdir}/ffidi_filt_align_.log'
    shell:
        "MapAlignerPoseClustering "
        "-in {input.featurexmls} "
        "-out {output.featurexmls} "
        "-threads {threads} "
        "{params.mz_max_difference} "
        "{params.mz_unit} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#FeatureLinkerUnlabeledQT:
rule link_ffi_maps:
    input:
        featurexmls = expand("work/{{dbsearchdir}}/{sample}/ffidi_filt_align_{sample}.featureXML",sample=SAMPLES)
    output:
        featurexml =
        temp("work/{dbsearchdir}/ffidi_flq.consensusXML")
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        mz_max_difference = "-algorithm:distance_MZ:max_difference 20",
        mz_unit = "-algorithm:distance_MZ:unit ppm",
        debug = '-debug {0}'.format(config["database"]),

        log = 'work/{dbsearchdir}/ffidi_flq.log'
    shell:
        "FeatureLinkerUnlabeledQT "
        "-in {input.featurexmls} "
        "-out {output.featurexml} "
        "-threads {threads} "
        "{params.mz_max_difference} "
        "{params.mz_unit} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#IDConflictResolverRule
rule resolve_ffi_map_conflicts:
    input:
        featurexml = "work/{dbsearchdir}/ffidi_flq.consensusXML"
    output:
        featurexml = temp("work/{dbsearchdir}/ffidi_flq_idcr.consensusXML")
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug {0}'.format(config["database"]),

        log = 'work/{dbsearchdir}/ffidi_flq_idcr.log'
    shell:
        "IDConflictResolver "
        "-in {input.featurexml} "
        "-out {output.featurexml} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#ConsensusMapNormalizer:
rule normalize_ffi_maps:
    input:
        featurexml = "work/{dbsearchdir}/ffidi_flq_idcr.consensusXML"
    output:
        featurexml = temp("work/{dbsearchdir}/ffidi_flq_idcr_cmn.consensusXML")
    singularity:
        config['singularity']['default']
    threads:
        14
    params:
        debug = '-debug {0}'.format(config["database"]),

        log = 'work/{dbsearchdir}/ffidi_flq_idcr_cmn.log'
    shell:
        "ConsensusMapNormalizer "
        "-in {input.featurexml} "
        "-out {output.featurexml} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

# ProteinQuantifier
rule quantify_proteins_ffi_maps:
    input:
        featurexml = "work/{dbsearchdir}/ffidi_flq_idcr_cmn.consensusXML",
        fido = "work/{dbsearchdir}/proteinid/fido_fdr_filt.idXML"
    output:
        csv = "csv/ffidi_{dbsearchdir}_proteinIntensities.csv"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug {0}'.format(config["database"]),

        log = "csv/ffidi_{dbsearchdir}_proteinIntensities.log"
    shell:
        "ProteinQuantifier "
        "-in {input.featurexml} "
        "-protein_groups {input.fido} "
        "-out {output.csv} "
        "-top 0 "
        "-average sum "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "
