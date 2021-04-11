# Kellogg's Football 2021 Code Creator

Have you ever wondered what valid codes for the Kelloggs 2021 Football raffle in Germany look like? **You're in luck!**
With this funky little tool, you will get to see thousands of examples a day without developing diabete type 2 from excessive cereal consumption.  

Kellogg's was friendly enough to provide the public with a service that tells you if a given list of codes qualifies you to enter their 2021 football raffle.
All we had to do is build a tool that annoys this service until we are lucky enough to find a working code.

We are using an advanced statistical approach to generate the candidates for valid codes called "guessing".
Considering that there are only 208827064576 possible codes to go through and we are heavily bottlenecked by their api running on what feels like a 2007 Dell notebook with an unlicensed windows server installation, this should be a breeze.

**Obvious disclaimer**: Don't use this to fraudulently enter the raffle. For one, it is legally and morally questionable. More importantly though, doing so will reduce our chances of winning the 43" Sony flatscreen. Please show some consideration.


## Setup

As an arbitrary step to avoid legal action, we have not provided you with the url to the home page of the raffle in question.
1. Rename ```.env_template``` to ```.env```
2. Use your favorite search engine to find a fitting raffle (any Kellogg's Football raffle running from 08.03.21 to 07.09.21 will do) and set the ``URL`` variable (leaving out the part after the tld).


### Deployment

This thing has a docker setup because of course it does.

For the deployment on your Linux machine, you will need both [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

To build the docker images, run 

```
docker-compose build
```

in the root directory.

After completing the setup, start our little magic tool with

```
docker-compose up -d
```

and watch in awe as ```./output/codes.txt``` fills with strings that look earily similar to raffle codes that work for Kellogg's Football raffles running from 08.03.21 to 07.09.21.

Stop the tool with

```
docker-compose down
```


### Development

If you want to tweak this marvelous piece of software to your liking, just follow these easy steps:

1. Get [Python 3.7](https://www.python.org/downloads/)
2. Run ````set -o allexport; source conf-file; set +o allexport````

You can now run the the tool with
```
python3.7 main.py
```

### Running the tests

We are brute forcing our way through a raffle for childrens serial. Do you really think this is a context where the term "unit test" has any meaning?


## Built With

* [Love](https://tinder.com/)
* [Care](https://hinge.co/) 
* [Passion](https://wiki.archlinux.org/)

## Contributing

Code wise we should be fine, but if you have any ideas for a cover
story that explains why we are in the "possession" of tens of thousands of Kellogg's cereal boxes, please help us out! 

## Trivia

* Going off of current rates, we can assume that there are 90 million valid codes.
* This allows us to estimate an utterly useless upper limit of Kellogg's daily cereal box sales in Germany of about 5 million.
* To get all codes the legit way, one would have to consume about 33750000 Kilograms of Kellogg's cereal.
* This is about 148837500000 calories (kcal), enough to feed the population of the Czech Republic for an entire week.

## Authors

* **Adrian Steffan** - [adriansteffan](https://github.com/adriansteffan)
* **Till Müller** - [tillmueller](https://github.com/tillmueller)
* **Vera Lily Eagle**
* **P. Lisa Donsume**


## Acknowledgments

* Hat tip to the lowest bidder contracting company that designed this raffle for Kelloggs's.

