---
title: JetBot Roomba Prototype
summary: Program an autonomous mobile robot with SLAM to perform area coverage.
tags:
  - Robotics
  - Coursework
# date: '2021-04-27T00:00:00Z'
weight: 4
location: CSE276A, UCSD
# authors: [Shrutheesh]
show_date: False
# Optional external URL for project (replaces project detail page).
external_link: ''

image:
  caption: NVidia Jetbot
  focal_point: Smart

# links:
#   - icon: twitter
#     icon_pack: fab
#     name: Follow
#     url: https://twitter.com/georgecushen
# url_code: ''
# url_pdf: ''
# url_slides: ''
# url_video: ''

# Slides (optional).
#   Associate this project with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
# slides: example
---

Developed a autonomous mobile robot (NVidia JetBot), equipped with perception, planning and control to be able to navigate in a given space, similar to a roomba, written from scratch, as part of CSE276A: Introduction to Robotics.
Features: 
- Perception performed with the help of AprilTags.
- EKF used for SLAM.
- A spiral-like pattern used for the lawn mover algorithms
- Written in C++, Python and ROS