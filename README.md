# Use Claude to curate Species sightings list

This script takes a file with species-level sightings, a user-supplied area of sampling such as "Cocos-Keeling Islands" or "South-Western Western Australia", and asks Claude whether the species found are expected in the area. We use these predictions as a data-point in curation of eDNA results, along with AquaMaps probabilities, OBIS sightings, and other external data-points.

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

A csv that looks like this:

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

Species identified by Claude to not be from the area have their close relatives listed - from there we go and check whether they are in the reference database we use (they are usually not).

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


# API usage

The example file contains 224 unique species.

According to the Anthropic log, a run of the curate.py script uses 12,918 input tokens and 8,939 output tokens. At the time of this writing that cost US $0.17.

# How accurate is this?

Here are results from a preliminary analysis with 12S_Miya/16S_Berry eDNA samples from around South-Western Western Australia. For each sample latitude/longitude and 'species' sighting, we pulled out the Aquamaps probability for that location and species. 

Here's a plot comparing Claude's TRUE/FALSE (TRUE = expected in the area, FALSE = not expected) with AquaMaps probabilities. Each dot is one species sighting in South-Western Western Australia, comparing that species' AquaMaps score for a SWWA latitude/longitude, and whteher Claude thinks it's in the area (TRUE) or not (FALSE).

![image](https://github.com/user-attachments/assets/64568307-0862-4c40-a4a6-934e3f7eb244)

As you can see, the average/median Aquamaps probability for sightings for which Claude says they are unlikely is 0, not likely for this area. The median for Claude's agreed-upon sightings for 16S is 0.76. You can see some 'leftovers' where Claude disagrees with Aquamaps, i.e., Claude says FALSE but AquaMaps has a probability above 0.8. These are *Pseudophycis breviuscula*, *Repomucenus calcaratus*, *Zebrias scalaris*, *Anoplogaster cornuta*, *Parapriacanthus elongatus*, *Caprodon schlegelii*, and *Lampadena speculigera*. Some of these, like *Lampadena speculigera*, are deep sea fish, but these are not impossible species. I expect that these species appear less frequently in Claude's training data. There's always room for improvement via fine-tuning!

We can also look at this from a higher level - we asked Fishbase whether these species are endemic/native or not to Australia (not just South-Western Australia).

![image](https://github.com/user-attachments/assets/e1dbffda-01b6-481a-ae86-7eaefe059509)

Here, 66% and 64% of the non-endemic species in 12S and 16S are labeled as FALSE by Claude. About 22% of endemic species are labeled as FALSE by Claude, but Claude evaluates on the area (South-Western Western Australia), not all of Australia. 

So far it has a 100% success rate with finding *very* wrong species, i.e., European freshwater fish in Australian marine samples. But you don't need 500 GPUs and Liechtenstein's energy consumption to tell you that.

# CAVEATS

- This is an LLM, **it lies**. It's hard to tell when it lies because it does not know when it lies. Always use other data sources for curation - never trust the system blindly.
- The list of alternative species is far shorter than it should be; lots of missing species. Sometimes it reports more, sometimes it reports fewer species when you rerun it. On average it reports two to three species.
- Rerunning can be a good idea - answers outside of the `In area?` question are somewhat random.
- The model "claude-3-5-sonnet-20240620" is hard-coded, have not really evaluated others. Some preliminary tests with Opus led to mostly identical results.
- Sometimes what the API returns is truncated. The script tries to detect these cases and should print something like "Warning: Response for species a, b, c might be truncated", but there is no guarantee that this works correctly.
- Once in a while, the csv line is broken. Here's an example: *"Vinciguerria lucetia",FALSE,"Found in tropical and subtropical waters of the Atlantic, Pacific, and Indian Oceans, but not typically near Australia","This species is a bioluminescent fish, often called the Panama lightfish",Vinciguerria nimbaria,Vinciguerria poweriae,Vinciguerria attenuata,Ichthyococcus ovatus,Pollichthys mauli"*. Can you see the missing " in front of Vinciguerria? That has to be added manually.
- Very little work has gone into optimising token usage. For starters, there is no prompt caching.
- Claude is instructed to return 'NA' when it is unsure whether a species is supposed to be present in an area. I have not seen it do that yet - 100% of my cases return TRUE or FALSE so far.
