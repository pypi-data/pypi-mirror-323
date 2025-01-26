# UserAgentReplica

## Description

UserAgentReplica is a Python package that provides functionality for simulating different user agents and xms user agents. This can be useful for web scraping, testing, or any other situation where you need to mimic various types of web clients.

## Features

- Safe to use in various platforms
- Simulate a variety of user agents [ Chrome, Safari & Firefox ]
- Simulate a random variety of xm user agents.
- Easy integration with existing projects
- Lightweight and simple to use

## Installation

You can install UserAgentReplica using pip:

```bash
pip install UserAgentReplica
```

## Example Uses

Here is an example of how to use the `UserAgentReplica` library to generate a random user agent:

```python
from UserAgentReplica import UserAgent

# Create an instance of UserAgent
agent = UserAgent()

# Get a random user agent
random_user_agent = agent.random_browser()
print(random_user_agent)

# Get a chrome user agent
chrome_user_agent = agent.chrome()
print(chrome_user_agent)

# Get a firefox user agent
firefox_user_agent = agent.firefox()
print(firefox_user_agent)

# Get a safari user agent
safari_user_agent = agent.safari()
print(safari_user_agent)
```

Here is an example of how to use the `UserAgentReplica` library to generate a random xms user agent:

```python
from UserAgentReplica import XMsUserAgent

# Create an instance of UserAgent
agent = XMsUserAgent()

# Get a random xms user agent
random_user_agent = agent.random()
print(random_user_agent)
```