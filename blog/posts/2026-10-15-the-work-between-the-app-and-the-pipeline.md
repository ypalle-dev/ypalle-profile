---
title: The work between the app and the pipeline
date: 2026-10-15
description: Field notes on shipping Dynamics 365 when Dataverse is the product and a system other platforms have to feed.
tags: Dynamics 365, Dataverse, Delivery
slug: the-work-between-the-app-and-the-pipeline
---

A model-driven app can look done while the data under it is still a guess. A pipeline can land every row in Dataverse and still be the wrong system, because security roles, status reasons, and the way an operations team works were never part of the design.

That gap is the work I want to write about.

I am a senior forward deployed engineer on Dynamics 365 and the Power Platform. I sit with the delivery: requirements, the data model, the UI, the integrations, and the path from development through production. Before this I spent years on Spark, Databricks, and Airflow. Those years still show up. The app is not separate from the load that fills it, or from the extract that leaves it.

## What these notes are

One problem at a time. The situation, the option I turned down, the part you can reuse, and what failed or what I would change.

The subjects will stay in a lane I actually work in:

- Dataverse modeling for operational apps, including security that matches the way the app is used
- Power Automate, custom connectors, and PCF where the platform form is not enough
- Solution ALM across development, QA, UAT, and production
- Inbound and outbound integrations beside the app, including the habits that matter when a file or an API is run again tomorrow

I am writing for people who already build on this stack. When a step is easy to skip, I will still write it down. I am not going to restate the product documentation.

## What I will leave out

Names, data, and anything that belongs to a client engagement. If a story needs a concrete shape, I will reduce it to a pattern and say that I did. The decision is the point. The account is not.

## A bar for the next note

A load into Dataverse that can be run twice has to decide identity before it decides columns.

```text
natural key:  source system + source id
write:        upsert on that key
failure:      log the row, alert, keep the batch moving
success:      the same key updates the same row
```

That block is not a design from a project. It is the size and the honesty I want from the notes that follow. If I cannot show the option I rejected and the failure path, the note is not ready.

I would rather publish one of those a month than a stream of recaps.
