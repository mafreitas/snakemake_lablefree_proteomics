# FeatureFinderMultiplex
rule find_features_multiplex:
    input:
        mzml = "mzml/{datafile}.mzML",
    output:
        consensusxml = "work/featurefindermultiplex/{datafile}/multiplex_{datafile}.consensusXML",
        featurexml = "work/featurefindermultiplex/{datafile}/multiplex_{datafile}.featureXML"
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/featurefindermultiplex/{datafile}/multiplex_{datafile}.log'
    singularity:
        config['singularity']['default']
    shell:
         "FeatureFinderMultiplex "
         "-in {input.mzml} -out {output.consensusxml} "
         "-out_features {output.featurexml} "
         "-threads {threads} "
         "{params.debug} "
         "2>&1 | tee {params.log} "

# IDFilter
rule filter_peptides_ffm:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_{datafile}.idXML"
    output:
        idxml = "work/{dbsearchdir}/{datafile}/ffm_filt_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/ffm_filt_{datafile}.log' % search
    shell:
        "IDFilter "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "-score:pep {peptide_fdr_filter} "
        "-score:prot 0 "
        "-delete_unreferenced_peptide_hits "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#IDMapper
rule map_ffm_features:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/ffm_filt_{datafile}.idXML",
        featurexml = "work/featurefindermultiplex/{datafile}/multiplex_{datafile}.featureXML"
    output:
        featurexml = "work/{dbsearchdir}/{datafile}/ffm_filt_idmap_{datafile}.featureXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        centroid_rt = "-feature:use_centroid_rt ",
        centroid_mz = "-feature:use_centroid_mz ",
        debug = '-debug %s' % debug,
        log = 'work/{dbsearchdir}/{datafile}/ffm_filt_idmap_{datafile}.log'
    shell:
        "IDMapper "
        "-id {input.idxml} "
        "-in {input.featurexml} "
        "-out {output.featurexml} "
        "{params.centroid_rt} "
        "{params.centroid_mz} "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#MapAlignerPoseClustering:
rule align_ffm_maps:
    input:
        featurexmls = expand("work/{{dbsearchdir}}/{sample}/ffm_filt_idmap_{sample}.featureXML",sample=SAMPLES)
    output:
        featurexmls =
        expand("work/{{dbsearchdir}}/{sample}/ffm_filt_idmap_align_{sample}.featureXML",sample=SAMPLES)
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        mz_max_difference = "-algorithm:pairfinder:distance_MZ:max_difference 20",
        mz_unit = "-algorithm:pairfinder:distance_MZ:unit ppm",
        debug = '-debug %s' % debug,
        log = 'work/{dbsearchdir}/ffm_filt_idmap_align.log'
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
rule link_ffm_maps:
    input:
        featurexmls = expand("work/{{dbsearchdir}}/{sample}/ffm_filt_idmap_align_{sample}.featureXML",sample=SAMPLES)
    output:
        featurexml =
        "work/{dbsearchdir}/ffm_flq.consensusXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        mz_max_difference = "-algorithm:distance_MZ:max_difference 20",
        mz_unit = "-algorithm:distance_MZ:unit ppm",
        debug = '-debug %s' % debug,
        log = 'work/{dbsearchdir}/ffm_flq.log'
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
rule resolve_ffm_map_conflicts:
    input:
        featurexml = "work/{dbsearchdir}/ffm_flq.consensusXML"
    output:
        featurexml = "work/{dbsearchdir}/ffm_flq_idcr.consensusXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/{dbsearchdir}/ffm_flq_idcr.log'
    shell:
        "IDConflictResolver "
        "-in {input.featurexml} "
        "-out {output.featurexml} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

#ConsensusMapNormalizer:
rule normalize_ffm_maps:
    input:
        featurexml = "work/{dbsearchdir}/ffm_flq_idcr.consensusXML"
    output:
        featurexml = "work/{dbsearchdir}/ffm_flq_idcr_cmn.consensusXML"
    singularity:
        config['singularity']['default']
    threads:
        14
    params:
        debug = '-debug %s' % debug,
        log = 'work/{dbsearchdir}/ffm_flq_idcr_cmn.log'
    shell:
        "ConsensusMapNormalizer "
        "-in {input.featurexml} "
        "-out {output.featurexml} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

# ProteinQuantifier
rule quantify_proteins_ffm_maps:
    input:
        featurexml = "work/{dbsearchdir}/ffm_flq_idcr_cmn.consensusXML",
        fido = "work/{dbsearchdir}/proteinid/fido_fdr_filt.idXML"
    output:
        csv = "csv/ffm_{dbsearchdir}_proteinIntensities.csv"
    priority:
        90
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = "csv/ffm_{dbsearchdir}_proteinIntensities.log"
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
