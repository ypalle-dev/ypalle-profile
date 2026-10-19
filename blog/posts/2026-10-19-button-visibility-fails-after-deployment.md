---
title: Why a button visibility formula fails after deployment
date: 2026-10-19
description: A Power Fx visibility rule can be correct and still disappear in the next environment, when the modern command and its library are not in the app solution.
tags: Dynamics 365, Power Apps, ALM
slug: button-visibility-fails-after-deployment
---

I chased a custom button whose Power Fx visibility formula worked in the environment where I built it and did nothing after the solutions were deployed. The formula was fine. The button had been created in the wrong place, so the command and the library that holds the formula did not travel together.

Create the button from the model-driven app. Do not create it from the Commands list on the table.

## Where to create the button

Power Fx actions and the visibility option **Show on condition from formula** are available when you open the command bar from the app designer. They are not available when you edit a command from the Commands list under a table in a solution. That list can still create a command record. It cannot author the formula the button depends on.

1. Open the solution that contains the model-driven app, select the app, and choose **Edit**.
2. In **Pages**, select **... → Edit command bar** next to the table.
3. Choose the location: **Main grid**, **Main form**, **Subgrid view**, or **Associated view**. Then choose **New → Command**.
4. **Save and publish**.

If the table was added to the app only as a URL, **Edit command bar** is missing. Add it with **Add page → Dataverse table** and turn off **Show in navigation**. It stays out of the menu, and the command bar becomes editable.

## If the button runs JavaScript

Keep the JavaScript web resource in the solution that owns the table. The command still belongs with the app.

- Create and publish the web resource in the data solution.
- Add the command from the app, as above. Set the action to **Run JavaScript** and select that web resource as the library.
- After you save, open **Web resources** in the app solution. If the library was added there automatically, use **Remove from this solution**. Do not delete the web resource. It should exist only in the data solution.

## A modern command is two components

What you see under a table's **Commands** list is the command, stored as an app action. It holds the label, the command bar location, and the action. A Power Fx visibility formula is not stored on that record. The command holds a reference to the formula.

The formula lives in the app's command component library. In a solution this shows up as a component library, often with **DefaultCommandLibrary** in the name. **OnSelect** Power Fx lives there too.

The command and the library have to be deployed together. Both belong in the solution that contains the app. If the library is in the app solution and the commands stay in the data solution, two things break.

**The solutions depend on each other.** The app solution already depends on tables in the data solution. Commands in the data solution then depend on a library in the app solution. Imports and upgrades fail on that circle.

**The wrong layer wins.** In a managed environment the top layer for a component is the one that runs. An older copy of the app or the commands, brought in by the data solution, overrides the newer copy in the app solution. That is why a visibility formula can be correct in the authoring environment and absent after deployment.

## What keeps the failure coming back

The same split causes three repeat problems.

- **The target environment shows the old button.** The authoring environment has one unmanaged layer, so the formula looks done. The target has managed layers. Whichever solution was installed later sits on top. If that layer is an older copy of the app or the commands, it hides the formula you just published.
- **The command is tied to the app you edited.** A modern command, and the component library created with it, cannot be added to a different app. You can copy the command and paste it into another app or another command bar location. Power Fx commands also cannot be converted to table scope or global scope, so they will not suddenly appear on the same table in every app.
- **Taking a component back out of a managed environment is expensive.** A component that landed in the wrong managed solution is not a normal delete. You need a holding solution and an upgrade. That is a poor price for a button.

## Split the solutions by what they own

Keep each kind of component in one solution, and install them in this order.

- **Data:** tables, columns, forms, views, choices, and JavaScript web resources
- **Automation:** cloud flows and processes
- **App:** the model-driven app, canvas apps, custom pages, the site map, commands, and the command library
- **Security:** security roles

Open the app from inside the app solution before you add a command, a page, or anything else on the app. New components are added to the solution you opened. Deployment order is data, then automation, then the app, then security.

## The two pages worth keeping open

[Customize the command bar](https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/use-command-designer) is the authoring path from the app designer.

[Command bar customization limitations](https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/command-designer-limitations) is the page that says Power Fx visibility is only authored from the app designer, and that a command library created in one app cannot be added to another.
