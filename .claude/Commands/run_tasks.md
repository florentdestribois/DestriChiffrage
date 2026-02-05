---
description: Run a task
---

For the given $ARGUMENTS you need to get the information about the tasks you need to do :

- If it's a file path, get the path to get the instructions and the feature we want to create
- If it's an issues number or URL, fetch the issues to get the information (with `gh cli`)

---
description: Explore codebase, create implementation plan, code, and test following EPCT workflow
---

# Explore, Plan, Code, Test Workflow

At the end of this message, I will ask you to do something.
Please follow the "Explore, Plan, Code, Test" workflow when you start.

## Explore

First, use parallel subagents to find and read all files that may be useful for implementing the ticket, either as examples or as edit targets. The subagents should return relevant file paths, and any other info that may be useful.
Prend connaissance des fichiers du dossier .claude/historique-de-conversation

## Plan

Next, think hard and write up a detailed implementation plan. Don't forget to include tests, lookbook components, and documentation. Use your judgement as to what is necessary, given the standards of this repo.

If there are things you are not sure about, use parallel subagents to do some web research. They should only return useful information, no noise.

If there are things you still do not understand or questions you have for the user, pause here to ask them before continuing.

## Code

When you have a thorough implementation plan, you are ready to start writing code. Follow the style of the existing codebase (e.g. we prefer clearly named variables and methods to extensive comments). Make sure to run our autoformatting script when you're done, and fix linter warnings that seem reasonable to you.

## Test

Use parallel subagents to run tests, and make sure they all pass.

If your changes touch the UX in a major way, use the browser to make sure that everything works correctly. Make a list of what to test for, and use a subagent for this step.

If your testing shows problems, go back to the planning stage and think ultrahard.

## Write up your work

When you are happy with your work, write up a short report that could be used as the PR description. Include what you set out to do, the choices you made with their brief justification, and any commands you ran in the process that may be useful for future developers to know about.

2. Make the update
   Update the files according to your plan.
   Auto correct yourself with TypeScript. Run TypeScript check and find a way everything is clean and working.

Impératif :

1 - Répond moi toujours en français
2 - Ne créer pas de classe dans la page mais fait toujours référence au fichier globals.css afin de pouvoir modifier le design général de l'application dans ce fichier 
3 - Aucune donnée en dur 
4 - Met à jour le fichier README.md 
5 - Met à jour le numéro de version se trouvant dans admin-dashboard.tsx et employee-dashboard.tsx correspondant à celui indiquer dans le fichier README.md 