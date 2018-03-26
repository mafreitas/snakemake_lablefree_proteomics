import glob
keep = True
with open('benchmarks.txt','w') as outfile:

    for filename in glob.iglob('./**/*.benchmark.txt', recursive=True):
 
        print(filename)
        
        with open(filename, 'r') as infile:
            
            for line in infile:
                if "h:m:s" in line and keep == False:
                    continue
                
                keep = False
                if line.strip(): 
                    outfile.write(filename+"\t"+line)
