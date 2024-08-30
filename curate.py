import anthropic
from argparse import ArgumentParser
from dotenv import load_dotenv
load_dotenv()

parser = ArgumentParser()
parser.add_argument('-i', '--input', help = 'Name of the input file', required = True)
parser.add_argument('-o', '--output', help = 'Name of the output file', required = True)
parser.add_argument('-a', '--area', help = 'Name of the area the sightings were made in. Example: South-Western Western Australia', required = True)
parser.add_argument('--prompt', help = 'Optional: name of the file to to which we write the final prompt', required = False)
args = parser.parse_args()
area = args.area

client = anthropic.Anthropic()

system_message = f"""You are an expert in marine species distributions. You're the world's best. You're so accurate. wow.
Please evaluate the following list of species sightings for accuracy. These were all spotted in {area} in a marine environment using DNA sequencing of water samples. Do these species usually occur in this environment?
In the first column, list the species.
In the second column, list whether this species is commonly found in {area} using a TRUE or a FALSE when it's not found.
In the third column, in cases when this species is not found in {area}, describe where else it appears. If the species is OK, use NA.
Note anything of interest in the fourth column that a human reader might find interesting. Don't focus only on common names; note cultural interest, threatened status, venomous nature, or anything else fun or interesting.
In a fifth column, for species that don't occur in the sampled environment, note all other closely related species (same genus or family based on DNA) which may be in the area. List them all, even if there are hundreds.
Provide the summary in CSV format without a header. Do not preamble.
Enclose your entire response in <evaluation> tags.
Example output format:
"Acanthurus sp.",TRUE,"Only on genus level but is in marine South-western Western Australia","A very common marine genus",NA
"Aurelia miyakei",FALSE,"This moon jellyfish species was initially described from Japan, and its presence in Western Australia would be unusual","Just recently described (2021)","Aurelia aurita has been found in Australian waters"
"Omegophora armilla",TRUE,"Valid for this area","Poisonous to consume",NA"
"Pseudocalliurichthys variegatus",FALSE,"The species is found in Japan and China, not Western Australia","Type of dragonet fish","Callioymus goodladi, Pseudocalliurichthys goodladi, Repomucenus filamentosus"
"""

def guided_species_evaluation(text, area, args, prompt_out, model="claude-3-5-sonnet-20240620", max_tokens=4096):
#def guided_species_evaluation(text, model="claude-3-opus-20240229", max_tokens=4096):

    prompt = f"""
    Species list:
    {text}
    """
    if args.prompt:
        prompt_out.write(prompt)

    full_response = ''
    with client.messages.stream(
        model = model,
        max_tokens = max_tokens,
        system = system_message,
        messages = [
            {
                "role": "user", 
                "content": prompt
            },
            {
                "role": "assistant",
                "content": "Here is an evaluation of the species list: <evaluation>"
            }
        ] ) as stream:
            for text in stream.text_stream:
                full_response += text

    if not full_response.endswith("</evaluation>"):
        species_list = ', '.join(text.split('\n'))
        print("Warning: Response for species {species_list} might be truncated")
    else:
        full_response = full_response.replace('</evaluation>', '')
        full_response = full_response.replace('<evaluation>', '')
    return full_response

specs = list()
with open(args.input) as fh:
    for line in fh:
        ll = line.split('\t')
        spec = ll[8].replace('"', '')
        if spec == 'dropped' or spec == "NA" or spec == '' or spec == 'LCA':
            continue
        if spec not in specs:
            specs.append(spec)

prompt_out = ''
if args.prompt:
    prompt_out = open(args.prompt, 'w')
    prompt_out.write('System message:\n')
    prompt_out.write(system_message)
    prompt_out.write('\n')

with open(args.output, 'w') as out:
    iterator = zip(*(iter(specs),) * 10)
    if len(specs) < 10:
        iterator = [specs]

    for sliced_text in iterator:
        text = '\n'.join(sliced_text)
        returned_text = guided_species_evaluation(text, args.area, args, prompt_out)
        # extra linebreaks, remove
        returned_text = '\n'.join([x for x in returned_text.split('\n') if len(x) > 0])
        out.write(returned_text)
