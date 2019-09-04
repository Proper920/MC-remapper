import os, json, urllib.request

def main():
    version = get_version()
    get_mappings(version)
    reformat_mappings(version)

def get_version():
    with open('version.config') as f:
        config = f.readlines()[0]
        return config.split('=')[-1].strip()

def get_mappings(version):
    jdir = os.getenv('APPDATA') + f'\\.minecraft\\versions\\{version}\\{version}.json'

    if os.path.exists(jdir) and  os.path.isfile(jdir):
        print(f'Found {version}.json')
        return

    with open(jdir) as f:
        jfile = json.load(f)
        url = jfile['downloads']['client_mappings']['url']

        print(f'Downloading the mappings for {version}...')
        download_file(url, 'mappings/client.txt')
        print('Done!')

def download_file(url, out):
    urllib.request.urlretrieve(url, out)

def reformat_mappings(version):
    out = []
    with open(f'mappings/{version}.mojang_mappings') as f:

        current_class = None

        for line in f.readlines():
            if line.startswith('#'): continue
            
            elif line.startswith('    '):
                if '(' in line:  new_line = parse_method(line, current_class)
                else:            new_line = parse_field(line, current_class)
            else: current_class, new_line = parse_class(line)
            out.append(new_line)
    
    with open(f'mappings/{version}.tiny', 'w') as f:
        f.write('\n'.join(out))


def parse_class(line):
    #com.mojang.blaze3d.Blaze3D -> cve:
    #CLASS	a	net/minecraft/class_1158

    deobf_name, obf_name = line.split(' -> ')
    obf_name = obf_name[:-2]
    return obf_name, f'CLASS\t{obf_name}\t{deobf_name}'

def parse_field(line, current_class):
    #    int source -> b
    #FIELD	co	Ljava/util/Collection;	b	field_9871

    fieldtype, deobf_name, _, obf_name = line.strip().split(' ')
    fieldtype = parse_type(fieldtype)

    return f'FIELD\t{current_class}\t{fieldtype}\t{obf_name}\t{deobf_name}'

def parse_method(line, current_class):
    #    852:865:void teleport(double,double,double,float,float,java.util.Set) -> a
    #METHOD	wc	(DDDFFLjava/util/Set;)V	a	method_14360

    returntype, temp, _, obf_name = line.strip().split(' ')
    
    deobf_name, temp = temp.split('(')

    params = ''
    for param in temp[:-1].split(','): params += parse_type(param)
    
    returntype = parse_type(returntype.split(':')[-1])

    return f'METHOD\t{current_class}\t({params}){returntype}\t{obf_name}\t{deobf_name}'

def parse_type(string):
    if string == '': return ''
    mapp = {
        'byte':'B',
        'char':'C',
        'double':'D',
        'float':'F',
        'int':'I',
        'long':'J',
        'short':'S',
        'boolean':'Z',
        'void':'V'
    }
    
    out = ''

    for x in range(string.count('[')): out += '['
    
    string = string.replace('[]','')

    if string in mapp: out += mapp[string]
    else: out += f'L{string};'
    
    return out

    


if __name__ == "__main__": main()