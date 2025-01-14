# %load Genome.py
from Bio import SeqIO
import sys, numpy, math, datetime
import CommonFunctions
from CommonFunctions import WriteArrayinFile
from operator import itemgetter
from collections import Counter

class Genome:
    DNAList= []
    DNA_current = []
    ReadLength_Considered = 100
    Filename    = ""
    SideLengths = 1
    Gap         = 1
    RepeatPositions = []
    """
        Basic Initialization
    """
    def __init__(self, Filename, Gap):
        self.Gap = Gap
        self.Filename = Filename
        Handle = open(Filename)
        for seq_record in SeqIO.parse(Handle, "fasta"):
            self.DNAList.append(str(seq_record.seq))
        print( "Length of the DNA is", len(self.DNAList[0]))
    
    """
        Implements log(n!)
    """
    def factlog(self,n):
        if n<20:
            return(math.log(math.factorial(n), 2))
        else:
            return( n*(math.log(n,2) - 1.44269) + 0.5*math.log(2*math.pi*n)) #math.log(math.e,2) = 1.4426950408889634
    
    def getReadLengthGraph(self):
     #Stores final data
        Summary = []
        self.DNA_current = self.DNAList[0]
        Start_length = 0
        End_length = 40000
        self.RepeatPositions = range(self.SideLengths, len(self.DNA_current) - Start_length - self.SideLengths )
        for length in range(Start_length,End_length):
            length += self.Gap
            Answer = self.NumberofRepeatsofLengthL(length) 
            if False == Answer[3]:
                break  
            print("Length", length, "Answer", Answer)
            Summary += [ Answer ]
        CommonFunctions.WriteArrayinFile(Summary, "RepeatStructure"+self.Filename[:-6]+".csv")
           
    def NumberofRepeatsofLengthL(self, length):
        #print("DNA Length", len(self.DNA_current))
        Reads = []
        Repeat_Positions = []
        for position in self.RepeatPositions:
            Reads +=[   
                        [ 
                         self.DNA_current[position - 1: position] , #Left Neighbhour
                         self.DNA_current[position: position + length] ,
                         self.DNA_current[position + length : position + length + 1],#Right Neigbhour
                         position
                        ]
                    ]
        #print("Sorting Read Array")
        # Sort w.r.t to the reads. (aggrerate them)
        Reads = sorted(Reads,key=itemgetter(1) )
        No_of_maximal_reads = 0
        No_of_occurences_of_maximal_reads = 0
        #print("Counting Repeats")
        CurrentString = Reads[0][1]
        Neighbhors = [ (Reads[0][0], Reads[0][2]) ]
        Repeat = 1
        Continue = False
        Example = ["none"]
        Positions = [ Reads[0][3]]
        for read in Reads[1:]:
            if read[1] == CurrentString:
                Repeat += 1
                Neighbhors += [ (read[0], read[2]) ]
                Positions += [ read[3] ]
            else:
                """
                   Count only when both right and left neigbhors are not the same

                """
                
                if Repeat > 1:
#                     print("Repeated", CurrentString, Positions[:100])
                    Repeat_Positions += Positions #Adding Repeat Positions

                    Continue = True
                    Example = [ CurrentString]
                    Is_Maximal = False
                    Neighbhors = list( set(Neighbhors) )
                    for i in range(1,len(Neighbhors)):
                        for j in range(i):
                            if( Neighbhors[i][0] != Neighbhors[j][0] and Neighbhors[i][1] != Neighbhors[j][1] ): #Implies that the given read is maximal
                                Is_Maximal = True
                                break
                       
                        else:
                            continue
                        break
                    if Is_Maximal:
                        No_of_maximal_reads += 1
                        No_of_occurences_of_maximal_reads += Repeat
#                 else:
#                     print("didnt repeat", CurrentString)           
                Repeat = 1        
                CurrentString = read[1]
                Neighbhors = [ (read[0], read[2]) ]
                Positions = [ read[3] ]
        
        """
        Last step after exiting the loop
        """
        if Repeat > 1:
#                     print("Repeated", CurrentString, Positions[:100])
            Repeat_Positions += Positions #Adding Repeat Positions

            Continue = True
            Example = [ CurrentString]
            Is_Maximal = False
            Neighbhors = list( set(Neighbhors) )
            for i in range(1,len(Neighbhors)):
                for j in range(i):
                    if( Neighbhors[i][0] != Neighbhors[j][0] and Neighbhors[i][1] != Neighbhors[j][1] ): #Implies that the given read is maximal
                        Is_Maximal = True
                        break
               
                else:
                    continue
                break
            if Is_Maximal:
                No_of_maximal_reads += 1
                No_of_occurences_of_maximal_reads += Repeat
        
        """
        Last step done
        """
        Repeat_Positions = list(set(Repeat_Positions))
        self.RepeatPositions = list(set(Repeat_Positions)) #Updating Repeat Positions
        return( [ length, No_of_maximal_reads, No_of_occurences_of_maximal_reads, Continue,Example ])

    def getUncertainty(self):
        #Stores final data
        Summary = []
        length = 1
        Start_length = 0
        self.DNA_current = self.DNAList[0]

        self.RepeatPositions = range(self.SideLengths, len(self.DNA_current) - Start_length - self.SideLengths )

        while True:
            length += self.Gap
            Answer = self.RepeatsofLengthL(length)  
            #print("Answer", Answer)
            Summary += [ Answer ]
            if Answer[-4] < 1:
                break
        CommonFunctions.WriteArrayinFile(Summary, "Uncertainity_Summary_"+self.Filename[:-6]+".csv")
   
    def RepeatsofLengthL(self, length = 100):
        self.ReadLength_Considered = length
        Repeat_Positions = []
        #print("DNA Length", len(self.DNA_current))
        Reads = []
        #print("Read Length", length)
        for position in self.RepeatPositions:
         #   if position % 1000000 == 0:
         #       print("In position", position, "DNA left", len(self.DNA_current) - position )           
            Reads +=[   
                        [ 
                         self.DNA_current[position - self.SideLengths:                             position] , #Left Neighbhour
                         self.DNA_current[position                   :position + self.ReadLength_Considered] ,
                         self.DNA_current[position + self.ReadLength_Considered : position + self.ReadLength_Considered + self.SideLengths], #Right Neigbhour
                         position
                        ]
                    ]
        #print("Sorting Read Array")
        # Sort w.r.t to the reads. (aggrerate them)
        Reads = sorted(Reads,key=itemgetter(1) )
        UpperboundUncertainty = []
        UncertaintyGap = []
        
        Is_less_than_critical_length = False
        Reason = "No reason"
        Position_of_repeat_less_than_2 = []
        
        #print("Counting Repeats")
        CurrentString = Reads[0][1]
        Repeat = 0
        LeftNeighbhors = [Reads[0][0]]
        RightNeighbors = [Reads[0][2]]
        RepeatPositions = [Reads[0][3]]
        Repeat = 1

        for read in Reads[1:]:
            if read[1] == CurrentString:
                Repeat += 1
                LeftNeighbhors  +=   read[0]
                RightNeighbors  +=   read[2]
                RepeatPositions += [ read[3] ]
            else:
                if Repeat > 1:
                    Repeat_Positions += RepeatPositions #Adding Repeat Positions

                """
                    If the read repeats more than one time and if the right neighbours are unique, 
                    then the node represented by this read will *not* get condensed and this node will add to the uncertainty
                """
                if Repeat > 1 and len( set(RightNeighbors) ) != 1:
                    
                    #Checking for l_critical
                    if Repeat > 2:
                        # If repeat >=3, then the given read length is definitely less than L_critical.
                        Is_less_than_critical_length = True
                        Reason = "Triple Repeats"
                    else:
                        # We accumulate all the reads with length = 2 and check if they interleave.
                        Position_of_repeat_less_than_2 += [ RepeatPositions]
                    
                    # We count the number of times each neighbhour is repeats
                    """
                        Example: If the repeat is 
                        AACA G
                        AACA G
                        AACA T
                        AACA T
                        AACA C
                        AACA C
                        AACA C
                        AACA C
                        AACA A
                        AACA A
                        AACA A
                        
                        Then the node [AACA] has 2 outgoing edges to ACA G, 
                        2 outgoing edges to ACA T, 4 outgoing edges to ACA C,
                        3 outgoing edges to ACA A.
                        
                        Note, if AACA is always present as G(AACA), then the node GAAC
                        will have all its outgoing edges to AACA and that wont be counted here because
                        unique right neigbhour = 1
                        
                    """
                    Count_stats = Counter(RightNeighbors).values()
                    
                    Uncertainty = self.factlog(sum(Count_stats))
                    for i in Count_stats:
                        Uncertainty -= self.factlog(i)
                    Gap = math.log(sum(Count_stats)/min(Count_stats),2)

                    UpperboundUncertainty += [ Uncertainty ]
                    UncertaintyGap += [ Gap ]
                """
                    Re-initialization.
                """
                
                LeftNeighbhors  =   read[0]
                RightNeighbors  =   read[2]
                RepeatPositions = [ read[3] ]
                Repeat = 1

                CurrentString = read[1]
        ####################################################################################
        #Repeat for last read
        if Repeat > 1:
            Repeat_Positions += RepeatPositions
        if Repeat > 1 and len( set(RightNeighbors) ) != 1:
            
            #Checking for l_critical
            if Repeat > 2:
                # If repeat >=3, then the given read length is definitely less than L_critical.
                Is_less_than_critical_length = True
                Reason = "Triple Repeats"
            else:
                # We accumulate all the reads with length = 2 and check if they interleave.
                Position_of_repeat_less_than_2 += [ RepeatPositions]

            Count_stats = Counter(RightNeighbors).values()
            
            Uncertainty = self.factlog(sum(Count_stats))
            for i in Count_stats:
                Uncertainty -= self.factlog(i)
            Gap = math.log(sum(Count_stats)/min(Count_stats),2)

            UpperboundUncertainty += [ Uncertainty ]
            UncertaintyGap += [ Gap ]        
        ######################################################################################
        
        if sorted(Position_of_repeat_less_than_2, key = itemgetter(0)) != sorted(Position_of_repeat_less_than_2, key = itemgetter(1)):
           # print( Position_of_repeat_less_than_2, sorted(Position_of_repeat_less_than_2))
            Reason = "Interleaved Repeats"
            Is_less_than_critical_length = True
            
        Summary = [ self.ReadLength_Considered, sum(UpperboundUncertainty), sum(UpperboundUncertainty) - sum(UncertaintyGap) ,Is_less_than_critical_length, str(datetime.datetime.now()) ]
        print( "ReadLength :", self.ReadLength_Considered, "Upperbound", sum(UpperboundUncertainty), "Lower Bound", sum(UpperboundUncertainty) - sum(UncertaintyGap))
        if False:
            print("Length of the DNA is", len(self.DNA_current))
            print("Number of reads repeating of length", self.ReadLength_Considered," is", len(UpperboundUncertainty))
            print("Time", datetime.datetime.now())
        #print("Uncertainity", sum(UpperboundUncertainty), "Is less than critical length", Is_less_than_critical_length, "reason", Reason)
        
        Repeat_Positions = list(set(Repeat_Positions))
        self.RepeatPositions = list(set(Repeat_Positions)) #Updating Repeat Positions
        
        return(Summary)


filename = ["RhodobacterSphaeroides.fasta", "Buchnera_aphidicola.fasta", "StaphylococcusAureus.fasta", "Lactobacillus acidophilus.fasta" ]
Gene = Genome(filename[3], 1)
Gene.getUncertainty()
#Gene.getReadLengthGraph()


