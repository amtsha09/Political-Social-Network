
# Collecting a political social network of recent election candidates

### We have taken twitter handle for four of the following US presidential candidates:
- DrJillStein
- GovGaryJohnson
- HillaryClinton
- realDonaldTrump

These names have been written into "candidates.txt"

### We have used "Twitter API" to construct a social network of these accounts and "networkx" library to plot these links.

#### Follow these steps and add your credentials
1. Create an account on [twitter.com](http://twitter.com).
2. Generate authentication tokens by following the instructions [here](https://dev.twitter.com/docs/auth/tokens-devtwittercom).
3. Add your tokens to the key/token variables below. (API Key == Consumer Key)


### Instructions to copy the environment to run the program without any dependency issue.

I have made a conda environment for this challenge and have saved that in "politicalsocialnetwork.yml"

For performing and running all these files its a better choice to activate this environment in which these have been written and executed.

Follow these steps to activate this environment:
	"conda env create -f politicalsocialnetwork.yml"
	"source activate politicalsocialnetwork"

Now you are in politicalsocialnetwork environment and can easily run all the files in this repository