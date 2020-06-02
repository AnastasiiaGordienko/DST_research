# DST_research
This is repository for everything related to our daylight saving time (DST) effect estimation project.

All errors and imperfections are my property :)

Data is not uploaded due to privacy reasons.

I am using a reproducible research template by our professor: http://hmgaudecker.github.io/econ-project-templates/. 

# What is happening here

This is our research project on effect estimation of DST policy on electricity consumption.

In past this is my bachelor thesis (BSc in Economics, NRU HSE - Perm, Russia), in future this is my master thesis (MSc in Economics, Uni Bonn, Germany) and our common publication. 

In my bachelor thesis, I investigated the effect of DST policy cancellation in 6 selected Russian regions on electricity consumption. I found the significant effect of DST compared to year-round winter time meaning some electricity savings imposed by DST. Those savings are negligible for regional economies, though.  

Now we intend to deepen our research using a wider data period, more accurate calculations and a larger coverage of Russian territories under investigation. For this reason, we have already got data on hourly electricity consumption for 75 regions of Russia for time period from August 2010 to December 2019, as well as weather characteristics data in 3-hours dynamics for the same regions and time.

# What is done up to now
* Data cleaning (electricity consumption and weather data cleaned and merged)
* Change of UTCs in data for all regions (time variables in modified data files are shown in local time - in Russia currently there are 11 UTCs)
* Some DST-related graphs and graphs to show change in UTCs are created
* Overview of what happened in Russia with time settings and in which regions

# Daylight Saving Time (DST) Introduction

The Daylight Saving Time (DST) policy (also known as Summer Time policy) is the practice of seasonal time changes: clocks are adjusted forward usually one hour in the spring and are set back in the autumn. One of the main reasons behind applying this policy is that to save electricity. It is obtained by utilizing the natural sunlight instead of artificial light (electricity). The idea behind DST is that people’s activities shift forward with the clock transitions, so that the sun appears to set one hour later during the summer and the extra hour of natural light decreases electricity load.  

Despite DST adaptation in most developed countries, there is still no clear view on its impacts on electricity demand. We are aiming at contribution to this issue focusing on the Russian case.

# DST History in Russia

Without any exaggeration, the history of DST policy in Russia is unique. Officially, DST was introduced in 1981: seasonal time changes by one hour were made in March-April and September-October. Several decades later, in 2011, the cancellation of DST practice in Russia was announced. The country turned on the «permanent» Summer Time and all regions added one hour. Later, in 2014, the transition to «permanent» Winter Time was declared, which is still present in most Russian regions. The implementation of the DST policy is hotly debated time and again: its potential impact is questioned. People mostly complain about health issues caused by time transmittings and inadequate daylight regime with too late sunrise or too early sunset. It has led to several cases when some regions locally decided to change their time zone. Currently, a draft law on DST return in Russia is under consideration.  

Besides intriguing DST efficiency issue, the Russian case is attractive due to several natural experiments available. They allow to compare DST practice with two alternative time policies: Summer Time (ST) and Winter Time (WT).

We have data on hourly regional electricity consumption from August 2010 to December 2019 and weather conditions data (air temperature, humidity, wind speed and dummies on twilight and sunrise). The time period includes official DST cancellation and turn to ST in March 2011 and turn to WT in October 2014.


