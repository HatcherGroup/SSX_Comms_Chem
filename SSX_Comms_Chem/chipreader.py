import argparse
import os
import sys
import time
import json
import csv

##### argparse commandline input #####

parser = argparse.ArgumentParser(description="i19 serial chip loading assessment")
parser.add_argument('-aI', '--autoIndex', action='store', dest='autoIndex', type=str, required=True, help='Run script in autoindexing mode? (Y / N)')
parser.add_argument('-uc','--unitCell', action='store', dest='unitCell', type=str, nargs='*', help='Optional: unit cell info for xia2 processing e.g. -uc 5.6,10.5,13.4,90,92.4,90')
parser.add_argument('-im','--instrumentModel', action='store', dest='instrumentModel', type=str, help='Optional: instrument model for xia2 processing e.g. -im IM.expt')
parser.add_argument('-dN', '--dataName', action='store', dest='dataName', type=str, required=True, help='data output file name in visit directory')
parser.add_argument('-sG', '--spaceGroup', action='store', dest='spaceGroup', type=str, help='space group of system (if known)')
parser.add_argument('-tW', '--totalWells', action='store', dest='totalWells', type=int, help='total number of wells in the grid (default: 400)')
parser.add_argument('-tF', '--totalFrames', action='store', dest='totalFrames', type=int, help='total number of frames taken per well (default: 50)')

args = parser.parse_args()
if args.autoIndex == Y or args.autoIndex == N:
	autoIndex = args.autoIndex
else:
	print("Invalid user input: Autoindexing selection must be either 'Y' or 'N', aborting script...")
	sys.exit()

if args.unitCell:
	pass
else:
	args.unitCell = "6.2,11.9,15.6,90,90,90"
	print(f"No user defined unit cell, using default: {args.unitCell}")
if args.spaceGroup:
	pass
else:
	args.spaceGroup = "Pnnm"
	print(f"No user defined space group, using default: {args.spaceGroup}")

if args.instrumentModel:
	pass
else:
	args.instrumentModel = f"{'/'.join(os.getcwd().split('/')[0:8])}/resources/IM.expt"
	print(f"No user defined instrument model, using {args.instrumentModel}")

if args.totalWells:
	totalWells = args.totalWells
else:
	totalWells = 400

if args.totalFrames:
	totalFrames = args.totalFrames
else:
	totalFrames = 50

############### classes ###############
	
class wellclass: # a class to hold information about the wells
	def __init__(self, wellnum, jobnum, solved, loadstatus, highreslimit, lowreslimit, completeness, multiplicity, isigma, Rmerge, Rmeas, Rpim, a_length, b_length, c_length, alpha, beta, gamma, cchalf, totalobs, totalunique, numindexed, numunindexed, percentindexed, spotsextracted, l3spotsremoved, g1Kspotsremoved, crystalsystem, spacegroup):
		self.wellnum = wellnum		
		self.jobnum = jobnum
		self.solved = solved		
		self.loadstatus = loadstatus
		self.highreslimit = highreslimit
		self.lowreslimit = lowreslimit
		self.completeness = completeness
		self.multiplicity = multiplicity
		self.isigma = isigma
		self.Rmerge = Rmerge
		self.Rmeas = Rmeas
		self.Rpim = Rpim
		self.a_length = a_length
		self.b_length = b_length
		self.c_length = c_length
		self.alpha = alpha
		self.beta = beta
		self.gamma = gamma
		self.cchalf = cchalf 
		self.totalobs = totalobs
		self.totalunique = totalunique
		self.numindexed = numindexed
		self.numunindexed = numunindexed
		self.percentindexed = percentindexed
		self.spotsextracted = spotsextracted
		self.l3spotsremoved = l3spotsremoved
		self.g1Kspotsremoved = g1Kspotsremoved
		self.crystalsystem = crystalsystem
		self.spacegroup = spacegroup
		
	def __str__(self):
		return f"{self.wellnum}(job number: {self.jobnum}, solved status: {self.solved}, load status: {self.loadstatus}, load status: {self.highreslimit}, low res limit: {self.lowreslimit}, completeness: {self.completeness}, multiplicity: {self.multiplicity}, I/sigma: {self.isigma}, Rmeas: {self.Rmeas}, Rpim: {self.Rpim}, a: {self.a_length}, b: {self.b_length}, c: {self.c_length}, alpha: {self.alpha}, beta: {self.beta}, gamma: {self.gamma} CChalf: {self.cchalf}, total observation: {self.totalobs}, total unique observations: {self.totalunique}, num indexed: {self.numindexed}, num unindexed: {self.numunindexed}, % indexed: {self.percentindexed}, num spots extracted: {self.spotsextracted}, <3 pixel spots removed: {self.l3spotsremoved}, >1000 spots removed: {self.g1Kspotsremoved}, crystal system: {self.crystalsystem}, space group: {self.spacegroup})"

############# functions ###############

def dataLocation(dataName): # produces a string with the cwd location of the dataset to be used, and checks whether the location exists
	current_directory = str(os.getcwd()).split('/')[1:6]
	data_location = '/' + '/'.join(current_directory) + '/' + dataName + '/'	
	if os.path.isdir(data_location) == True:
		print(f'Data directory {data_location} exists, moving on with script...')
	else:
		print(f'Data directory {data_location} does not exist! Aborting script...')
		sys.exit()
	return(data_location)

def wellsSearcher(data_location, wellclass, totalFrames, autoIndex): # searches for the number of wells in the data collection folder and returns a list, and also finds the prefix for the dataset
	classcounter = []
	wellcounter = []
	prefix = ""
	well_counter = 0
	current_directory = os.getcwd()
	visit_directory = "/"+"/".join(str(os.getcwd()).split('/')[1:6])

	print(f"Monitoring the {args.dataName} folder for data on wells, and will submit when the specified number of frames have been collected...")
	while well_counter < totalWells:
		for cbf in sorted(os.listdir(data_location)): # iterate through the number of files in the set data location
			if prefix == "" and cbf.endswith(".cbf"): # output the prefix of the dataset
				prefix = cbf[:-14]
				os.mkdir(f"{os.getcwd()}/datasets")
				print("Generated folder for well dataset processing...")
			if cbf.endswith(".cbf"): # generate a list of objects of the wells, setting the object values to zero for now. 
				if int(cbf[-13:-10]) in wellcounter:
					pass
				elif int(cbf[-13:-10]) not in wellcounter and str(totalFrames) in cbf[-9:-4]:
					wellcounter.append(int(cbf[-13:-10]))
					classcounter.append(wellclass(cbf[-13:-10], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
					try:
						os.mkdir(f"{os.getcwd()}/datasets/{classcounter[well_counter].wellnum}")
						print(f"Made folder for {classcounter[well_counter].wellnum}, moving on...")
					except:
						print(f"Could not make folder for {classcounter[well_counter].wellnum} as folder already exists, aborting...")
						sys.exit()

					xia2directory = f"{working_location}/datasets/{classcounter[well_counter].wellnum}/xia2/"
					os.mkdir(xia2directory)
				
					if autoIndex == 'Y':

						xia2input = ["xia2 ",   #xia2 command, variables can be changed here if necessary
				   		     "small_molecule=true ",
				        	     "resolution_range=999,15 ",
				        	     "trust_beam_centre=true ",
				        	     "read_all_image_headers=False ",
				        	     "absorption_level=medium ",
				        	     "method=fft3d ",
						     "keep_all_reflections=False ",
				 		     "cc_half=none ",
						     "isigma=2 ",
						     "integrate.min_spots.overall=10 ",
						     "integrate.min_spots.per_degree=0 ",
						     "failover=True ",
						     "remove_blanks=True ",
						     f"reference_geometry={args.instrumentModel} ",
						     f"image={visit_directory}/{args.dataName}/{prefix}_{classcounter[well_counter].wellnum}_00001.cbf:1:{totalFrames}"]

					elif autoIndex == 'N':

						xia2input = ["xia2 ",   #xia2 command, variables can be changed here if necessary
				   		     "small_molecule=true ",
				        	     "resolution_range=999,15 ",
				        	     "trust_beam_centre=true ",
				        	     "read_all_image_headers=False ",
				        	     "absorption_level=medium ",
				        	     "method=real_space_grid_search ",
						     "keep_all_reflections=False ",
				 		     "cc_half=none ",
						     "isigma=2 ",
						     "integrate.min_spots.overall=10 ",
						     "integrate.min_spots.per_degree=0 ",
						     "failover=True ",
						     "remove_blanks=True ",
						     f"unit_cell={unitCell} ",
						     f"space_group={spaceGroup} ",
						     f"reference_geometry={args.instrumentModel} ",
						     f"image={visit_directory}/{args.dataName}/{prefix}_{classcounter[well_counter].wellnum}_00001.cbf:1:{totalFrames}"]
	
					bashinput = ["#!/bin/bash", #a list in which each item is a separate line to be printed into the bash file 
			        	      "#SBATCH --nodes=1",
			        	      "#SBATCH --cpus-per-task=20",
			        	      "#SBATCH --time=04:00:00",
			        	      f"#SBATCH --error=j_{classcounter[well_counter].wellnum}.err",
			        	      f"#SBATCH --output=j_{classcounter[well_counter].wellnum}.out",
			        	      "#SBATCH -p cs05r",
					      "#############################",
					      "module load xia2",
					      "module load dials/nightly",
					      f"{''.join(xia2input)}"]					

					f = open(f"{os.getcwd()}/datasets/{classcounter[well_counter].wellnum}/xia2/j_{classcounter[well_counter].wellnum}.sh", "x") # write bash script
					for x in bashinput:
						f.write(f"{x}\n")
					f.close()
					
					os.chdir(f"{os.getcwd()}/datasets/{classcounter[well_counter].wellnum}/xia2") # change directory to then execute the job submission to wilson
					bashsubmit = os.popen(f"sbatch j_{classcounter[well_counter].wellnum}.sh")
					classcounter[well_counter].jobnum = str(''.join(bashsubmit.read().split(" ")[-1:])).strip('\n')
					print(f"Successfully submitted j_{classcounter[well_counter].wellnum}.sh with job number {classcounter[well_counter].jobnum} to the cluster...")
					os.chdir(current_directory)
					well_counter += 1
					print(f"Current well collection progress: {well_counter} / {totalWells}")
					time.sleep(0.1)			
					if well_counter == totalWells:	
						break
	return(classcounter, prefix)

def clusterChecker(classcounter): # monitor the cluster and allow script to continue when no further jobs are running
	xia2check = True

	while xia2check == True: # monitor whether jobs are still running on wilson, keep looping until no jobs are there...
		wilsoncheck = str(os.popen("squeue --me").read())
		xia2check = False
		for xia2checkcounter in classcounter:
			if str(xia2checkcounter.jobnum) in wilsoncheck and int(xia2checkcounter.jobnum) != 0:
				xia2check = True
			else:
				pass
		if xia2check == True:
			print("xia2 jobs still running, sleeping for 10 seconds and will then check again...")
			time.sleep(10)
		else:
			print("no xia2 job running, continuing with script...")

def classFiller(classcounter): # fill the classes with information depending on the output from xia2 for that well
	solvedstructures = 0
	for xia2outputcheck in range(len(classcounter)): # after jobs have finished running check for the status of the wells, import useful information
		outfilelocation = f"{working_location}/datasets/{classcounter[xia2outputcheck].wellnum}/xia2/j_{classcounter[xia2outputcheck].wellnum}.out"
		outfiledata = str(os.popen(f"tail -10 {outfilelocation}").read())
		if classcounter[xia2outputcheck].jobnum != 0:
			if "Status: normal termination" in outfiledata:
				classcounter[xia2outputcheck].solved = True
				classcounter[xia2outputcheck].loadstatus = "solvable"
				classcounter[xia2outputcheck] = wellInfoExtractor(classcounter, outfilelocation, xia2outputcheck) #function wellInfoExtractor will fill the class objects with info if solved
				solvedstructures = solvedstructures + 1
			elif "No spots found in sweep SWEEP1" in outfiledata:
				classcounter[xia2outputcheck].solved = False
				classcounter[xia2outputcheck].loadstatus = "empty   "
			elif "No suitable indexing solution could be found" in outfiledata:
				classcounter[xia2outputcheck].solved = False
				classcounter[xia2outputcheck].loadstatus = "no solve"

	percentstructures = float("{:.2f}".format(solvedstructures/len(classcounter))) # calculate the percentage of wells with usable structures...
	print(f"the number of wells with solvable structures are: {solvedstructures} ({percentstructures*100}% of wells analysed)")
	return(classcounter)

def wellInfoExtractor(classcounter, outfilelocation, xia2outputcheck): #yoink the data from the xia2 outputs to fill the well classes
	xia2data = open(outfilelocation, "r")
	lines = [line.rstrip() for line in xia2data] 

	for x in range(len(lines)):
		if lines[x].startswith("High resolution limit"):
			classcounter[xia2outputcheck].highreslimit = lines[x].split()[3]
		elif lines[x].startswith("Low resolution limit"):
			classcounter[xia2outputcheck].lowreslimit = lines[x].split()[3]
		elif lines[x].startswith("Completeness"):
			classcounter[xia2outputcheck].completeness = lines[x].split()[1]
		elif lines[x].startswith("Multiplicity"):
			classcounter[xia2outputcheck].multiplicity = lines[x].split()[1]
		elif lines[x].startswith("I/sigma"):
			classcounter[xia2outputcheck].isigma = lines[x].split()[1]
		elif lines[x].startswith("Rmerge(I)"):
			classcounter[xia2outputcheck].Rmerge = lines[x].split()[1]
		elif lines[x].startswith("Rmeas(I)"):
			classcounter[xia2outputcheck].Rmeas = lines[x].split()[1]
		elif lines[x].startswith("Rpim(I)"):
			classcounter[xia2outputcheck].Rpim = lines[x].split()[1]
		elif lines[x].startswith("CC half"):
			classcounter[xia2outputcheck].cchalf = lines[x].split()[2]
		elif lines[x].startswith("Total observations"):
			classcounter[xia2outputcheck].totalobs = lines[x].split()[2]
		elif lines[x].startswith("Total unique"):
			classcounter[xia2outputcheck].totalunique = lines[x].split()[2]
		elif lines[x].startswith("Unit cell (with estimated std devs):"):
			classcounter[xia2outputcheck].a_length = lines[x+1].split()[0]
			classcounter[xia2outputcheck].b_length = lines[x+1].split()[1]
			classcounter[xia2outputcheck].c_length = lines[x+1].split()[2]
			classcounter[xia2outputcheck].alpha = lines[x+2].split()[0]
			classcounter[xia2outputcheck].beta = lines[x+2].split()[1]
			classcounter[xia2outputcheck].gamma = lines[x+2].split()[2]
		elif lines[x].startswith("Indexing solution:"):
			classcounter[xia2outputcheck].crystalsystem = lines[x+1].split()[0]
		elif lines[x].startswith("Assuming spacegroup:"):
			classcounter[xia2outputcheck].spacegroup = lines[x][21:]

	return(classcounter[xia2outputcheck])

def wellIndexExtractor(classcounter): # a function to retrieve the indexing information output by DIALS when called by xia2
	print("Extracting information regarding indexing to well class objects from xia2 outputs...")
	for x in range(len(classcounter)):
		if classcounter[x].loadstatus == "solvable" and classcounter[x].solved == True:
			indexdata = open(f"{working_location}/datasets/{classcounter[x].wellnum}/xia2/DEFAULT/NATIVE/SWEEP1/index/4_dials.index.log", "r")
			indexlines = [line.rstrip() for line in indexdata]
			classcounter[x].numindexed = indexlines[-10].split()[3]
			classcounter[x].numunindexed = indexlines[-10].split()[5]
			classcounter[x].percentindexed = (indexlines[-10].split()[7])[:-1]
		indexdata = open(f"{working_location}/datasets/{classcounter[x].wellnum}/xia2/DEFAULT/NATIVE/SWEEP1/index/2_dials.find_spots.log", "r")
		indexlines = [line.rstrip() for line in indexdata]
		for y in range(len(indexlines)):
			if indexlines[y].startswith("Extracted"):
				classcounter[x].spotsextracted = indexlines[y].split()[1]
			elif "spots with size < 3 pixels" in indexlines[y]:
				classcounter[x].l3spotsremoved = indexlines[y].split()[1]
			elif "spots with size > 1000 pixels" in indexlines[y]:
				classcounter[x].g1Kspotsremoved = indexlines[y].split()[1]	
	print("Completed extraction of well class object indexing information...")	
	return(classcounter)

def JSONmaker(classcounter, prefix): # a function which will generate a JSON file containing the class objects containing the information about each well.
	try:
		print(f"Attempting to write class objects in JSON format to {prefix}_JSON.txt...") 
		f = open(f"{working_location}/{prefix}_JSON.txt", "x") #the writing of the JSON file
	
		for x in range(len(classcounter)):
			f.write(f"{json.dumps(classcounter[x].__dict__)}\n")
		f.close()
	except:
		print(f"Could not generate the {prefix}_JSON.txt...")	

def statsFileMaker(classcounter, outputdatalocation): # generate a text file containing the xia2 output information for all wells
	print("Generating .csv file with well data stripped from xia2 outputs") 
	with open(outputdatalocation, "w", newline='') as csv_file:
		writer = csv.writer(csv_file)
		field = ["wellnum", "jobnum", "solved", "loadstatus", "highreslimit", "lowreslimit", "completeness", "multiplicity", "isigma", "Rmerge", "Rmeas", "Rpim", "a_length", "b_length", "c_length", "alpha", "beta", "gamma", "cchalf", "totalobs", "totalunique", "numindexed", "numunindexed", "percentindexed", "spotsextracted", "l3spotsremoved", "g1Kspotsremoved", "crystal_system", "space_group"]
		writer.writerow(field)
		for x in range(len(classcounter)):
			writer.writerow([classcounter[x].wellnum, classcounter[x].jobnum, classcounter[x].solved, classcounter[x].loadstatus, classcounter[x].highreslimit, classcounter[x].lowreslimit, classcounter[x].completeness, classcounter[x].multiplicity, classcounter[x].isigma, classcounter[x].Rmerge, classcounter[x].Rmeas, classcounter[x].Rpim, classcounter[x].a_length, classcounter[x].b_length, classcounter[x].c_length, classcounter[x].alpha, classcounter[x].beta, classcounter[x].gamma, classcounter[x].cchalf, classcounter[x].totalobs, classcounter[x].totalunique, classcounter[x].numindexed, classcounter[x].numunindexed, classcounter[x].percentindexed, classcounter[x].spotsextracted, classcounter[x].l3spotsremoved, classcounter[x].g1Kspotsremoved, classcounter[x].crystalsystem, classcounter[x].spacegroup])
	print(f"Output file with well statistics created at {working_location}/{prefix}_outputs.csv") 

############ code execution #############

data_location = dataLocation(args.dataName)

working_location = os.getcwd()

os.chdir(working_location)

classcounter, prefix = wellsSearcher(data_location, wellclass, totalFrames, autoIndex)

clusterChecker(classcounter)

classcounter = classFiller(classcounter)
		
outputdatalocation = str(f"{working_location}/{prefix}_outputs.csv")

classcounter = wellIndexExtractor(classcounter)

JSONmaker(classcounter, prefix)

statsFileMaker(classcounter, outputdatalocation) # produce stats file output









