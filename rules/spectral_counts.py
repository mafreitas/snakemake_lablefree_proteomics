# IDFilter
rule filter_peptides_sc:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/fdr_{datafile}.idXML"
    output:
        idxml = "work/{dbsearchdir}/{datafile}/sc_filt_{datafile}.idXML"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = 'work/%s/{datafile}/sc_filt_{datafile}.log' % search
    shell:
        "IDFilter "
        "-in {input.idxml} "
        "-out {output.idxml} "
        "-delete_unreferenced_peptide_hits "
        "-score:pep {peptide_fdr_filter} "
        "-score:prot 0 "


# ProteinQuantifierSeparate
rule count_spectra_perfile:
    input:
        idxml = "work/{dbsearchdir}/{datafile}/sc_filt_{datafile}.idXML",
        fido = "work/{dbsearchdir}/proteinid/fido_fdr_filt.idXML"
    output:
        csv = "csv/{datafile}_{dbsearchdir}_proteinCounts.csv"
    singularity:
        config['singularity']['default']
    threads:
        1
    params:
        debug = '-debug %s' % debug,
        log = "csv/{datafile}_{dbsearchdir}_proteinCounts.log"
    singularity:
        config['singularity']['default']
    shell:
        "ProteinQuantifier "
        "-in {input.idxml} "
        "-protein_groups {input.fido} "
        "-out {output.csv} "
        "-top 0 "
        "-average sum "
        "-include_all "
        "-threads {threads} "
        "{params.debug} "
        "2>&1 | tee {params.log} "

# ProteinQuantifierCombiner
rule combine_spectral_counts:
    input:
        csvs = expand(
            "csv/{sample}_{{dbsearchdir}}_proteinCounts.csv", sample=SAMPLES)
    output:
        csv = "csv/{dbsearchdir}_combined_proteinCounts.csv"
    params:
        names = expand("{sample}", sample=SAMPLES),
        log = 'false'
    threads:
        1
    run:
        import pandas as pd
        import numpy as np
        import glob
        import os

        files = input.csvs
        df = pd.read_csv(files[0], sep="\t", skiprows=2)
        colnames = df.columns

        newnames = [colnames[0]]
        for i in range(1, len(colnames)):
            name = colnames[i]
            newnames.append(params.names[0] + name)
        df.columns = newnames

        for i in range(1, len(files)):
            dft = pd.read_csv(files[i], sep="\t", skiprows=2)

            colnames = dft.columns
            newnames = [colnames[0]]
            for j in range(1, len(colnames)):
                name = colnames[j]
                newnames.append(params.names[i] + "_" + name)
            dft.columns = newnames

            df = pd.merge(df, dft, how="outer", on='protein')

        df.to_csv(output.csv)
