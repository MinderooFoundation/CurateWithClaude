# Use Claude to curate Species sightings list

This script takes a file with species-level sightings as produced by the OceanOmics amplicon pipeline, a user-supplied area of sampling such as "Cocos-Keeling Islands" or "South-Western Western Australia", and asks Claude whether the species found are expected in the area. Useful as a data-point in curation of eDNA results.

# Installation

This script depends on a fairly recent Python and the anthropic Python package.

There's a prepared conda environment:

```bash
conda env create -f anthropic.yml
```

IMPORTANT: You need a .env file in the working directory with your Anthropic API key. It should look like this:

```bash
ANTHROPIC_API_KEY=blablabla
```

# Usage

-i for the input file,  
-o for the output file,  
-a for the area,  
--prompt (optional) for the output file that will contain the prompt with all species sent to Claude.  

```bash
python curate.py -i asv_final_taxa_filtered.tsv \
	-o asv_final_taxa_claude.csv \
	-a 'South-Western Western Australia' \
	--prompt prompt_out.txt
```

# Input

A tsv of species sightings produced by the OceanOmics amplicon pipeline, example in `asv_final_taxa_filtered.tsv`

```
"ASV"   "domain"        "phylum"        "class" "order" "family"        "genus" "species"       "LCA"   "numberOfUnq_BlastHits" "X.ID"  "Gene"  "Genus.prediction"        "Genus.score"   "Species.prediction"    "Species.score" "ASV_sequence"
"1"     "ASV_10"        "Eukaryota"     "Chordata"      "Actinopteri"   "Syngnathiformes"       "Mullidae"      "Upeneichthys"  "Upeneichthys lineatus"   "Upeneichthys lineatus" 1461    98.824  NA      NA      NA      NA      NA      "TTCCCTAGCTTTCGTGGGTTCGGGATAAGTAAAGCCACTTTCGTGGTGGGGCTTCATATCTTCGAGAACGTATAACAGCTTTGAAGACGTTCGGCTTTACTAGAATAATACTCCGTAACCACCCTTTACGCCGGTGCCTATCAACTTGGGCCCCTCGTATAACCGCGGTG"
"2"     "ASV_11"        "Eukaryota"     "Chordata"      "Actinopteri"   "Cypriniformes" "Cyprinidae"    "Alburnus"      "Alburnus alburnus"     "Alburnus alburnus"       1461    98.824  NA      NA      NA      NA      NA      "TTCCCTAGCTTTCGTGGGTTCGGGATAAGTAAAGCCACTTTCGTGGTGGGGCTTCATATCTTCGAGAACGTATAACAGCTTTGAAGACGTTCGGCTTTACTAGAATAATACTCCGTAACCACCCTTTACGCCGGTGCCTATCAACTTGGGCCCCTCGTATAACCGCGGTG"
```

# Output

A csv (produced by Claude so can be buggy!) that looks like this, I added the header manually:

| Species | In area? | Where else? | Fun fact | Other species |
| --- | --- | --- | --- | --- |
| Upeneichthys lineatus | TRUE | NA | Known as the blue-lined goatfish, this species is endemic to southern Australia and an important catch in some local fisheries | NA |
| Alburnus alburnus | FALSE | This freshwater fish species is native to Europe and western Asia | Commonly known as the bleak, it's an important bait fish in Europe | Nematalosa come, Nematalosa erebi, Hyperlophus vittatus, Spratelloides robustus, Sardinops sagax, Etrumeus teres, Engraulis australis |

The raw output contains no header.

Raw:

```
"Upeneichthys lineatus",TRUE,NA,"Known as the blue-lined goatfish, this species is endemic to southern Australia and an important catch in some local fisheries",NA
"Alburnus alburnus",FALSE,"This freshwater fish species is native to Europe and western Asia","Commonly known as the bleak, it's an important bait fish in Europe","Nematalosa come, Nematalosa erebi, Hyperlophus vittatus, Spratelloides robustus, Sardinops sagax, Etrumeus teres, Engraulis australis"
```

The columns are:
	1. The supplied species,
	2. TRUE if Claude thinks it's in the area and FALSE if not,
	3. If the species is not in the area, some explanation, otherwise NA
	4. A 'fun fact' about the species 
	5. if the species is not in the area, a list of alternative closely related species that could be, otherwise NA

# CAVEATS

- This is an LLM, it lies. It's hard to tell when it lies.  
- The list of alternative species is far shorter than it should be; lots of missing species.
- The model "claude-3-5-sonnet-20240620" is hard-coded, have not really evaluated others. Some preliminary tests with Opus led to mostly identical results.
