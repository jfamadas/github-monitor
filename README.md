# GitHub-monitor
Monitoring WatchEvent, PullRequestEvent and IssuesEvent from the GitHub API

## Context Diagram
![Diagram](utils/diagram.jpg)


## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/jfamadas/github-monitor.git
   ```
2. Install requirements
   ```sh
   pip install -r requirements.txt 
   ```


## Usage

1. Start data extractor
   ```sh
   python extract.py -t [ENTER YOUR GITHUB TOKEN HERE]
   ```
2. Start the API in a new terminal (it will run at 127.0.0.1:5000)
   ```sh
   python api.py
   ```
   
With the API running, you can send GET requests to the following endpoints:

- /events-by-type/[offset_minutes]
  - Return the total number of events grouped by the event type for a given offset (in minutes)
  - *IMPORTANT: GitHub Events API delay the public events feed by five minutes. [More info.](https://docs.github.com/en/rest/activity/events#list-public-events)*
      - e.g. "/events-by-type/30" will return events from 30 minutes ago to 5 minutes ago.
        
    
- /time-between-requests/[github_user]/[repository]
  - Calculate the average time between pull requests for a given repository
  
### Examples

Find some examples in [/tests](https://github.com/jfamadas/github-monitor/tree/main/tests)
