# SpliceAILookup

Web frontend to inspect SpliceAI raw scores. Heavily inspired by https://spliceailookup.broadinstitute.org/

This was developed to address a couple of use cases

* Being able to query +/- NN distance from variant site (your tool already does that)

* Being able to easy view the splice site confidence REF and VAR scores . We’ve noticed that sometimes SpliceAI assigns a low confidence score to the REF splice site e.g. 0.13 and a variant might reduce the confidence to 0.01

* - Under this circumstance, the delta score is 0.12 (while this is under then 0.2 cut off that the authors recommend, the reduction of confidence from 0.13 to 0.01 suggests that the splice site may be substantially diminished)

* Being able to see REF/VAR scores across multiple distances and quickly identify those where there may have been a noticeable change


## Set up
* Clone the repository
* Modify docker.compose files to repoint the API's volume to where the hg19 fasta file is stored

### Invoking SpliceAILookup
```docker-compose -f docker.compose.yml up -d```

### Shutting down SpliceAILookup
```docker-compose down```


## Todo
* Updated to properly handle GRCh37 and GRCh38 builds
* Better error handling / messages
* Integrate with genome browser so visually display the impact of a variant
