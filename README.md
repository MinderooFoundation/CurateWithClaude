# Use Claude to curate Species sightings list

This script takes a file with species-level sightings as produced by the OceanOmics amplicon pipeline, a user-supplied area of sampling such as "Cocos-Keeling Islands" or "South-Western Western Australia", and asks Claude whether the species found are expected in the area. Useful as a data-point in curation of eDNA results.

# Installation

This script depends on a fairly recent Python and the anthropic Python package.

There's a prepared conda environment in `anthropic.yml` that you can use to get conda to install everything:

```bash
conda env create -f anthropic.yml
```

You need a .env file in the working directory with your Anthropic API key. It should look like this:

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

The input is a flat text file of species names (or family names or whatever taxonomic unit).

Looks like this, the example is in `for_claude.txt`:

```
Upeneichthys lineatus
Trachinops noarlungae
Parapercis ramsayi
Bathytoshia brevicaudata
Heteroscarus acroptilus
Olisthops cyanomelas
Leviprora inops
Sphyraena novaehollandiae
Lophonectes gallus
Gymnothorax prasinus
Siphonognathus argyrophanes
Sheardichthys radiatus
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

There is example output in `claude_commented.csv`.

# API usage

The example file contains 224 unique species.

According to the Anthropic log, a run of the curate.py script uses 12,918 input tokens and 8,939 output tokens. At the time of this writing that cost US $0.17.

# CAVEATS

- This is an LLM, it lies. It's hard to tell when it lies.  
- The list of alternative species is far shorter than it should be; lots of missing species. Sometimes it reports more, sometimes it reports fewer species when you rerun it.
- Rerunning can be a good idea - answers are somewhat random.
- The model "claude-3-5-sonnet-20240620" is hard-coded, have not really evaluated others. Some preliminary tests with Opus led to mostly identical results.
- Sometimes what the API returns is truncated. The script tries to detect these cases and should print something like "Warning: Response for species a, b, c might be truncated", but there is no guarantee that this works correctly.
- Once in a while, the csv line is broken. Here's an example: *"Vinciguerria lucetia",FALSE,"Found in tropical and subtropical waters of the Atlantic, Pacific, and Indian Oceans, but not typically near Australia","This species is a bioluminescent fish, often called the Panama lightfish",Vinciguerria nimbaria,Vinciguerria poweriae,Vinciguerria attenuata,Ichthyococcus ovatus,Pollichthys mauli"*. Can you see the missing " in front of Vinciguerria? That has to be added manually.
- Very little work has gone into optimising token usage. There is no prompt caching.
