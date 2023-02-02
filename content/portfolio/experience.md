---
# An instance of the Experience widget.
# Documentation: https://wowchemy.com/docs/page-builder/
widget: experience

# This file represents a page section.
headless: true

# Order that this section appears on the page.
weight: 40

title: Experience
subtitle:

# Date format for experience
#   Refer to https://wowchemy.com/docs/customization/#date-format
date_format: Jan 2006

# Experiences.
#   Add/remove as many `experience` items below as you like.
#   Required fields are `title`, `company`, and `date_start`.
#   Leave `date_end` empty if it's your current employer.
#   Begin multi-line descriptions with YAML's `|2-` multi-line prefix.
experience:
  - title: Software Perception Intern
    company: Aurora Innovation
    company_url: 'https://aurora.tech'
    company_logo: aurora
    location: California
    date_start: '2022-06-21'
    date_end: '2022-09-09'
    description: |2-
        - Implemented and integrated range-view based object detection for the lidar sensors with camera sensors for the self-driving autonomy stack to improve long-range object detection
        - Increased the long-range detection capabilities allowing the vehicle to detect objects >200m on all sides
        - Skills: 3D Object Detection, Lidar Processing, Depth Processing, PyTorch, Python, C++

  - title: Technical Associate (Research Intern formerly)
    company: Robert Bosch Center for Cyber-Physical Systems, IISc
    company_url: 'https://cps.iisc.ac.in/'
    company_logo: rbccps
    location: Bangalore, India
    date_start: '2019-11-21'
    date_end: '2021-01-31'
    description: |2-
        - Worked on two research projects: Visual Odometry for Navigation, and Teleoperation of a Humanoid Robot
        - Visual Odometry: Developed a stereo odometry parking using learned features, which was used for emergency parking of the autonomous vehicle developed in the lab. Published a survey on the same.
        - Teleoperation: Competed in the ANA Xprize Avatar Challenge as a university-industry team. Developed human arm teleoperation libraries using optical trackers and inverse kinematics.
        - Skills: ROS, Pytorch, 3D Vision, SLAM, PCL, Inverse Kinematics
  - title: Part-time Research Assistant
    company: Indian Institute of Management, Bangalore
    company_url: 'https://www.iimb.ac.in/'
    company_logo: iimb
    location: Bangalore, India
    date_start: '2020-08-21'
    date_end: '2021-03-31'
    description: |2-
        - Implemented a pipeline to extract textual and numeric data from public financial filings of firms for an academic project which seeks to develop a new measure of Disclosure Quality
        - Responsibilities included libraries to perform web scraping, data cleaning, text and numerical extraction, mathematical modeling, and visualization
  - title: Research Intern
    company: LightMetrics Pvt. Ltd.
    company_url: 'https://www.lightmetrics.co/'
    company_logo: lightmetrics
    location: Bangalore, India
    date_start: '2019-05-21'
    date_end: '2019-08-08'
    description: |2-
        - As a returning intern for the summer of 2019, worked in the video telematics team to compress neural networks
        -  Compared the performance of various techniques for compressing neural networks for real-time performance on edge compute. Implemented filter based and activation based pruning techniques to achieve 6x reduction in size and 6x speedup for object detection. 
design:
  columns: '2'
---
