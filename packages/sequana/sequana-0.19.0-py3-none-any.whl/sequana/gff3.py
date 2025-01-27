#
#  This file is part of Sequana software
#
#  Copyright (c) 2016-2022 - Sequana Development Team
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
import sys
from collections import defaultdict

import colorlog

from sequana.errors import BadFileFormat
from sequana.lazy import pandas as pd
from sequana.lazy import pysam

logger = colorlog.getLogger(__name__)

__all__ = ["GFF3"]


class GFF3:
    """Read a GFF file, version 3


    .. seealso:: https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md


    ::

        g = GFF3(filename)
        # first call is slow
        g.df
        # print info about the different feature types
        g.features
        # prints info about duplicated attributes:
        g.get_duplicated_attributes_per_genetic_type(self)

    On eukaryotes, the reading and processing of the GFF may take a while.
    On prokaryotes, it should be pretty fast (a few seconds).
    To speed up the eukaryotes case, we skip the processing biological_regions
    (50% of the data in mouse).

    """

    def __init__(self, filename, skip_types=["biological_region"]):
        self.filename = filename
        self.skip_types = skip_types
        self._df = None
        self._features = None
        self._attributes = None

    def _get_features(self):
        """Extract unique GFF feature types

        This is equivalent to awk '{print $3}' | sort | uniq to extract unique GFF
        types. No sanity check, this is suppose to be fast.

        Less than a few seconds for mammals.
        """
        # This is used by the rnaseq pipeline and should be kept fast
        count = 0
        if self._features:
            features = self._features
        else:
            features = set()
            with open(self.filename, "r") as reader:
                for line in reader:
                    # Skip metadata and comments
                    if line.startswith("#"):
                        continue
                    # Skip empty lines
                    if not line.strip():  # pragma: no cover
                        continue
                    split = line.rstrip().split("\t")
                    L = len(split)
                    if L == 9:
                        features.add(split[2])
                    count += 1
                # FIXME may be overwritten by get_df
                self._features = features

        return sorted(features)

    features = property(_get_features)

    def get_attributes(self, feature=None):
        """Return list of possible attributes

        If feature is provided, must be valid and used as a filter
        to keep only entries for that feature.

        ~10 seconds on mouse genome GFF file.

        sep must be "; " with extra space to cope with special cases
        where an attribute has several entries separated by ; e.g.:

            BP="GO:0006412"; MF="GO:0005524;GO:0004004;"

        """
        # This is used by the rnaseq pipeline and should be kept fast
        if feature:
            dd = self.df.query("genetic_type == @feature")
            self._attributes = sorted(dd.loc[:, dd.notna().all()].columns[8:])
        else:
            self._attributes = sorted(self.df.columns[8:])

        return self._attributes

    def read(self):
        """Read annotations one by one creating a generator"""

        self._features = set()

        with open(self.filename, "r") as reader:
            line = None
            for line in reader:
                # stop once FASTA starts
                if line.startswith("##FASTA"):
                    break

                # Skip metadata and comments
                if line.startswith("#"):
                    continue

                # Skip empty lines
                if not line.strip():
                    continue

                # Format checking. skip rows that do not have 9 columns since
                # it is comments or fasta sequence
                split = line.rstrip().split("\t")
                if len(split) != 9:
                    continue

                # skipping  biological_region saves lots of time
                if split[2].strip() in self.skip_types:
                    continue

                # we process main fields and attributes. This takes most of the
                # time
                self._features.add(split[2])

                # the main first 8 fields
                annotation = self._process_main_fields(split[0:8])

                # all attributes as key/values added to all annotations.
                annotation["attributes"] = self._process_attributes(split[8])
                annotation.update(annotation["attributes"])

                yield annotation

    def _get_df(self):
        if self._df is not None:
            return self._df

        logger.info("Processing GFF file. 1. Reading the input file. Please be patient")
        # ~ 30 seconds on mouse
        df = pd.DataFrame(self.read())

        self._df = df
        return self._df

    df = property(_get_df)

    def get_duplicated_attributes_per_genetic_type(self):
        results = {}
        for typ in self.features:
            results[typ] = {}
            print("{}: {} entries".format(typ, len(self.df.query("genetic_type==@typ"))))
            for attr in sorted(self.get_attributes(feature=typ)):
                L = len(self.df.query("genetic_type==@typ")[attr].dropna())
                dups = self.df.query("genetic_type==@typ")[attr].dropna().duplicated().sum()
                if dups > 0:
                    print(f"  - {attr}:{dups} duplicates ({L} in total)")
                else:
                    print(f"  - {attr}:No duplicates ({L} in total)")
                results[typ][attr] = dups

        df = pd.DataFrame(results)
        return df

    def transcript_to_gene_mapping(self, feature="all", attribute="transcript_id"):
        """

        :param feature: not used yet
        :param attribute: the attribute to be usde. should be transcript_id for
            salmon compatability but could use soething different.
        """
        # entries may have transcripts set to None
        transcripts = [x for x in self.df[attribute] if x]

        # retrieve only the data with transcript id defined
        transcripts_df = self.df.set_index(attribute)
        transcripts_df = transcripts_df.loc[transcripts]
        transcripts_df = transcripts_df.reset_index()

        results = {}

        results2 = defaultdict(list)
        for _id, data in transcripts_df[["ID", "Parent"]].iterrows():
            results[data.values[0]] = data.values[1]
            results2[data.values[1]].append(data.values[0])

        return results, results2

    def save_annotation_to_csv(self, filename="annotations.csv"):
        self.df.to_csv(filename, index=False)

    def read_and_save_selected_features(self, outfile, features=["gene"]):
        count = 0
        with open(self.filename, "r") as fin, open(outfile, "w") as fout:
            for line in fin:
                # stop once FASTA starts
                if line.startswith("##FASTA"):
                    break
                split = line.rstrip().split("\t")
                # skipping  biological_region saves lots of time
                try:
                    if split[2].strip() in features:
                        fout.write(line)
                        count += 1
                except IndexError:
                    pass
        logger.info(f"Found {count} entries and saved into {outfile}")

    def save_gff_filtered(self, filename="filtered.gff", features=["gene"], replace_seqid=None):
        """

        save_gff_filtered("test.gff", features=['misc_RNA', 'rRNA'],
                replace_seqid='locus_tag')
        """
        with open(filename, "w") as fout:
            fout.write("#gff-version 3\n#Custom gff from sequana\n")
            count = 0
            from collections import defaultdict

            counter = defaultdict(int)
            for x, y in self.df.iterrows():
                if y["genetic_type"] in features:
                    if replace_seqid:
                        y["seqid"] = y["attributes"][replace_seqid]
                    fout.write(
                        "{}\tfeature\tcustom\t{}\t{}\t.\t{}\t{}\t{}\n".format(
                            y["seqid"],
                            y["start"],
                            y["stop"],
                            y["strand"],
                            y["phase"],
                            ";".join([f"{a}={b}" for a, b in y["attributes"].items()]),
                        )
                    )
                    counter[y["genetic_type"]] += 1
                    count += 1
            logger.info("# kept {} entries".format(count))
            for feature in features:
                counter[feature] += 0
                logger.info("# {}: {} entries".format(feature, counter[feature]))

    def _process_main_fields(self, fields):
        annotation = {}

        # Unique id of the sequence
        annotation["seqid"] = fields[0]

        # Optional source
        if fields[1] != ".":
            annotation["source"] = fields[1]

        # Annotation type
        annotation["genetic_type"] = fields[2]

        # Start and stop
        annotation["start"] = int(fields[3])
        annotation["stop"] = int(fields[4])

        # Optional score field
        if fields[5] != ".":
            annotation["score"] = float(fields[5])

        # Strand
        if fields[6] == "+" or fields[6] == "-" or fields[6] == "?" or fields[6] == ".":
            annotation["strand"] = fields[6]

        # Phase
        if fields[7] != ".":
            annotation["phase"] = int(fields[7]) % 3
        else:
            annotation["phase"] = fields[7]
        return annotation

    def _process_attributes(self, text):
        attributes = {}

        # some GFF/GTF use different conventions:
        # - "ID=1;DB=2"     this is the standard
        # - "ID 1;DB 2"     some gtf uses spaces but should be fine
        # - "ID=1;DB=2;Note=some text with ; character " worst case scenario
        # In the later case, there is no easy way to fix this. I believe this is
        # a non-compatible GFF file.

        # we first figure out whether this is a = or space convention

        sep = None
        text = text.strip()
        # find the first = or  space indicating the key=value operator (e.g. =)
        for x in text:
            if x in ["=", " "]:
                sep = x
                break

        if sep is None:
            logger.error(f"Your GFF/GTF does not seem to be correct ({text}). Expected a = or space as separator")
            sys.exit(1)

        # ugly but fast replacement of special characters.
        text = text.replace("%09", "\t").replace("%0A", "\n").replace("%0D", "\r")
        text = text.replace("%25", "%").replace("%3D", "=").replace("%26", "&").replace("%2C", ",")
        text = text.replace("%28", "(").replace("%29", ")")  # brackets
        # we do not convert the special %3B into ;  or %20 into spaces for now

        import re

        def parse_gff_attributes(attributes, sep="="):
            """parse attributes so handle

            Quoted values (e.g., key="value")
            Unquoted values (e.g., key=value)
            Empty values (e.g., key="")
            Values with semicolons (e.g., MF="GO:0005524;GO:0004004")
            """
            # Regular expression to match key=value pairs with or without quotes

            pattern = re.compile(r'(\S+?)[= ](".*?"|[^;]*)(?:;|$)')

            # Dictionary to store parsed attributes
            parsed_attributes = {}

            # Find all matches for key=value pairs
            matches = pattern.findall(attributes)

            # Populate dictionary with matches
            for key, value in matches:
                # Remove quotes around the value if present
                value = value.strip('"')
                parsed_attributes[key] = value

            return parsed_attributes

        return parse_gff_attributes(text)

        # replace " by nothing (GTF case)
        # attributes[attr[:idx]] = value.replace('"', "").replace("%3B", ";").replace("%20", " ")

    def to_gtf(self, output_filename="test.gtf", mapper={"ID": "{}_id"}):
        # experimental . used by rnaseq pipeline to convert input gff to gtf,
        # used by RNA-seqc tools

        fout = open(output_filename, "w")

        with open(self.filename, "r") as reader:
            for line in reader:
                # stop once FASTA starts
                if line.startswith("##FASTA"):
                    break
                # Skip metadata and comments
                if line.startswith("#"):
                    fout.write(line)
                    continue
                # Skip empty lines
                if not line.strip():  # pragma: no cover
                    continue
                split = line.rstrip().split("\t")
                L = len(split)

                name = split[0]
                source = split[1]
                feature = split[2]
                start = split[3]
                stop = split[4]
                a = split[5]
                strand = split[6]
                b = split[7]
                attributes = split[8]

                new_attributes = ""
                for item in attributes.split(";"):
                    try:
                        key, value = item.split("=")
                        if key in mapper.keys():
                            key = mapper[key].format(feature)
                        new_attributes += '{} "{}";'.format(key, value)
                    except:
                        pass

                # Here we need some cooking due to gtf/gff clumsy conventiom
                # 1. looks like attributes' values must have "" surrounding their content
                # 2. if feature is e.g. exon, then gtf expects the exon_id attribute
                msg = f"{name}\t{source}\t{feature}\t{start}\t{stop}\t{a}\t{strand}\t{b}\t{new_attributes}\n"
                fout.write(msg)

        fout.close()

    def to_fasta(self, ref_fasta, fasta_out, features=["gene"], identifier="ID"):
        """From a genomic FASTA file ref_fasta, extract regions stored in the
        gff. Export the corresponding regions to a FASTA file fasta_out.

        :param ref_fasta: path to genomic FASTA file to extract rRNA regions from.
        :param fasta_out: path to FASTA file where rRNA regions will be exported to.
        """

        count = 0

        with pysam.Fastafile(ref_fasta) as fas:
            with open(fasta_out, "w") as fas_out:
                for record in self.df.to_dict("records"):
                    if record["genetic_type"] in features:
                        region = f"{record['seqid']}:{record['start']}-{record['stop']}"
                        ID = record[identifier]
                        seq_record = f">{ID}\n{fas.fetch(region=region)}\n"
                        fas_out.write(seq_record)
                        count += 1

        logger.info(f"{count} regions were extracted from '{ref_fasta}' to '{fasta_out}'")

    def to_pep(self, ref_fasta, fasta_out):
        """Extract CDS, convert to proteines and save in file"""
        raise NotImplementedError
        df = self.df.query("genetic_type=='CDS'")

    def to_bed(self, output_filename, attribute_name, features=["gene"]):
        """Experimental export to BED format to be used with rseqc scripts

        :param str attribute_name: the attribute_name name to be found in the
            GFF attributes
        """

        # rseqc expects a BED12 file. The format is not clear from the
        # documentation. The first 6 columns are clear (e.g., chromosome name
        # positions, etc) but last one are not. From the examples, it should be
        # block sizes, starts of the transcript but they recommend bedops
        # gff2bed tool that do not extract such information. For now, for
        # prokaryotes, the block sizes version have been implemented and worked
        # on a leptospira example.
        fout = open(output_filename, "w")
        with open(self.filename, "r") as reader:
            for line in reader:
                # stop once FASTA starts
                if line.startswith("##FASTA"):
                    break
                # Skip metadata and comments
                if line.startswith("#"):
                    continue
                # Skip empty lines
                if not line.strip():  # pragma: no cover
                    continue

                # a line is read and split on tabulations
                split = line.rstrip().split("\t")

                chrom_name = split[0]
                # source = split[1]    #keep this code commented for book-keeping
                feature = split[2]
                gene_start = int(split[3])
                gene_stop = int(split[4])
                cds_start = gene_start  # for prokaryotes, for now cds=gene
                cds_stop = gene_stop
                a = split[5]  # not used apparently
                strand = split[6]
                b = split[7]  # not used apparently
                attributes = split[8]  # may be required for eukaryotes

                score = 0  # in examples for rseqc, the score is always zero
                unknown = 0  # a field not documented in rseqc
                block_count = 1
                block_sizes = f"{cds_stop-cds_start},"  # fixme +1 ?
                block_starts = "0,"  # commas are important at the end. no spaces
                # according to rseqc (bed.py) code , the expected bed format is
                # chrom, chrom_start, chrom_end, gene name, score, strand, cdsStart, cdsEnd,
                # blockcount, blocksizes, blockstarts where blocksizes and blocks
                # starts are comma separated list. Here is a line example on
                # human:
                # chr1	1676716 1678658 NM_001145277 0 +    1676725 1678549 0 4	182,101,105, 0,2960,7198

                # for now only the feature 'gene' is implemented. We can
                # generalize this later on.
                if feature in features:
                    gene_name = None
                    for item in attributes.split(";"):
                        if item.split("=")[0].strip() == attribute_name:
                            gene_name = item.split("=")[-1]
                    assert gene_name
                    # should be the cds start/stop but for now we use the gene
                    # info start/stop
                    msg = f"{chrom_name}\t{gene_start}\t{gene_stop}\t{gene_name}\t{score}\t{strand}\t{cds_start}\t{cds_stop}\t{unknown}\t{block_count}\t{block_sizes}\t{block_starts}\n"
                    fout.write(msg)

        fout.close()

    def clean_gff_line_special_characters(self, text):
        """Simple leaner of gff lines that may contain special characters"""
        text = text.replace("%09", "\t").replace("%0A", "\n").replace("%0D", "\r")
        text = text.replace("%25", "%").replace("%3D", "=").replace("%26", "&").replace("%2C", ",")
        text = text.replace("%28", "(").replace("%29", ")")  # brackets
        return text

    def get_simplify_dataframe(self):
        """Method to simplify the gff and keep only the most informative features."""
        # Set weight for genetic type to sort them and keep only the most informative
        if self.df.empty:
            raise BadFileFormat("%s file is not a GFF3.", self.filename)
        genetype = ["tRNA", "rRNA", "ncRNA", "CDS", "exon", "gene", "tRNA"]
        worst_score = len(genetype) + 1
        weight = {k: i for i, k in enumerate(genetype)}
        # Note seems optional

        tokeep = [
            x
            for x in [
                "seqid",
                "genetic_type",
                "start",
                "stop",
                "strand",
                "gene",
                "gene_id",
                "gene_name",
                "locus_tag",
                "Note",
                "product",
            ]
            if x in self.df.columns
        ]

        df = self.df.filter(tokeep, axis=1)

        # remove region and chromosome row
        df = df.drop(df.loc[df.genetic_type.isin({"region", "chromosome"})].index)
        try:
            df["gene"] = df["gene"].fillna(df.locus_tag)
        except (KeyError, AttributeError):
            pass
        df["score"] = [weight.get(g_t, worst_score) for g_t in df.genetic_type]
        # keep most informative features if on the same region
        best_idx = df.groupby(["seqid", "start", "stop"])["score"].idxmin()
        return df.loc[best_idx].reset_index(drop=True)

    def get_features_dict(self):
        """Format feature dict for sequana_coverage."""
        df = self.get_simplify_dataframe()
        # rename column to fit for sequana_coverage
        df = df.set_index("seqid").rename(columns={"start": "gene_start", "stop": "gene_end", "genetic_type": "type"})
        return {chr: df.loc[chr].to_dict("records") for chr in df.index.unique()}

    def get_seqid2size(self):
        return dict([(row.seqid, row.stop) for _, row in self.df.query("genetic_type=='region'").iterrows()])

    def search(self, pattern):
        from numpy import logical_or, zeros

        pattern = str(pattern)
        hits = zeros(len(self.df))
        for col in self.df.columns:
            hits = logical_or(self.df[col].apply(lambda x: pattern in str(x)), hits)
        return self.df.loc[hits].copy()
