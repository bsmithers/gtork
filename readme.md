# GTORK: Garmin to RunKeeper

A simple [Flask](http://flask.pocoo.org/) application, allowing users to upload their [Garmin Connect](https://connect.garmin.com) activities to [Runkeeper](https://runkeeper.com/)

## Motivation

My wife's been using Runkeeper for a long time and likes the interface, incluing the Runkeeper Pro graphs, but she also likes to use her Garmin Watch to actually record the activities (as it is more accurate & convenient).

While Runkeeper has a decent (although incomplete) API, Garmin requires a $5,000 payment to even try the API(really!). We default to scraping the website. As I have no desire to store Garmin login credentials, they are kept in the user's browser and sent with each request - non ideal, but allows this to generalize beyond one user. 

## Status

An initial implementation is complete

### TODOs & Known Issues

- Garmin login should be checked when the details are provided
- General UI improvements, especially the header
- Users may want to override the GPS distance calculations and use the total distance instead (e.g. partial GPS data)
- Optionally enable the Runkeeper pause-detection
- Runkeeper does not use our heart rate when no GPS data is supplied. This seems like it might be a known issue. Consider providing avg heart rate in this case
- Support for more activity types, including stationary walking & cycling. 

