---
title: A flow that works in DEV and talks to the wrong environment after deployment
date: 2026-10-21
description: The flow can succeed and still read or write the environment where you built it. The connection reference and the environment variable are what move, not the connection you clicked while editing.
tags: Power Automate, Dataverse, ALM
slug: flow-talks-to-the-wrong-environment
---

I imported a cloud flow, turned it on, and watched a successful run. The row it created was not in that environment. It was in the environment where I had built the flow. The steps were fine. The flow was still holding the first environment.

A connection does not travel in a solution. A connection reference does. If you never look at the reference after import, the flow keeps using whatever connection was selected when the reference was created.

## What the solution actually contains

While you edit a flow, you pick a connection. That connection belongs to a user, in one environment. A solution cannot carry it.

When the flow is in a solution, each connector action uses a **connection reference**. The reference is the solution component. During import, the target environment has to bind that reference to a connection that already exists there. Until you do that, the flow is not really deployed. It is a copy of the steps, still aimed at the connection from the environment you exported.

Use the **Microsoft Dataverse** connector that runs in the current environment. A connection for that connector does not store an environment URL. The flow reads and writes the environment it is running in.

The older Dataverse connector is different. Its connection is pinned to the environment you chose in the connection dialog. Map that reference to a connection someone created while looking at the original environment, and every run in the target still talks to the original environment. The run is green. The data is in the wrong place.

## If the flow calls a URL

The current-environment connector is not always an option. An HTTP action, a custom connector, or a Web API call often has the environment address typed into the action. That text is part of the flow definition, so export and import copy it as it stands.

Put the address in an environment variable. The definition of the variable travels in the solution. The current value should be set in each environment, and it should not be the value from the environment you exported.

Before you export, remove the current value from the solution. Leave the variable definition. On import, set the value to that environment's address. If the exported value stays in the solution, the import writes the original address into the target, and the flow calls home.

## Where the pieces belong

Put the flow and its connection references in the automation solution. Put environment variable definitions in the same solution as the component that reads them. Install the data solution first, so tables exist before a flow tries to use them, then the automation solution.

After import, in the target environment:

1. Open the imported flow and read the connection references on it. Do not check this from the environment you built in.
2. For each reference, use a connection created in this environment. For Dataverse, use the current-environment connector.
3. Set each environment variable to this environment. Confirm the value is not the address you exported.
4. Turn the flow on only after those two are done.
5. Trigger one run. Open the row it created or updated, in this environment. A successful run is not the check. The row's environment is the check.

## The two pages worth keeping open

[Connection references](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference) is how a solution carries the connector without carrying the connection.

[Environment variables](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables) is where an address belongs when an action cannot use the current environment.
