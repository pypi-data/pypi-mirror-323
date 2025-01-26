---
description: Soooo much questions…
---
# FAQ

## How is it different than Nagios?

In a few words, Argos do less things than Nagios, but it makes it more simple.

Nagios can do a lot more than Argos, as it can monitor the load of a server, its disk occupation and so much more.
You can extend the possibilities of Nagios with your own plugins, allowing to monitor almost everything.  
Argos can only monitor web sites, in various ways (check the HTTP status, check the certificate validity time…).

On the other hand, configuration and deployment of Argos are very much simpler than Nagios’.

## How is it different than statping-ng or Uptime Kuma?

In one word: scalability.

While [statping-ng](https://statping-ng.github.io/) and [Uptime Kumap](https://uptime.kuma.pet/) have a similar goal than Argos, you can’t monitor thousands of web sites with them efficiently as their dashboard wants to present you the results of all of your web sites at once… and with the history of the results.

We gave those solutions a try, but fetching thousand of results from the dashboard made the backend overloads.

## Who created Argos?

### Framasoft

Framasoft is a non-profit association founded in 2004, financed by [donations](https://support.framasoft.org/), which is limited to a dozen employees and about thirty volunteers (a group of friends!).
You can find more informations on <https://framasoft.org/>.

We needed a very efficient web sites monitoring tool for one of our project, but didn’t had time to develop it, so we hired [Alexis Métaireau](#alexis-metaireau) for that.

### Alexis Métaireau

Alexis is a long-time free software developer, who has worked for Mozilla, created [Pelican](http://getpelican.com/), a static site generator, [I Hate Money](http://ihatemoney.org/), a website for managing group expenses and many more other projects.

See <https://blog.notmyidea.org/> for more informations about him.
